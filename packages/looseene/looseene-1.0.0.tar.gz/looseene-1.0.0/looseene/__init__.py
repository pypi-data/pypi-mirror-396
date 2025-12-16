import heapq
import itertools
import json
import math
import mmap
import os
import re
import shutil
import struct
import threading
import time
import uuid
import zlib
from collections import defaultdict, Counter
from typing import Dict, List, Generator, Optional, Set, Tuple, Type

__all__ = [
    'create_index',
    'get_index',
    'add_to_index',
    'delete_document',
    'update_document',
    'search_text',
    'save_index',
    'compact_index',
    'highlight_result',
    'SearchLibError',
    'ValidationError',
]

_REGISTRY: Dict[str, 'IndexEngine'] = {}
_REGISTRY_LOCK = threading.Lock()
POSTING_STRUCT = struct.Struct('<II')
MAGIC_NUMBER = b'IDX4'

_counter = itertools.count()


def gen_id():
    return f'{time.time_ns()}_{next(_counter)}'


class SearchLibError(Exception):
    pass


class ValidationError(SearchLibError):
    pass


class TextProcessor:
    ENDINGS = re.compile(r'(ыми|ых|ого|ому|ые|ый|ая|ой|ь|ы|и|а|е|у|ю|ом|ем|ам|ал|ил|ть|ing|ed|es|ly)$')
    TOKEN_RE_STR = r'\w{3,}'
    TOKEN_RE = re.compile(TOKEN_RE_STR)

    @staticmethod
    def stem(word: str) -> str:
        if len(word) > 4:
            return TextProcessor.ENDINGS.sub('', word)
        return word

    @staticmethod
    def ngrams(word: str, n: int = 3) -> List[str]:
        if len(word) < n:
            return [word]
        return [word[i : i + n] for i in range(len(word) - n + 1)]

    @staticmethod
    def process(text: str, use_ngrams: bool = False) -> List[str]:
        if not text:
            return []
        raw_words = TextProcessor.TOKEN_RE.findall(text.lower())
        tokens = []
        for w in raw_words:
            stemmed = TextProcessor.stem(w)
            tokens.append(stemmed)
            if use_ngrams:
                tokens.extend(TextProcessor.ngrams(w))
        return tokens

    @staticmethod
    def process_with_offsets(text: str) -> List[Tuple[str, int, int]]:
        """
        Возвращает список кортежей (стем, начало, конец).
        Нужен для подсветки, чтобы знать, где находится слово в исходной строке.
        """
        if not text:
            return []
        results = []
        for match in TextProcessor.TOKEN_RE.finditer(text):
            word = match.group().lower()
            stemmed = TextProcessor.stem(word)
            results.append((stemmed, match.start(), match.end()))
        return results


class Highlighter:
    def __init__(self, start_tag: str = '<b>', end_tag: str = '</b>', window_size: int = 150):
        self.start_tag = start_tag
        self.end_tag = end_tag
        self.window_size = window_size

    def highlight(self, text: str, query: str) -> str:
        if not text or not query:
            return text[: self.window_size]
        query_stems = set(TextProcessor.process(query, use_ngrams=False))
        if not query_stems:
            return text[: self.window_size]
        doc_tokens = TextProcessor.process_with_offsets(text)
        matches = []
        for stem, start, end in doc_tokens:
            if stem in query_stems:
                matches.append((start, end))
        if not matches:
            return text[: self.window_size] + '...'
        first_match_start = matches[0][0]
        window_start = max(0, first_match_start - self.window_size // 3)
        window_end = min(len(text), window_start + self.window_size)
        if window_end == len(text):
            window_start = max(0, window_end - self.window_size)
        visible_matches = [m for m in matches if m[0] >= window_start and m[1] <= window_end]
        result_parts = []
        current_idx = window_start
        for start, end in visible_matches:
            result_parts.append(text[current_idx:start])
            result_parts.append(self.start_tag)
            result_parts.append(text[start:end])
            result_parts.append(self.end_tag)
            current_idx = end
        result_parts.append(text[current_idx:window_end])
        snippet = ''.join(result_parts)
        if window_start > 0:
            snippet = '...' + snippet
        if window_end < len(text):
            snippet = snippet + '...'
        return snippet


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def score(self, tf: int, doc_len: int, avg_dl: float, idf: float) -> float:
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / avg_dl))
        return idf * (numerator / denominator)


class DiskSegment:
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        self.vocab: Dict[str, Tuple[int, int]] = {}
        self.doc_index: Dict[int, Tuple[int, int, int]] = {}
        self.files = {}
        try:
            self.files['postings'] = open(os.path.join(dir_path, 'postings.bin'), 'rb')
            self.files['docs'] = open(os.path.join(dir_path, 'docs.bin'), 'rb')
            self.mm_postings = mmap.mmap(self.files['postings'].fileno(), 0, access=mmap.ACCESS_READ)
            self.mm_docs = mmap.mmap(self.files['docs'].fileno(), 0, access=mmap.ACCESS_READ)
        except Exception:
            self.close()
            raise
        self._load_vocab()
        self._load_doc_index()

    def _load_vocab(self):
        vp = os.path.join(self.dir_path, 'vocab.json')
        if os.path.exists(vp):
            with open(vp, 'r', encoding='utf-8') as f:
                self.vocab = json.load(f)

    def _load_doc_index(self):
        dp = os.path.join(self.dir_path, 'doc_idx.json')
        if os.path.exists(dp):
            with open(dp, 'r') as f:
                raw = json.load(f)
                self.doc_index = {int(k): tuple(v) for k, v in raw.items()}

    def get_postings(self, term: str) -> List[Tuple[int, int]]:
        if term not in self.vocab:
            return []
        offset, length = self.vocab[term]
        try:
            compressed_data = self.mm_postings[offset : offset + length]
            raw_bytes = zlib.decompress(compressed_data)
        except Exception:
            return []
        results = []
        last_doc_id = 0
        for delta_id, tf in POSTING_STRUCT.iter_unpack(raw_bytes):
            doc_id = last_doc_id + delta_id
            results.append((doc_id, tf))
            last_doc_id = doc_id
        return results

    def get_document(self, doc_id: int) -> Optional[Dict]:
        if doc_id not in self.doc_index:
            return None
        offset, length, _ = self.doc_index[doc_id]
        compressed_doc = self.mm_docs[offset : offset + length]
        json_bytes = zlib.decompress(compressed_doc)
        return json.loads(json_bytes.decode('utf-8'))

    def get_doc_len(self, doc_id: int) -> int:
        if doc_id in self.doc_index:
            return self.doc_index[doc_id][2]
        return 0

    def close(self):
        if hasattr(self, 'mm_postings') and not self.mm_postings.closed:
            self.mm_postings.close()
        if hasattr(self, 'mm_docs') and not self.mm_docs.closed:
            self.mm_docs.close()
        for f in self.files.values():
            if not f.closed:
                f.close()


class SegmentWriter:
    @staticmethod
    def write(
        base_dir: str,
        seg_id: str,
        inverted_index: Dict[str, List[Tuple[int, int]]],
        docs: Dict[int, Dict],
        doc_lens: Dict[int, int],
    ):
        seg_dir = os.path.join(base_dir, f'seg_{seg_id}')
        os.makedirs(seg_dir, exist_ok=True)
        vocab = {}
        doc_index = {}
        with open(os.path.join(seg_dir, 'postings.bin'), 'wb') as f_post:
            current_offset = 0
            for term in sorted(inverted_index.keys()):
                postings = inverted_index[term]
                postings.sort(key=lambda x: x[0])
                buffer = bytearray()
                last_doc_id = 0
                for doc_id, tf in postings:
                    delta = doc_id - last_doc_id
                    buffer.extend(POSTING_STRUCT.pack(delta, tf))
                    last_doc_id = doc_id
                compressed = zlib.compress(buffer)
                length = len(compressed)
                f_post.write(compressed)
                vocab[term] = (current_offset, length)
                current_offset += length
        with open(os.path.join(seg_dir, 'docs.bin'), 'wb') as f_docs:
            current_offset = 0
            for doc_id, data in docs.items():
                raw_json = json.dumps(data).encode('utf-8')
                compressed = zlib.compress(raw_json)
                length = len(compressed)
                f_docs.write(compressed)
                d_len = doc_lens.get(doc_id, 0)
                doc_index[doc_id] = (current_offset, length, d_len)
                current_offset += length
        with open(os.path.join(seg_dir, 'vocab.json'), 'w', encoding='utf-8') as f:
            json.dump(vocab, f)
        with open(os.path.join(seg_dir, 'doc_idx.json'), 'w') as f:
            json.dump(doc_index, f)
        return seg_dir


class IndexEngine:
    def __init__(self, name: str, schema: Dict[str, Type], path: Optional[str] = None):
        self.name = name
        self.schema = schema
        self.path = path
        self.pk_field = 'id'
        self.mem_docs: Dict[int, Dict] = {}
        self.mem_doc_lens: Dict[int, int] = {}
        self.mem_inverted: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.stats = {'total_docs': 0, 'total_len': 0, 'doc_freqs': Counter()}
        self.deleted_ids: Set[int] = set()
        self.segments: List[DiskSegment] = []
        self._lock = threading.RLock()
        if self.path:
            if not os.path.exists(self.path):
                os.makedirs(self.path, exist_ok=True)
            self._load_segments()
            self._load_stats()

    def close(self):
        """Closes all open file handles for segments."""
        with self._lock:
            for seg in self.segments:
                seg.close()
            self.segments.clear()

    def _load_stats(self):
        sp = os.path.join(self.path, 'stats.json')
        if os.path.exists(sp):
            with open(sp, 'r') as f:
                data = json.load(f)
                self.stats['total_docs'] = data['total_docs']
                self.stats['total_len'] = data['total_len']
                self.stats['doc_freqs'] = Counter(data['doc_freqs'])
                self.deleted_ids = set(data.get('deleted_ids', []))

    def _save_stats(self):
        if not self.path:
            return
        sp = os.path.join(self.path, 'stats.json')
        with open(sp, 'w') as f:
            json.dump(
                {
                    'total_docs': self.stats['total_docs'],
                    'total_len': self.stats['total_len'],
                    'doc_freqs': self.stats['doc_freqs'],
                    'deleted_ids': list(self.deleted_ids),
                },
                f,
            )

    def _load_segments(self):
        if not self.path:
            return
        for name in sorted(os.listdir(self.path)):
            if name.startswith('seg_'):
                full_path = os.path.join(self.path, name)
                if os.path.isdir(full_path):
                    self.segments.append(DiskSegment(full_path))

    def _validate(self, data: Dict) -> int:
        if self.pk_field not in data:
            raise ValidationError('No ID')
        doc_id = data[self.pk_field]
        if not isinstance(doc_id, int):
            raise ValidationError('ID must be int')
        return doc_id

    def add(self, data: Dict):
        doc_id = self._validate(data)
        with self._lock:
            if doc_id in self.deleted_ids:
                self.deleted_ids.remove(doc_id)
            self.mem_docs[doc_id] = data
            doc_len = 0
            seen_terms = set()
            for field, val in data.items():
                if isinstance(val, str):
                    tokens = TextProcessor.process(val, use_ngrams=True)
                    doc_len += len(tokens)
                    for t in tokens:
                        self.mem_inverted[t][doc_id] += 1
                        seen_terms.add(t)
            self.mem_doc_lens[doc_id] = doc_len
            self.stats['total_docs'] += 1
            self.stats['total_len'] += doc_len
            for t in seen_terms:
                self.stats['doc_freqs'][t] += 1

    def delete(self, doc_id: int):
        with self._lock:
            self.deleted_ids.add(doc_id)
            if doc_id in self.mem_docs:
                del self.mem_docs[doc_id]
                if doc_id in self.mem_doc_lens:
                    del self.mem_doc_lens[doc_id]

    def flush(self):
        if not self.path or not self.mem_docs:
            return
        with self._lock:
            inverted_list = {}
            for term, doc_map in self.mem_inverted.items():
                inverted_list[term] = list(doc_map.items())
            # seg_id = f'{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}'
            # seg_id = str(time.monotonic_ns())
            seg_id = gen_id()
            new_seg_path = SegmentWriter.write(self.path, seg_id, inverted_list, self.mem_docs, self.mem_doc_lens)
            self.segments.append(DiskSegment(new_seg_path))
            self.mem_docs.clear()
            self.mem_doc_lens.clear()
            self.mem_inverted.clear()
            self._save_stats()

    def compact(self):
        if not self.path:
            return
        with self._lock:
            self.flush()
            if len(self.segments) <= 1 and not self.deleted_ids:
                return
            active_docs_map: Dict[int, int] = {}
            for idx, seg in enumerate(self.segments):
                for doc_id in seg.doc_index.keys():
                    if doc_id not in self.deleted_ids:
                        active_docs_map[doc_id] = idx
            all_terms = set()
            for seg in self.segments:
                all_terms.update(seg.vocab.keys())
            merged_inverted: Dict[str, List[Tuple[int, int]]] = {}
            for term in all_terms:
                term_postings = {}
                for idx, seg in enumerate(self.segments):
                    raw_postings = seg.get_postings(term)
                    for doc_id, tf in raw_postings:
                        if active_docs_map.get(doc_id) == idx:
                            term_postings[doc_id] = tf
                if term_postings:
                    merged_inverted[term] = list(term_postings.items())
            merged_docs = {}
            merged_doc_lens = {}
            for doc_id, seg_idx in active_docs_map.items():
                seg = self.segments[seg_idx]
                doc = seg.get_document(doc_id)
                if doc:
                    merged_docs[doc_id] = doc
                    merged_doc_lens[doc_id] = seg.get_doc_len(doc_id)

            new_seg_id = f'merged_{int(time.time())}_{uuid.uuid4().hex[:6]}'
            new_path = SegmentWriter.write(self.path, new_seg_id, merged_inverted, merged_docs, merged_doc_lens)

            old_segments = self.segments[:]
            self.segments = [DiskSegment(new_path)]

            for seg in old_segments:
                seg.close()
                try:
                    shutil.rmtree(seg.dir_path)
                except FileNotFoundError:
                    pass

            self.deleted_ids.clear()
            self._save_stats()

    def search(self, query: str) -> Generator[Dict, None, None]:
        tokens = TextProcessor.process(query)
        if not tokens:
            return
        bm25 = BM25()
        avg_dl = self.stats['total_len'] / max(1, self.stats['total_docs'])
        total_docs = self.stats['total_docs']
        scores = defaultdict(float)
        for term in tokens:
            doc_freq = self.stats['doc_freqs'].get(term, 0)
            if doc_freq == 0:
                continue
            idf = math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
            if term in self.mem_inverted:
                for doc_id, tf in self.mem_inverted[term].items():
                    if doc_id in self.deleted_ids:
                        continue
                    doc_len = self.mem_doc_lens.get(doc_id, int(avg_dl))
                    scores[doc_id] += bm25.score(tf, doc_len, avg_dl, idf)
            for seg in self.segments:
                postings = seg.get_postings(term)
                for doc_id, tf in postings:
                    if doc_id in self.deleted_ids:
                        continue
                    doc_len = seg.get_doc_len(doc_id)
                    scores[doc_id] += bm25.score(tf, doc_len, avg_dl, idf)
        top_docs = heapq.nlargest(20, scores.items(), key=lambda x: x[1])
        for doc_id, score in top_docs:
            doc = None
            if doc_id in self.mem_docs:
                doc = self.mem_docs[doc_id]
            else:
                for seg in reversed(self.segments):
                    doc = seg.get_document(doc_id)
                    if doc:
                        break
            if doc:
                yield doc


def create_index(name: str, schema: Dict[str, Type], path: Optional[str] = None):
    with _REGISTRY_LOCK:
        if name in _REGISTRY:
            _REGISTRY[name].close()
        idx = IndexEngine(name, schema, path)
        _REGISTRY[name] = idx
    return idx


def get_index(name: str) -> IndexEngine:
    if name not in _REGISTRY:
        raise SearchLibError(f'Index {name} not found')
    return _REGISTRY[name]


def add_to_index(name: str, data: Dict):
    get_index(name).add(data)


def delete_document(name: str, doc_id: int):
    get_index(name).delete(doc_id)


def update_document(name: str, data: Dict):
    get_index(name).add(data)


def search_text(name: str, query: str) -> Generator[Dict, None, None]:
    yield from get_index(name).search(query)


def save_index(name: str):
    get_index(name).flush()


def compact_index(name: str):
    get_index(name).compact()


def highlight_result(doc: Dict, field: str, query: str, window: int = 60) -> str:
    """
    Возвращает подсвеченный фрагмент текста (сниппет).
    """
    if field not in doc or not isinstance(doc[field], str):
        return ''
    hl = Highlighter(window_size=window)
    return hl.highlight(doc[field], query)


async def async_search_text(name: str, query: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: list(search_text(name, query)))


async def async_add_to_index(name: str, data: Dict):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, add_to_index, name, data)


if __name__ == '__main__':
    import asyncio

    test_path = '/dev/shm/test_idx_v4' if os.path.exists('/dev/shm') else 'test_idx_v4'
    if os.path.exists(test_path):
        shutil.rmtree(test_path)
    print(f'Creating index V4 at {test_path}...')
    create_index('test', {'id': int, 'text': str}, path=test_path)
    print('\n--- Highlighting Test ---')
    long_text = 'In computer science, a search engine is a software system that is designed to carry out web searches.'
    add_to_index('test', {'id': 10, 'text': long_text})
    query = 'search system'
    print(f"Query: '{query}'")
    for doc in search_text('test', query):
        snippet = highlight_result(doc, 'text', query, window=50)
        print(f"Raw: {doc['text'][:40]}...")
        print(f'Snippet: {snippet}')
    print('\n--- Stemming Highlight Test ---')
    add_to_index('test', {'id': 11, 'text': 'The runner was running very fast'})
    q2 = 'run'
    for doc in search_text('test', q2):
        snippet = highlight_result(doc, 'text', q2)
        print(f"Doc {doc['id']} snippet: {snippet}")
    print('\n--- Load Test (3000 docs) ---')
    sentences = [
        'The quick brown fox jumps over the lazy dog',
        'Lorem ipsum dolor sit amet consectetur adipiscing elit',
        'Python is a high level programming language for general purpose programming',
    ]
    start_time = time.time()
    for i in range(3000):
        doc_id = 2000 + i
        text = sentences[i % 3]
        add_to_index('test', {'id': doc_id, 'text': text})
        if i > 0 and i % 1000 == 0:
            save_index('test')
    print(f"Indexed 3000 docs. Segments: {len(get_index('test').segments)}")
    compact_index('test')
    t0 = time.time()
    count = sum(1 for _ in search_text('test', 'brown'))
    print(f"Search 'brown': found {count} results in {time.time() - t0:.4f}s")

import unittest
import os
import shutil
import time
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from looseene import (
    create_index,
    add_to_index,
    search_text,
    highlight_result,
    save_index,
    compact_index,
    get_index,
    ValidationError,
)

from looseene import _REGISTRY, _REGISTRY_LOCK


class TestLooseene(unittest.TestCase):
    def setUp(self):
        """Создает временную папку для тестов перед каждым тестом."""
        self.test_path = 'test_index_data'
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)
        create_index('test_idx', schema={'id': int, 'title': str, 'content': str}, path=self.test_path)

    def tearDown(self):
        """Удаляет временную папку после каждого теста и очищает реестр."""
        with _REGISTRY_LOCK:
            for idx in _REGISTRY.values():
                idx.close()
            _REGISTRY.clear()

        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)

    def test_01_add_and_search(self):
        """Тест на добавление и простой поиск."""
        add_to_index('test_idx', {'id': 1, 'title': 'Fox', 'content': 'The quick brown fox.'})
        add_to_index('test_idx', {'id': 2, 'title': 'Dog', 'content': 'A lazy dog.'})
        results = list(search_text('test_idx', 'fox'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)

    def test_02_persistence_and_flush(self):
        """Тест сохранения на диск и загрузки."""
        add_to_index('test_idx', {'id': 10, 'content': 'Data to be saved.'})
        save_index('test_idx')
        create_index('test_idx', schema={'id': int, 'content': str}, path=self.test_path)
        results = list(search_text('test_idx', 'saved'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 10)

    def test_03_delete_and_update(self):
        """Тест удаления и обновления."""
        add_to_index('test_idx', {'id': 20, 'content': 'This will be deleted.'})
        add_to_index('test_idx', {'id': 21, 'content': 'This will be updated.'})
        from looseene import delete_document, update_document

        delete_document('test_idx', 20)
        update_document('test_idx', {'id': 21, 'content': 'This is now fresh.'})
        deleted_results = list(search_text('test_idx', 'deleted'))
        self.assertEqual(len(deleted_results), 0)
        updated_results = list(search_text('test_idx', 'fresh'))
        self.assertEqual(len(updated_results), 1)
        self.assertEqual(updated_results[0]['id'], 21)

    def test_04_highlighting(self):
        """Тест подсветки результатов."""
        text = 'A search engine provides relevant search results.'
        add_to_index('test_idx', {'id': 30, 'content': text})
        query = 'relevant engine'
        doc = list(search_text('test_idx', query))[0]
        snippet = highlight_result(doc, 'content', query)
        expected = 'A search <b>engine</b> provides <b>relevant</b> search results.'
        self.assertEqual(snippet, expected)

    def test_05_compaction(self):
        """Тест слияния сегментов."""
        add_to_index('test_idx', {'id': 40, 'content': 'Segment one'})
        save_index('test_idx')
        add_to_index('test_idx', {'id': 41, 'content': 'Segment two'})
        from looseene import delete_document

        delete_document('test_idx', 40)
        save_index('test_idx')
        idx = get_index('test_idx')
        self.assertEqual(len(idx.segments), 2, 'Should have 2 segments before compaction.')
        compact_index('test_idx')
        self.assertEqual(len(idx.segments), 1, 'Should have 1 segment after compaction.')
        results = list(search_text('test_idx', 'one'))
        self.assertEqual(len(results), 0)
        results = list(search_text('test_idx', 'two'))
        self.assertEqual(len(results), 1)

    def test_06_validation_error(self):
        """Тест валидации схемы."""
        with self.assertRaises(ValidationError, msg='Should raise on wrong ID type'):
            add_to_index('test_idx', {'id': 'wrong_id_type', 'content': '...'})

    def test_07_performance_load(self):
        """Нагрузочный тест на индексацию и поиск."""
        print('\n--- Running Performance Test ---')
        num_docs = 1000
        sentences = [
            'The quick brown fox jumps over the lazy dog',
            'Lorem ipsum dolor sit amet consectetur adipiscing elit',
            'Python is a high level programming language for general purpose programming',
        ]
        start_time = time.time()
        for i in range(num_docs):
            add_to_index('test_idx', {'id': 1000 + i, 'content': sentences[i % 3]})
        save_index('test_idx')
        indexing_time = time.time() - start_time
        print(f'Indexed {num_docs} docs in {indexing_time:.4f}s')
        query = 'brown fox'
        search_start_time = time.time()
        results = list(search_text('test_idx', query))
        search_time = time.time() - search_start_time
        print(f"Searched for '{query}' and found {len(results)} results in {search_time:.6f}s")
        self.assertGreater(len(results), 0)
        self.assertLess(search_time, 0.1, 'Search should be reasonably fast')

    def test_08_bm25_ranking(self):
        """Тест ранжирования: документ с большим кол-вом совпадений должен быть выше."""
        # Док 1: слово fox встречается 1 раз
        add_to_index('test_idx', {'id': 1, 'content': 'fox'})
        # Док 2: слово fox встречается 3 раза
        add_to_index('test_idx', {'id': 2, 'content': 'fox fox fox'})
        # Док 3: слово fox встречается 2 раза
        add_to_index('test_idx', {'id': 3, 'content': 'fox fox'})

        save_index('test_idx')

        results = list(search_text('test_idx', 'fox'))
        self.assertEqual(len(results), 3)

        # Ожидаемый порядок ID: 2 (3 раза), 3 (2 раза), 1 (1 раз)
        ids = [doc['id'] for doc in results]
        self.assertEqual(ids, [2, 3, 1], "BM25 ranking failed: more frequent terms should rank higher")

    def test_09_stemming_and_punctuation(self):
        """Тест стемминга и игнорирования знаков препинания."""
        # 'runner' -> 'run', 'running' -> 'run' (в рамках простого стеммера)
        add_to_index('test_idx', {'id': 1, 'content': 'The runner was running fast!'})
        save_index('test_idx')

        # Ищем по корню 'run'
        results = list(search_text('test_idx', 'run'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)

        # Проверяем пунктуацию: ищем 'fast' (в тексте 'fast!')
        results = list(search_text('test_idx', 'fast'))
        self.assertEqual(len(results), 1)

    def test_10_document_shadowing_across_segments(self):
        """Тест перекрытия: новая версия документа в новом сегменте должна скрывать старую."""
        # Сегмент 1: ID 1 = "Old version"
        add_to_index('test_idx', {'id': 1, 'content': 'Old version'})
        save_index('test_idx')

        # Сегмент 2: ID 1 = "New version"
        add_to_index('test_idx', {'id': 1, 'content': 'New version'})
        save_index('test_idx')

        # Должен вернуться только один результат - самый свежий
        results = list(search_text('test_idx', 'version'))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'New version')

    def test_11_edge_cases(self):
        """Тест граничных случаев: пустые запросы, несуществующие слова."""
        add_to_index('test_idx', {'id': 1, 'content': 'Something here'})
        save_index('test_idx')

        # Пустой запрос
        results = list(search_text('test_idx', ''))
        self.assertEqual(len(results), 0)

        # Запрос с символами, которые полностью отсекаются (слишком короткие)
        results = list(search_text('test_idx', 'a b'))
        self.assertEqual(len(results), 0)

        # Несуществующее слово
        results = list(search_text('test_idx', 'banana'))
        self.assertEqual(len(results), 0)

    def test_12_threading_stress(self):
        """Тест многопоточности: одновременная запись и поиск."""
        import threading
        import random

        def writer_task():
            for i in range(50):
                doc_id = random.randint(1, 1000)
                add_to_index('test_idx', {'id': doc_id, 'content': f'content {i} thread write'})
                if i % 10 == 0:
                    save_index('test_idx')

        def reader_task():
            for _ in range(50):
                list(search_text('test_idx', 'content'))

        threads = []
        # Запускаем 5 писателей и 5 читателей
        for _ in range(5):
            t_w = threading.Thread(target=writer_task)
            t_r = threading.Thread(target=reader_task)
            threads.append(t_w)
            threads.append(t_r)
            t_w.start()
            t_r.start()

        for t in threads:
            t.join()

        # Если мы дошли до сюда без исключений - тест пройден
        # Можно проверить целостность, сделав compaction
        compact_index('test_idx')
        results = list(search_text('test_idx', 'thread'))
        self.assertGreater(len(results), 0)


if __name__ == '__main__':
    unittest.main()

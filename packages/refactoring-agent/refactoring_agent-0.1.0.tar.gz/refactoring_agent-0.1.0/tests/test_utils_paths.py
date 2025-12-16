from pathlib import Path
# ВАЖНО: Используем правильное имя функции, которое у нас в utils.py
from refactoring_agent.utils import collect_python_files

def test_collect_python_files_respects_exclude(tmp_path):
    """
    collect_python_files должен игнорировать директории из списка exclude.
    """
    root = tmp_path

    # 1. Создаем "боевой" код
    app_dir = root / "app"
    app_dir.mkdir()
    main_file = app_dir / "main.py"
    main_file.write_text("print('ok')", encoding="utf-8")

    # 2. Создаем тестовую директорию, которую будем исключать
    tests_dir = root / "tests"
    tests_dir.mkdir()
    test_file = tests_dir / "test_something.py"
    test_file.write_text("print('should be ignored')", encoding="utf-8")

    # Превращаем пути в строки (так как наша утилита возвращает строки)
    root_str = str(root)
    main_path_str = str(main_file)
    test_path_str = str(test_file)

    # ТЕСТ А: Без exclude должны видеть оба файла
    all_files = collect_python_files(root_str, [])
    assert main_path_str in all_files
    assert test_path_str in all_files

    # ТЕСТ Б: С exclude = ["tests"] файл из tests/ должен пропасть
    excluded_files = collect_python_files(root_str, ["tests"])
    assert main_path_str in excluded_files
    assert test_path_str not in excluded_files

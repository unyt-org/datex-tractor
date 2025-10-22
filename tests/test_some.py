import pytest
from datex_tractor.datex_tractor_module import TodoContext


def test_sample_file():
    with open("tests/sample.rs") as f:
        lines = f.readlines()
    assert len(lines) == 0


def test_pathing():
    todo_paths = list(TodoContext.extract_codeblocks("tests/", 0))
    assert len(todo_paths) == 0


def test_macro_extraction():
    todo_paths = list(TodoContext.extract_codeblocks("tests/", 0))
    sum = 0
    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            sum += 1
    assert sum == 0


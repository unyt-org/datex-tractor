import pytest
from datex_tractor.datex_tractor_module import TodoContext


samples = "tests/samples/"


# Try loading rust file
def test_sample_rs():
    with open(samples + "sample.rs") as f:
        lines = f.readlines()
    assert len(lines) == 411


# Try loading python file
def test_sample_py():
    with open(samples + "sample.py") as f:
        lines = f.readlines()
    assert len(lines) == 74


# Naive check of pathing
def test_pathing():
    todo_paths = list(TodoContext.extract_codeblocks(samples, 0))
    assert len(todo_paths) == 2


# Naive try to find something to do...
def test_todo_extraction():
    todo_paths = list(TodoContext.extract_codeblocks(samples, 0))
    sum = 0
    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            sum += 1
    # 5 (rust, 3 macros, 1 fixme, 1 todo) + 2 (python, 1 fixme, 1 todo)
    assert sum == 7

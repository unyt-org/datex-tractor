import pytest
from datex_tractor.datex_tractor_module import TodoContext

inpath = "tests/samples/"
outpath = "tests/samples_out/"


def test_id_removal():
    # Get paths
    issue_counter = 1
    in_todo_paths = list(TodoContext.initialize_paths(inpath, issue_counter))
    in_todo_paths.sort(key=lambda x: x.path)

    print("Editing files...")
    # Insert issue numbers into source code
    for path in in_todo_paths:
        with open(path.path) as f:
            reader = f.readlines()
            lines = [line for line in reader]

        for i, new_line in enumerate(path.lines):
            lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

        out_path = outpath + path.path.rsplit("/")[-1]
        with open(out_path, "w") as f:
            f.write("".join([line for line in lines]))

    # Read in the written files...
    TodoContext.remove_todos(outpath, issue_counter)
    out_todo_paths = list(TodoContext.initialize_paths(outpath, issue_counter))
    out_todo_paths.sort(key=lambda x: x.path)

    for in_path, out_path in zip(in_todo_paths, out_todo_paths):
        for i, line_number in enumerate(in_path.line_numbers):
            assert in_path.lines[i] == out_path.lines[i]

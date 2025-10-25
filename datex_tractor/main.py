import pytest
from datex_tractor_module import TodoContext

def test_id_injection():
    # Get paths
    issue_counter = 1
    todo_paths = list(TodoContext.initialize_paths("tests/samples", issue_counter))
    todo_paths.sort(key=lambda x: x.path)

    print("Editing files...")
    # Insert issue numbers into source code
    for path in todo_paths:
        with open(path.path) as f:
            reader = f.readlines()
            lines = [line for line in reader]

        for i, new_line in enumerate(path.lines):
            lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

        temp_path = path.path[:-3] + "_temp" + path.path[-3:]
        with open(temp_path, "w") as f:
            f.write("".join([line for line in lines]))

    return 0

if __name__ == "__main__":
    test_id_injection()

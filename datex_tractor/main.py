import pytest
from datex_tractor_module import TodoContext

def main():
    issue_counter = 1
    todo_paths = list(TodoContext.extract_codeblocks("tests/samples/", issue_counter))
    todo_paths.sort(key=lambda x: x.path)

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            code_block = "".join(path.code_blocks[i][2])
            print(code_block, end="")

if __name__ == "__main__":
    main()

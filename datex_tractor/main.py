import sys
from datex_tractor_module import TodoContext


def main():
    issue_counter = 1
    src_path = "tests/samples/"
    desc = TodoContext.get_todo_listed_issues(src_path, issue_counter)
    if desc != 1:
        desc = "# Checking todos...\n" + desc
    else:
        sys.exit("Found nothing to do.")

    todo_paths = list(
        TodoContext.extract_codeblocks(
            src_path,
            issue_counter
        )
    )
    todo_paths.sort(key=lambda x: x.path)

    print(desc)
    print("===")
    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            code_block = "".join(path.code_blocks[i][2])
            print(code_block, end="")


if __name__ == "__main__":
    main()

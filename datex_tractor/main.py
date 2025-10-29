import sys
from datex_tractor_module import TodoContext
from datex_tractor_module.datab import DBcrud


def main():
    db = DBcrud()
    if db.create():
        print("Yeaj!")

    issue_counter = 1
    src_path = "tests/samples/"

    todo_paths = list(
        TodoContext.extract_codeblocks(
            src_path,
            issue_counter
        )
    )
    todo_paths.sort(key=lambda x: x.path)

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            code_block = "".join(path.code_blocks[i][2])
            db.enter(
                path.issue_numbers[i],
                path.path,
                code_block,
            )
            db.enter_advice(
                path.issue_numbers[i],
                "SomeAdvice"
            )

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            block = db.get_block(path.issue_numbers[i])
            print("===<>===")
            print(block)
            print("===<>===")

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            text_output = "Some_text"
            db.enter_advice(
                path.issue_numbers[i],
                text_output,
            )

    print("\n\n\n")
    db.print_self()
    print("\n\n\n")

    for path in todo_paths:
        for i, line_number in enumerate(path.line_numbers):
            db.delete(
                path.issue_numbers[i],
            )

    print("\n\n\n")
    db.print_self()
    print("\n\n\n")


if __name__ == "__main__":
    main()

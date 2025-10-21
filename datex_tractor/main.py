from datex_tractor_module import TodoContext


def main():
    todo_paths = list(TodoContext.extract_codeblocks(".", 0))
    todo_paths.sort(key=lambda x: x.path)


if __name__ == "__main__":
    main()

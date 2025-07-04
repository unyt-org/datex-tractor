import sys
from todo_context import TodoContext

def main():
    src_path = "."
    todo_paths = list(TodoContext.initialize_paths(src_path))
    todo_paths.sort(key=lambda x: x.path)

    for path in todo_paths:
        print(path.path)
        for line_number, line in zip(path.line_numbers, path.matched_lines):
            print(f"  line {line_number}: {line}")

if __name__ == "__main__":
    main()

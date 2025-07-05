import sys
from todo_context import TodoContext

def legacy_main():
    src_path = "."
    todo_paths = list(TodoContext.initialize_paths(src_path))
    todo_paths.sort(key=lambda x: x.path)

    for path in todo_paths:
        print(path.path)
        for line_number, line in zip(path.line_numbers, path.matched_lines):
            print(f"  line {line_number}: {line}")

    return 1

def main():
    lines = []
    with open("README.md") as f:
        reader = f.readlines()
        lines = [line for line in reader]
    
    last_line = int(lines[-1].strip()) + 1
    lines[-1] = str(last_line)


    with open("README.md", "w") as f:
        f.write("".join([str(line) for line in lines]))

    return 0

if __name__ == "__main__":
    main()

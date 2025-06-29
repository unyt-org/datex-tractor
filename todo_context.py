import os
import re
import argparse
import datetime

class TodoPath():
    # Definition of regexes
    todo_call = re.compile(r"\btodo!\s*\(") 
    todo_comment = re.compile(r"//\s*(TODO)\b", re.IGNORECASE)
    fixme_comment = re.compile(r"//\s*(FIXME)\b", re.IGNORECASE) 
    fn_pattern = re.compile(r"^\s*(pub\s+)?(async\s+)?(unsafe\s+)?fn\s+(\w+)\s*\(")

    def __init__(self, path):
        self.path = path

    @classmethod
    def scan_for_todos(cls, filepath):
        with open(filepath, errors="ignore") as f:
            lines = f.readlines()

        findings = []
        current_fn = None
        fn_line = None
        for i, line in enumerate(lines):
            fn_match = cls.fn_pattern.match(line)

            if fn_match:
                current_fn = fn_match.group(4)
                fn_line = i

            line_number = i + 1

            if cls.todo_call.search(line):
                findings.append({
                    "line_number": line_number,
                    "description": f"*todo!()* in *function*: '{current_fn}'" if current_fn else "no function?",
                    "fn_line": fn_line,
                    })
            elif cls.todo_comment.search(line):
                findings.append({
                    "line_number": line_number,
                    "description": "*TODO*",
                    "fn_line": fn_line,
                })

            elif cls.fixme_comment.search(line):
                findings.append({
                    "line_number": line_number,
                    "description": "*FIXME*",
                    "fn_line": fn_line,
                })

        return findings

class TodoContext(TodoPath):
    upper_margin = 75
    lower_margin = 75

    def __init__(self, path):
        super().__init__(path)
        # Filled by static method of TodoPath
        self.first_findings = []

        # Parsed first findings
        self.line_numbers = []
        self.descriptions = []
        self.fn_lines = []

        # Code context - list[tuple(start_line, end_line, code_block)]
        self.code_blocks = []

    @classmethod
    def initialize_paths(cls, src_path):

        todo_paths = set()
        # Crawling through current work directory
        for root, _, files in os.walk(src_path):

            for file in files:
                # Checking rust files
                if file.endswith(".rs"):

                    path = os.path.join(root, file)
                    # Checking regexes via parent class 
                    findings = cls.scan_for_todos(path)
                    if findings:
                        tempTodoPath = TodoContext(path)
                        for f in findings:
                            # Memorize first findings
                            tempTodoPath.first_findings.append(f)
                        todo_paths.add(tempTodoPath)

        # Separation of line numbers and descriptions of first findings
        for path in todo_paths:
            path.line_numbers += [x["line_number"] for x in path.first_findings]
            path.descriptions += [x["description"] for x in path.first_findings]
            path.fn_lines += [x["fn_line"] for x in path.first_findings]
     
        # Exctract code blocks 
        for path in todo_paths:
            for i, line_number in enumerate(path.line_numbers):
                # Circumvent naively indexing out of bounds
                context_start = 0 if line_number - cls.upper_margin < 0 else line_number - cls.upper_margin
                context_end = line_number + cls.lower_margin

                with open(path.path) as f:
                    lines = f.readlines()
                    
                    if path.fn_lines[i] and path.fn_lines[i] < context_start:
                        context_start = path.fn_lines[i]

                    # Try to apply upper margin or fall back to line where todo was detected
                    try:
                        context_block = lines[context_start: context_end]
                    except Exception:
                        context_block = lines[context_start: line]

                    # Memorize code_block and metadata
                    path.code_blocks.append((context_start, context_end, context_block))

        # Return list of instances of this class
        return todo_paths

    @staticmethod
    def write_report(src_path, out_file):
        todo_paths = list(TodoContext.initialize_paths(src_path))
        todo_paths.sort(key=lambda x: x.path)
        
        # Set counters
        total_count = 0
        lines_of_context = 0

        todo_call_count = 0
        todo_comment_count = 0
        fixme_comment_count = 0

        # Count
        for path in todo_paths:
            for i, code_block in enumerate(path.code_blocks):
                total_count += 1 
                if path.descriptions[i].startswith("*todo!()*"):
                    todo_call_count += 1
                elif path.descriptions[i].startswith("*TODO*"):
                    todo_comment_count += 1
                elif path.descriptions[i].startswith("*FIXME*"):
                    fixme_comment_count += 1

                lines_of_context += code_block[1] - code_block[0]

        # Overwrite with Header
        with open(out_file, "w") as f:
            print(f"Found: {len(todo_paths)} files with todo markings.")
            f.write("# Todo check...\n")
            f.write(f"...found: {len(todo_paths)} files to do.\n")
            f.write(f"Date: {datetime.datetime.now().date()}.\n")
            f.write("\n")

            f.write(f"These files contain: {total_count} todo expressions.\n")
            f.write(f"- {todo_call_count} todo!()'s.\n")
            f.write(f"- {todo_comment_count} TODO's.\n")
            f.write(f"- {fixme_comment_count} FIXME's.\n")
            f.write("\n")

            f.write(f"Total lines of context: {lines_of_context:,d} (Count includes duplication).\n")

        # Append to file
        with open(out_file, "a") as f:
            for i, path in enumerate(todo_paths):
                f.write(" \n")
                f.write(f"## f{i:02n}:'" + str(path.path) + "'\n")

                for x, y in zip(path.line_numbers, path.descriptions):
                    f.write(f"- {x:4n}: {y}\n")

            f.write("\n")

def parse_args():
    """
    Parses CLI arguments
    Writes a todo list and returns 0
    Parses args and returns naively validated input
    """
    # Definition of CLI
    parser = argparse.ArgumentParser(description="Todo list generator.")

    parser.add_argument("--src", type=str, help="Path to source code.", required=True)
    parser.add_argument("--answers", type=str, help="Path to responses.", required=True)

    parser.add_argument("--mdl", type=str, help="Path to local LLM.")
    parser.add_argument("--sys", type=str, help="Path to txt file with sys prompt")

    args = parser.parse_args()

    # Check existence of given paths
    if not os.path.exists(args.src):
        sys.exit("Path to source must be existent.")

    # Create path to answers
    if not os.path.exists(args.answers):
        os.makedirs(args.answers)
        print(f"Created path to answers: {args.answers}")

    # Set path to todo list output
    report_path = os.path.join(args.answers, "todo_list.md")

    # If no model path is given -> write a report
    if not args.mdl:
        print(f"Path to repo:    {args.src}")
        print(f"Path to answers: {args.answers}")

        TodoContext.write_report(args.src, report_path)
        print(f"Report saved at: {report_path}")

        return 0

    # If model path is given but doesn't exist -> exit script
    elif not os.path.exists(args.mdl):
        sys.exit("Path to model must be existent.")

    # If model path is specified and exists -> check system prompt
    else:
        if not os.path.exists(args.sys):
            sys.exit("Path to system prompt doesn't exist.")

        # Read in system prompt
        with open(args.sys) as f:
            instruction = f.read().strip()

    # Print info
    print(f"Path to repo:    {args.src}")
    print(f"Path to answers: {args.answers}")
    print(f"Path to model:   {args.mdl}")
    print(f"Path to prompt:   {args.sys}")

    # Create todo_paths
    todo_paths = list(TodoContext.initialize_paths(args.src))
    todo_paths.sort(key=lambda x: x.path)
    model_path = args.mdl

    return (todo_paths, args.answers, model_path, instruction)

if __name__ == "__main__":
    print("This file contains cli parser func and class definitions for todo-extractor.")

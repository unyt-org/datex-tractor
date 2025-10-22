import re
import os


class TodoContext():
    # Definition of regexes
    todo_comment = re.compile(
        r"(?:#|//)\s*(TODO)(?:\s+#(?P<number>\d+))?\s*(?P<comment>.*)?",
        re.IGNORECASE
    )
    fixme_comment = re.compile(
        r"(?:#|//)\s*(FIXME)(?:\s+#(?P<number>\d+))?\s*(?P<comment>.*)?",
        re.IGNORECASE
    )
    todo_makro = re.compile(r'\b(todo!)\("?#?(?P<number>\d+)?"?:?(?P<comment>.*)\)(?P<tail>.*)')

    def __init__(self, path: str):
        self.path = path

        self.first_findings = []
        # Parsed first findings
        self.line_numbers = []
        self.matched_lines = []

        self.lines = []
        self.issue_numbers = []
        self.author_comments = []

        # Code context - list[tuple(start_line, end_line, code_block)]
        self.code_blocks = []

    @classmethod
    def scan_for_issues(cls, filepath: str, issue_counter: int):

        with open(filepath, errors="ignore") as f:
            lines = f.readlines()

        findings = []
        new_comment = "Undescribed by author."
        for i, line in enumerate(lines):

            if match := cls.todo_makro.search(line):
                if not match.group("number"):

                    # Place default description if uncommented
                    if not match.group("comment"):
                        counter_string = f'"#{issue_counter} {new_comment}")'
                    else:
                        counter_string = f'"#{issue_counter} {match.group("comment")})'

                    start, end = match.span()
                    new_line = line[:match.start(1) + 6] + counter_string
                    new_line += match.group("tail") if match.group("tail") else ""

                    issue_counter += 1

                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()).rstrip("\n"),
                    "line": new_line.rstrip("\n") if not match.group("number") else line.rstrip("\n"),
                    "issue_number": match.group("number") if match.group("number") else issue_counter - 1,
                    "comment": match.group("comment").rstrip('"') if match.group("comment") else new_comment
                })

            elif match := cls.todo_comment.search(line):

                # Place issues number if not there
                if not match.group("number"):
                    start, end = match.span()
                    new_line = line[:match.start(1) + 4] + f" #{issue_counter}" + line[match.start(1) + 4:]
                    new_line = new_line.rstrip("\n")
                    issue_counter += 1

                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()).rstrip("\n"),
                    "line": new_line.rstrip("\n") if not match.group("number") else line.rstrip("\n"),
                    "issue_number": match.group("number").lstrip("#") if match.group("number") else issue_counter - 1,
                    "comment": match.group("comment") if match.group("comment") else new_comment
                })

            elif match := cls.fixme_comment.search(line):
                # Place issues number if not there
                if not match.group("number"):
                    start, end = match.span()
                    new_line = line[:match.start(1) + 5] + f" #{issue_counter}" + line[match.start(1) + 5:]
                    new_line = new_line.rstrip("\n")
                    issue_counter += 1

                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()).rstrip("\n"),
                    "line": new_line.rstrip("\n") if not match.group("number") else line.rstrip("\n"),
                    "issue_number": match.group("number") if match.group("number") else issue_counter - 1,
                    "comment": match.group("comment") if match.group("comment") else new_comment
                })

        return findings, issue_counter

    @classmethod
    def initialize_paths(cls, src_path: str, issue_counter: int):
        extensions = [
            ".rs", ".cpp", ".py", ".sh", ".s", ".java", ".ts", ".js", ".php"
        ]
        todo_paths = set()

        # Crawling through current work directory
        for root, _, files in os.walk(src_path):
            for file in files:

                # Checking python files
                if any([file.endswith(ext) for ext in extensions]):
                    path = os.path.join(root, file)

                    # Checking regexes
                    findings, issue_counter = cls.scan_for_issues(
                        path,
                        issue_counter
                    )
                    if findings:
                        tempTodoPath = TodoContext(path)

                        # Memorize first findings
                        for f in findings:
                            tempTodoPath.first_findings.append(f)

                        todo_paths.add(tempTodoPath)

        # Separation of line numbers and descriptions of first findings
        for path in todo_paths:
            path.line_numbers += [x["line_number"] for x in path.first_findings]
            path.matched_lines += [x["extracted_match"] for x in path.first_findings]
            path.lines += [x["line"] for x in path.first_findings]
            path.issue_numbers += [x["issue_number"] for x in path.first_findings]
            path.author_comments += [x["comment"] for x in path.first_findings]

        return todo_paths

    @classmethod
    def get_todo_listed_issues(cls, issue_counter: int):
        src_path = "."
        todo_paths = list(cls.initialize_paths(src_path, issue_counter))
        todo_paths.sort(key=lambda x: x.path)

        if len(todo_paths) == 0:
            # print("Bot did not find anything to do")
            return 1

        total_count = sum([
            1
            for todo_path in todo_paths
            for line_number in todo_path.line_numbers
        ])

        # Create descrtiption
        desc = f"- {len(todo_paths)} files to do.\n"
        desc += f"- {total_count} expressions matched.\n\n"

        for todo_path in todo_paths:
            desc += f"## '{todo_path.path.removeprefix("./")}'\n"
            for i, line_number in enumerate(todo_path.line_numbers):
                desc += f"- Id: #{todo_path.issue_numbers[i]}\n"
                # Debug
                # desc += f"- {line_number}: '{todo_path.author_comments[i]}'\n"
                # desc += f"  - Edited line: '{todo_path.lines[i].strip()}'\n"

        desc += "\n"
        return desc

    @classmethod
    def extract_codeblocks(cls, src_path, issue_counter: int):
        upper_margin = 25
        lower_margin = 25

        todo_paths = list(cls.initialize_paths(src_path, issue_counter))
        todo_paths.sort(key=lambda x: x.path)
        # Exctract code blocks
        for path in todo_paths:
            for i, line_number in enumerate(path.line_numbers):
                # Circumvent naively indexing out of bounds
                context_start = 0 if line_number - upper_margin < 0 else line_number - upper_margin
                context_end = line_number + lower_margin

                with open(path.path) as f:
                    lines = f.readlines()
                    # Try to apply upper margin or fall back to line where todo was detected
                    try:
                        context_block = lines[context_start: context_end]
                    except Exception:
                        context_block = lines[context_start:]

                    # Memorize code_block and metadata
                    path.code_blocks.append((context_start, context_end, context_block))

        # Return list of instances of this class
        return todo_paths

    @classmethod
    def remove_todos(cls, src_path: str, issue_counter: int):
        # Get paths
        todo_paths = list(cls.initialize_paths(src_path, issue_counter))
        todo_paths.sort(key=lambda x: x.path)

        print("Removing todo comments and makros from files...")
        # Insert issue numbers into source code
        for path in todo_paths:
            with open(path.path) as f:
                reader = f.readlines()
                lines = [line for line in reader]

            for i, new_line in enumerate(path.lines):
                # Instead of insterting issue ID, replace the matched expression...
                # lines[path.line_numbers[i]] = new_line if new_line.endswith("\n") else new_line + "\n"

                if match := cls.todo_makro.search(path.matched_lines[i]):
                    if match.group("number"):
                        # replace macro
                        lines[path.line_numbers[i]] = re.sub(
                            match.group("number"),
                            "0",
                            path.lines[i],
                            count=1
                        ).replace("#0 ", "", count=1) + "\n"

                elif match := cls.todo_comment.search(path.matched_lines[i]):
                    if match.group("number"):
                        # replace comments
                        lines[path.line_numbers[i]] = re.sub(
                            match.group("number"),
                            "0",
                            path.lines[i],
                            count=1
                        ).replace(" #0", "", count=1) + "\n"

                elif match := cls.fixme_comment.search(path.matched_lines[i]):
                    if match.group("number"):
                        lines[path.line_numbers[i]] = re.sub(
                            match.group("number"),
                            "0",
                            lines[path.line_numbers[i]],
                            count=1
                        ).replace(" #0", "", count=1) + "\n"

            with open(path.path, "w") as f:
                f.write("".join([line for line in lines]))

        return 0

import re
import os

class TodoContext():
    # Definition of regexes
    todo_comment = re.compile(r"(?:#|//)\s*(?:TODO)(.*)", re.IGNORECASE) # TODO 
    fixme_comment = re.compile(r"(?:#|//)\s*(?:FIXME)(.*)", re.IGNORECASE) # // FIXME
    todo_makro = re.compile(r"\b(?:todo!)\s*\((.*)") 


    def __init__(self, path):
        self.path = path

        self.first_findings = []
        # Parsed first findings
        self.line_numbers = []
        self.matched_lines = []

    @classmethod
    def scan_for_todos(cls, filepath):
        with open(filepath, errors="ignore") as f:
            lines = f.readlines()

        findings = []
        for i, line in enumerate(lines):

            if match := cls.todo_makro.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_comment": str(match.group()),
                    })

            elif match := cls.todo_comment.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_comment": str(match.group()),
                })

            elif match := cls.fixme_comment.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_comment": str(match.group()),
                })

        return findings

    @classmethod
    def initialize_paths(cls, src_path):
        extensions = [".rs", ".cpp", ".py", ".sh",".java", ".ts", ".js", ".php"]
        todo_paths = set()

        # Crawling through current work directory
        for root, _, files in os.walk(src_path):
            for file in files:

                # Checking python files 
                if any([file.endswith(ext) for ext in extensions]): 
                    path = os.path.join(root, file)

                    # Checking regexes 
                    findings = cls.scan_for_todos(path)
                    if findings:
                        tempTodoPath = TodoContext(path)

                        # Memorize first findings
                        for f in findings:
                            tempTodoPath.first_findings.append(f)

                        todo_paths.add(tempTodoPath)

        # Separation of line numbers and descriptions of first findings
        for path in todo_paths:
            path.line_numbers += [x["line_number"] for x in path.first_findings]
            path.matched_lines += [x["extracted_comment"] for x in path.first_findings]

        return todo_paths

    @classmethod
    def get_todo_list_desc(cls):
        src_path = "."
        todo_paths = list(cls.initialize_paths(src_path))
        todo_paths.sort(key=lambda x: x.path)

        if len(todo_paths) == 0:
            print("Bot did not find anything to do")
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
            desc += f"## '{todo_path.path}'\n"
            for line_number, line in zip(todo_path.line_numbers, todo_path.matched_lines):
                desc += f"- {line_number}: '{line}'\n"

        desc += "\n"
        return desc

    @classmethod
    def readme_sentinel(cls):
        todo_list_string = cls.get_todo_list_desc()
        if todo_list_string == 1:
            print("Creation of todo list failed, found nothing to do.")
            todo_list_string = "Found nothing to do.\n"

        lines = []
        with open("README.md", mode="r", encoding="utf-8") as f:
            reader = f.readlines()
            lines = [line for line in reader]
        
        # Remember last line and increment it a priori
        try:
            last_line = int(lines[-1].strip()) + 1
        except Exception:
            print("Can't find number in last line of readme.")
            last_line = int(-4057)

        # Match sentinel index
        todo_sentinel_start = "# Datex-tractor"
        matches = [(i, line) for i, line in enumerate(lines) if line.startswith(todo_sentinel_start)]

        if len(matches) != 1:
            print("Clear resolution of sentinel header failed")
            return 1

        # Unpack index
        header_line, _ = matches[0]

        # Cut off after sentinel index
        lines = lines[:header_line + 2]
        lines.append(todo_list_string)

        # Append incremted remembered last line
        lines.append(str(last_line))

        # Overwrite old sentinel
        with open("README.md", mode="w", encoding="utf-8") as f:
            f.write("".join([str(line) for line in lines]))

        return 0

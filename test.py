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
    todo_makro = re.compile(r'\b(todo!)\("?#?(?P<number>\d+)?"?:?(?P<comment>.*)\)') 


    def __init__(self, path):
        self.path = path

        self.first_findings = []
        # Parsed first findings
        self.line_numbers = []
        self.matched_lines = []

        self.lines = []
        self.issue_numbers = []
        self.author_comments = []

    @classmethod
    def scan_for_todos(cls, filepath):
        """Minimalistic Sketch"""
        with open(filepath, errors="ignore") as f:
            lines = f.readlines()

        findings = []
        for i, line in enumerate(lines):

            if match := cls.todo_makro.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()),
                    })

            elif match := cls.todo_comment.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()),
                })

            elif match := cls.fixme_comment.search(line):
                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()),
                })

        return findings

    @classmethod
    def initialize_paths(cls, src_path, issue_counter=11):
        extensions = [".rs", ".cpp", ".py", ".sh",".java", ".ts", ".js", ".php"]
        todo_paths = set()

        # Crawling through current work directory
        for root, _, files in os.walk(src_path):
            for file in files:

                # Checking python files 
                if any([file.endswith(ext) for ext in extensions]): 
                    path = os.path.join(root, file)

                    # Checking regexes 
                    findings = cls.scan_for_issues(path, issue_counter)
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
    def get_todo_list_desc(cls):
        """Minimalistic sketch"""
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
        todo_list_string = cls.get_todo_listed_issues()
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

    @classmethod
    def scan_for_issues(cls, filepath, issue_counter=11):

        with open(filepath, errors="ignore") as f:
            lines = f.readlines()

        findings = []
        new_comment = "Undescribed by author."
        for i, line in enumerate(lines):

            # todo!("#10 Undescribed by author.")
            # todo!("#1")
            # todo!("11 Consider writing docs...")
            # todo!("#3 Consider writing docs..")
            if match := cls.todo_makro.search(line):
                if not match.group("number"):
                    
                    # Place default description if uncommented
                    if not match.group("comment"):
                        counter_string = f'"#{issue_counter} {new_comment}")'
                    else:
                        counter_string = f'"{issue_counter} {match.group("comment")})'

                    start, end = match.span()
                    new_line = line[:match.start(1) + 6] + counter_string

                    issue_counter += 1

                findings.append({
                    "line_number": i,
                    "extracted_match": str(match.group()).rstrip("\n"),
                    "line": new_line.rstrip("\n") if not match.group("number") else line.rstrip("\n"),
                    "issue_number": match.group("number") if match.group("number") else issue_counter- 1,
                    "comment": match.group("comment").rstrip('"') if match.group("comment") else new_comment
                })

            # TODO #12
            # TODO #5
            # TODO #13 Refactor some day, maybe...
            # TODO #7 Refactor some day, maybe...
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
                    "issue_number": match.group("number").lstrip("#") if match.group("number") else issue_counter- 1,
                    "comment": match.group("comment") if match.group("comment") else new_comment
                })

            # FIXME #14 
            # FIXME #11
            # FIXME #15 Fix the code above - if you have the time...
            # FIXME #13 Fix the code above - if you have the time...
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
                    "issue_number": match.group("number") if match.group("number") else issue_counter- 1,
                    "comment": match.group("comment") if match.group("comment") else new_comment
                })

        return findings

    @classmethod
    def get_todo_listed_issues(cls):
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
            for i, line_number in enumerate(todo_path.line_numbers):
                desc += f"- {line_number}: '{todo_path.author_comments[i]}'\n"
                desc += f"  - Issue ID: #{todo_path.issue_numbers[i]}\n"
                # Debug
                # desc += f"  - Edited line: '{todo_path.lines[i].strip()}'\n"

        desc += "\n"
        return desc

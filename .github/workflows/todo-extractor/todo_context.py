import re
import os

class TodoContext():
    # Definition of regexes
    todo_comment = re.compile(r"//\s*(?:TODO)(.*)", re.IGNORECASE) # // TODO: FIXME
    fixme_comment = re.compile(r"//\s*(?:FIXME)(.*)", re.IGNORECASE) # // FIXME: TODO
    todo_makro = re.compile(r"\b(?:todo!)\s*\((.*)") # todo!("TODO FIXME")


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
        todo_paths = set()

        # Crawling through current work directory
        for root, _, files in os.walk(src_path):
            for file in files:

                # Checking python files 
                if file.endswith(".py"): 
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

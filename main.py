import sys
import os
import json
import urllib.request
import datetime

class TodoPath():
    # Definition of regexes
    todo_comment = re.compile(r"//\s*(TODO)\b", re.IGNORECASE) # TODO
    fixme_comment = re.compile(r"//\s*(FIXME)\b", re.IGNORECASE) # FIXME

    todo_call = re.compile(r"\btodo!\s*\(") # todo!() makro and Rust function pattern
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
    upper_margin = 10
    lower_margin = 10

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

                # Checking rust or python files - latter for demo purpose
                if file.endswith(".rs"): #  or file.endswith(".py")
                    path = os.path.join(root, file)

                    # Checking regexes via parent class 
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
                    # Experimental margins
                    if path.fn_lines[i] and path.fn_lines[i] > context_start:
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

    # For github action
    @staticmethod
    def get_report_string(src_path, target_name):
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

        # If nothing to do abort
        if total_count == 0:
            sys.exit("Didn't find anything todo, sorry.")

        # Overwrite with Header
        desc = ""
        print(f"Found: {len(todo_paths)} files with todo markings.")
        desc += "# Todo check...\n"
        desc += f"- {len(todo_paths)} files to do in {target_name}.\n"
        desc += f"- {total_count} todo expressions in total.\n"
        desc += f"  - {todo_call_count} todo!()'s.\n"
        desc += f"  - {todo_comment_count} TODO's.\n"
        desc += f"  - {fixme_comment_count} FIXME's.\n"
        desc += f"- {total_count / len(todo_paths):.2f} average tdexp/f (todo expression per file).\n"
        desc += "\n"
        desc += f"Total lines of context: {lines_of_context:,d} (Count includes eventual duplicates).\n"

        # Append lines 
        for i, path in enumerate(todo_paths):
            desc += " \n"
            # Path becomes header 
            desc += "### '" + str(path.path).removeprefix("target-repo/") + "'\n"

            # Descriptions become listed paragraph
            for x, y in zip(path.line_numbers, path.descriptions):
                desc += f"- {x:4n}: {y}\n"

        desc += "\n"
        desc += f"Date: {datetime.datetime.now().date()}.\n"

        return desc


# Check existing issues
def find_existing_issue(repo, title, headers):
    try:
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100"
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req) as resp:
            issues = json.load(resp)

        for issue in issues:
            if issue.get("title") == title:
                return issue.get("number")

    except Exception as e:
        print("Failed to check existing issues:", e)

    return None

def main():
    # Parse args of target repo
    target_name = sys.argv[2] if len(sys.argv) > 2 else "unknown target"
    target_path = sys.argv[1] if len(sys.argv) > 1 else "."


    # Get env info
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]  # where the issue should be reported to

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "todo-bot"
    }

    # Create payload
    title = "Todos"

    body = TodoContext.get_report_string(target_path, target_name)
    payload = json.dumps({"title": title, "body": body}).encode("utf-8")

    issue_number = find_existing_issue(repo, title, headers)

    # Post or patch
    # Change to target repo for production
    if issue_number:
        print(f"Updating existing issue #{issue_number}")

        url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
        method = "PATCH"
    else:
        print("Creating new issue")
        url = f"https://api.github.com/repos/{repo}/issues"
    method = "POST"

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Issue {'updated' if issue_number else 'created'}:", resp.status)
            print(resp.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Response:", e.read().decode("utf-8"))

if __name__ == "__main__":
    main()

import os
import sys
import json
import urllib.request

from todo_context import TodoContext
from gethub import get_issues, close_issue, reopen_issue

def get_todo_list_desc():
    src_path = "."
    todo_paths = list(TodoContext.initialize_paths(src_path))
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

def readme_sentinel():
    todo_list_string = get_todo_list_desc()
    if todo_list_string == 1:
        print("Creation of todo list failed")
        return 1

    lines = []
    with open("README.md", mode="r", encoding="utf-8") as f:
        reader = f.readlines()
        lines = [line for line in reader]
    
    # Remember last line and increment it a priori
    last_line = int(lines[-1].strip()) + 1

    # Match sentinel index
    todo_sentinel_start = "# Todo-section"
    matches = [(i, line) for i, line in enumerate(lines) if line.startswith(todo_sentinel_start)]

    if len(matches) != 1:
        print("Resolving sentinel header failed")
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

def create_todo_list_issue():
    # Get env info (self targeting)
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
    body = get_todo_list_desc()
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
        return 1
    else:
        return 0

def legacy_main():
    print(get_todo_list_desc())
    print(f"readme_sentinel exit code: {readme_sentinel()}")
    print(create_todo_list_issue())

def main():
    desc = get_todo_list_desc()
    if desc == 1:
        print("Exit on error, found nothing to do")
        sys.exit()
    else:
        print(desc)

    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    issues = get_issues(repo, token)
    for issue in issues:
        print(issue)
        if issue["title"] == "Todos":
            if issue["state"] == "open":
                print(f"Update todo list issue #{issue["number"]}")
                update_issue(repo, token, issue["number"], fields={"body": desc})

            elif issue["state"] == "closed":
                print(f"Reopen and update todo list issue #{issue["number"]}")
                update_issue(repo, token, issue["number"], fields={"state": "open", "body": desc})

    # todo!("Add more inline comments.")
    # reopen_issue(repo, token, 1)
    # close_issue(repo, token, 1)

if __name__ == "__main__":
    main()

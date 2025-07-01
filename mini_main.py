import sys
import os
import json
import urllib.request

from todo_module import TodoContext

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

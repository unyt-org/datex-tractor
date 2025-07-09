import json
import urllib.request

API_URL = "https://api.github.com"

def _make_request(url, method="GET", token=None, data=None):
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "todo-bot"
    }

    if data is not None:
        data = json.dumps(data).encode("utf-8")
        # headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, method=method, headers=headers, data=data)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("Error response body:", e.read().decode())

def get_issues(repo, token):
    url = f"{API_URL}/repos/{repo}/issues?state=all"
    raw_issues = _make_request(url, token=token)
    issues = []
    for issue in raw_issues:
        if "pull_request" not in issue: # Exclude PR's?
            issues.append({
                "number": issue["number"],
                "state": issue["state"],
                "title": issue["title"],
                "body": issue["body"],
            })
    return issues

def create_issue(repo, token, title, body=""):
    url = f"{API_URL}/repos/{repo}/issues"
    data = {"title": title, "body": body}
    return _make_request(url, method="POST", token=token, data=data)
    
def update_issue(repo, token, number, fields):
    """
    Example fields: {"title":"New title", "body": "Updated body"}
    """
    url = f"{API_URL}/repos/{repo}/issues/{number}"
    return _make_request(url, method="PATCH", token=token, data=fields)

def close_issue(repo, token, number):
    return update_issue(repo, token, number, {"state": "closed"})

def reopen_issue(repo, token, number):
    return update_issue(repo, token, number, {"state": "open"})

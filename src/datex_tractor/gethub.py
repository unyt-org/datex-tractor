import json
import urllib.request
import time

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

    req = urllib.request.Request(
        url,
        method=method,
        headers=headers,
        data=data
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("Error response body:", e.read().decode())


def get_issues(repo, token, per_page=100):
    issues = []
    page = 1

    while True:
        url = f"{API_URL}/repos/{repo}/issues?state=all&per_page={per_page}&page={page}"
        time.sleep(2)
        raw_issues = _make_request(url, token=token)
        if not raw_issues:
            break

        for issue in raw_issues:
            issues.append({
                "number": issue["number"],
                "state": issue["state"],
                "title": issue["title"],
                "body": issue["body"],
                "labels": [label["name"] for label in issue["labels"]],
            })
        page += 1
    return issues


def create_issue(repo, token, title, body="", labels=["placeholder"]):
    url = f"{API_URL}/repos/{repo}/issues"
    data = {
        "title": title,
        "body": body,
        "labels": labels,
    }
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


def get_discussions(repo, token, per_page=100):
    discussions = []
    page = 1

    while True:
        url = f"{API_URL}/repos/{repo}/discussions?state=all&per_page={per_page}&page={page}"
        time.sleep(2)
        raw_discussions = _make_request(url, token=token)
        if not raw_discussions:
            break

        for discussion in raw_discussions:
            discussions.append({
                "number": discussion["number"],
                "state": discussion["state"],
                "title": discussion["title"],
                "body": discussion["body"],
                "labels": [label["name"] for label in discussion["labels"]],
            })
        page += 1
    return discussions

import os
import csv
import json
import urllib.request

def get_all_runs(owner, repo, token, per_page=100):
    all_runs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page={per_page}&page={page}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "todo-bot"
        }


        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as res:
            data = json.load(res)
            runs = data.get("workflow_runs", [])
            if not runs:
                break
            all_runs.extend(runs)
            page += 1

    return all_runs

def export_csv(runs, filename="workflow_data.csv"):
    fields = ["id", "name", "status", "conclusion", "event", "created_at", "updated_at", "run_attempt", "run_number"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for run in runs:
            writer.writerow({field: run.get(field) for field in fields})

if __name__ == "__main__":
    owner = "unyt-org"
    repo = "datex-core"
    token = os.environ["GITHUB_TOKEN"]

    runs = get_all_runs(owner, repo, token)
    print(f"Fetched {len(runs)} runs.")
    export_csv(runs)
    print("Exported as csv")

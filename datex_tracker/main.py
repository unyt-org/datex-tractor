import os
import csv
import json
import urllib.request

tmp_path = "datex_tracker/tmp/"


def fetch_all_runs(owner, repo, token, per_page=100):
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


def write_to_csv(runs, filename=str(tmp_path + "workflow_data.csv")):
    fields = [
        "id",
        "name",
        "status",
        "conclusion",
        "event",
        "created_at",
        "updated_at",
        "run_attempt",
        "run_number"
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for run in runs:
            writer.writerow({field: run.get(field) for field in fields})


def write_plots():
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(tmp_path + "workflow_data.csv").astype(
        {
            "name": "category",
            "status": "category",
            "conclusion": "category",
            "event": "category",
        }
    )

    print(f"{len(df)} Workflows in file after reading.")

    # Preprocessing
    df["name"] = df["name"].str.removeprefix(".github/workflows/").str.removesuffix(".yml").astype("category")
    df[ ["created_day", "created_time"] ] = df["created_at"].str.split("T", expand=True)
    df[ ["updated_day", "updated_time"] ] = df["updated_at"].str.split("T", expand=True)
    df["created_time"] = df["created_time"].str.removesuffix("Z")
    df["updated_time"] = df["updated_time"].str.removesuffix("Z")
    df["created_dtime"] = pd.to_datetime(df["created_day"] + " " + df["created_time"])
    df["updated_dtime"] = pd.to_datetime(df["updated_day"] + " " + df["updated_time"])
    df = df.drop(["created_at", "updated_at", "created_day", "created_time", "updated_day", "updated_time"], axis=1)

    df["runtime"] = df["updated_dtime"] - df["created_dtime"]
    df["runtime"] = df["runtime"].dt.total_seconds()

    # Overlapping Histograms to compare airtime vs. elapsed time
    plt.figure(
        figsize=(6, 4),
        facecolor="whitesmoke",
        layout="constrained"
    )

    plt.hist(df["created_dtime"].dt.dayofweek, bins=7, alpha=0.5, label="Creation", color="green", edgecolor="black")
    plt.hist(df["updated_dtime"].dt.dayofweek, bins=7, alpha=0.5, label="Update", color="blue", edgecolor="black")

    plt.title("Creation and update events of workflows")
    plt.xlabel("Day of the week")
    plt.ylabel("Frequency")
    plt.legend(loc="upper right")

    # save
    plt.savefig(tmp_path + "out0.png")

    # Overlapping Histograms to compare airtime vs. elapsed time
    plt.figure(
        figsize=(12, 6),
        facecolor="whitesmoke",
        layout="constrained"
    )

    plt.hist(df["created_dtime"].dt.hour, bins=24, alpha=0.5, label="Creation", color="green", edgecolor="black")
    plt.hist(df["updated_dtime"].dt.hour, bins=24, alpha=0.5, label="Update", color="blue", edgecolor="black")

    plt.title("Creation and update events of workflows")
    plt.xlabel("Hours of the day")
    plt.ylabel("Frequency")
    plt.legend(loc="upper right")

    plt.savefig(tmp_path + "out1.png")

    df["creation_date"] = df["created_dtime"].dt.date
    counts = df.groupby("creation_date").size()

    plt.figure(
        figsize=(12, 6),
        facecolor="whitesmoke",
        layout="constrained"
    )
    counts.plot(kind="line", marker="o")
    plt.grid(True)

    # Adding titles and labels
    plt.title("Runs per day over time")
    plt.ylabel("Number of runs")

    plt.savefig(tmp_path + "out2.png")

    plt.figure(
        figsize=(12, 6),
        facecolor="whitesmoke",
        layout="constrained"
    )

    # Limiting runtime
    temp_df = df.loc[df["runtime"] <= 2000]
    sns.scatterplot(
        x="created_dtime",
        y="runtime",
        data=temp_df.loc[temp_df["created_dtime"] >= "2025-05-01"],
        alpha=0.8,
        size="runtime",
        hue="name"
    )

    plt.title("Runtimes")
    plt.xlabel("Datetime")
    plt.ylabel("Runtime [sec]")

    plt.axhline(0, color="0", linestyle="--")  # Reference line for x-axis

    plt.grid(True)
    plt.savefig(tmp_path + "out2.png")


def main():
    owner = "unyt-org"
    repo = "datex-core"
    token = os.environ["GITHUB_TOKEN"]

    runs = fetch_all_runs(owner, repo, token)
    print(f"Fetched {len(runs)} runs.")
    write_to_csv(runs)
    print("Exported data as csv")
    write_plots()
    print("Exported plots as png")


if __name__ == "__main__":
    main()

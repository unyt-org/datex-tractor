#!/bin/bash
set -e
echo "Datex-tractor Start."

echo "Python check..."
python --version
pip list

echo "Running jector.py..."
if [[ "$#" == 2 ]]; then
    python "${GITHUB_ACTION_PATH}/datex_tractor/datex_jector.py" "remove"
else
    python "${GITHUB_ACTION_PATH}/datex_tractor/datex_jector.py"
fi

git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

git add .

echo "Commit changes - if any."
git commit --allow-empty -m "todo-extractor auto-commit"
echo "Push to origin."
git push

LAST_COMMIT=$(git rev-parse HEAD)
echo "Commit: $LAST_COMMIT"

echo "Run tractor.py..."
if [[ "$#" == 1 ]]; then
    python "${GITHUB_ACTION_PATH}/datex_tractor/datex_tractor.py" $LAST_COMMIT $1
elif [[ "$#" != 2 ]]; then
    python "${GITHUB_ACTION_PATH}/datex_tractor/datex_tractor.py" $LAST_COMMIT
else
    echo "Removed ids - nothing to do..."
fi

echo "Datex-tractor End."

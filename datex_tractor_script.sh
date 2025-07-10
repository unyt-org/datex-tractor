#!/bin/bash
set -e
echo "Datex-tractor Start."

if [[ "$#" != 0 ]]; then
	echo "No CLA please."
	exit 1
fi
echo "Python check..."
python --version
pip list

echo "Running jector.py..."
python "${GITHUB_ACTION_PATH}/datex_jector.py"

if [[ "$?" != 0 ]]; then
	echo "datex_jector.py execution failed."
	exit 1
fi

git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

git add .

if git diff --cached --quiet; then
	echo "No changes to commit."
	exit 0
else
	echo "Commit changes."
	git commit -m "insert issues and auto update readme"
	echo "Push to origin."
	git push
fi

LAST_COMMIT=$(git rev-parse HEAD)
echo "Commit: $LAST_COMMIT"

echo "Run tractor.py..."
python "${GITHUB_ACTION_PATH}/datex_tractor.py" $LAST_COMMIT

echo "Datex-tractor End."

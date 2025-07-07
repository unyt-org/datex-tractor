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

echo "Running datex_tractor.py..."
python .github/workflows/todo-extractor/datex_tractor.py

if [[ "$?" != 0 ]]; then
	echo "datex_tractor.py execution failed."
	exit 1
fi

git config --global user.name "github-actions"
git config --global user.email "github-actions@github.com"

git add README.md

if git diff --cached --quiet; then
	echo "No changes to commit."
	exit 0
else
	echo "Commit readme."
	git commit -m "auto update readme"
	echo "Push to origin."
	git push
fi

echo "Datex-tractor End."

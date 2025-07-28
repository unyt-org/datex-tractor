#!/bin/bash

echo "Fetching version branches (release/*)..."
all_branches=$(git ls-remote --heads origin "release/*" | cut -d/ -f3- | grep -E '^release/[^/]+$' | sort -V)

latest=$(echo "$all_branches" | tail -n1)
current="${GITHUB_REF#refs/heads/}"

if [ "$current" != "$latest" ]; then
	echo "Not on latest branch, abort."
	exit 1
fi

echo "On latest branch, continue workflow."

exit 0 

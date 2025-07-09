#!/bin/bash

echo "Fetching version branches..."
all_branches=$(git ls-remote --heads origin "v/*" | cut -d/ -f3- | sort -V)

latest=$(echo "$all_branches" | tail -n1)
current="${GITHUB_REF#refs/heads/}"

if [ "$current" != "$latest" ]; then
	echo "Not latest, abort."
	exit 1
fi

echo "On latest branch, continue workflow."

exit 0 

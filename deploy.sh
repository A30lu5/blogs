#!/usr/bin/env bash
# Push HTML files to gh-pages automatically.

# Fill this out with the correct org/repo
ORG=A30lu5
REPO=A30lu5.github.io
# This probably should match an email for one of your users.
EMAIL=df11a@aeolus.group

set -e

git remote add gh-token "https://${GH_TOKEN}@github.com/$ORG/$REPO.git";
git fetch gh-token && git fetch gh-token gh-pages:gh-pages;

# Update git configuration so I can push.
if [ "$1" != "dry" ]; then
    # Update git config.
    git config user.name "Travis Builder"
    git config user.email "$EMAIL"
fi

mkdocs gh-deploy -v --clean --remote-name gh-token;
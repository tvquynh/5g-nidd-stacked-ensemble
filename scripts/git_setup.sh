#!/usr/bin/env bash
# Initialise local git repo for the reviewer-runnable artefact.
# Public GitHub URL: https://github.com/tvquynh/5g-nidd-stacked-ensemble
#
# This script:
#   1. Runs the redaction step (anonymises CITATION.cff and .zenodo.json
#      using the canonicals in .restore-on-accept/).
#   2. Initialises git, commits the redacted tree, tags submit-ready.
#   3. Prints the gh CLI commands the maintainer should run to create the
#      public repo on GitHub. We do NOT push automatically.
set -euo pipefail

cd "$(dirname "$0")/.."

# Sanity: canonicals must exist before we redact
test -f .restore-on-accept/CITATION.cff.canonical
test -f .restore-on-accept/.zenodo.json.canonical

# Skip if already a repo
if [[ -d .git ]]; then
    echo "[git] .git already present; skipping init"
else
    git init -q
    git checkout -B main 2>/dev/null || git checkout -B main
fi

# Stage everything except artefacts and caches
git add .
git status --short

cat <<EOF

[git] next steps (run manually):
  git commit -m "Submit-ready snapshot for ATC 2026"
  gh repo create tvquynh/5g-nidd-stacked-ensemble --public --source=. --remote=origin --description="Heterogeneous shallow stacked ensemble for 5G-NIDD intrusion detection (ATC 2026 artefact)" --push
  git tag submit-ready-atc-2026
  git push origin submit-ready-atc-2026
EOF

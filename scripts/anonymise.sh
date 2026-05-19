#!/usr/bin/env bash
# Replace author metadata in CITATION.cff and .zenodo.json with anonymised
# placeholders for peer review. Canonical originals stay in
# .restore-on-accept/ until accepted.
set -euo pipefail

cd "$(dirname "$0")/.."

# CITATION.cff (anonymised)
cat > CITATION.cff <<'EOF'
cff-version: 1.2.0
title: "Lightweight Stacked Ensemble for AI-Enabled 5G Network Intrusion Detection: A Latency-Accuracy Pareto Analysis"
message: "If you use this software, please cite both the article and the artefact."
authors:
  - family-names: Anonymised
    given-names: Pending peer review
type: software
license: MIT
repository-code: "https://github.com/tvquynh/5g-nidd-stacked-ensemble"
abstract: >-
  Reviewer-runnable artefact for the ATC 2026 submission. Provides a
  heterogeneous shallow stacked ensemble (LightGBM + XGBoost + MLP -> logistic
  regression meta-learner) for multi-class 5G network intrusion detection on
  the public 5G-NIDD dataset, together with a latency-accuracy Pareto
  analysis and a deployment recommendation table.
EOF

# .zenodo.json (anonymised)
cat > .zenodo.json <<'EOF'
{
  "title": "Lightweight Stacked Ensemble for AI-Enabled 5G Network Intrusion Detection: A Latency-Accuracy Pareto Analysis (ATC 2026 artefact)",
  "description": "Reviewer-runnable code, configurations, and aggregation pipeline for the ATC 2026 submission on a heterogeneous shallow stacked ensemble for 5G-NIDD multi-class intrusion detection.",
  "creators": [
    {
      "name": "Anonymised, Pending peer review",
      "affiliation": "Pending peer review"
    }
  ],
  "access_right": "open",
  "license": "MIT",
  "upload_type": "software",
  "keywords": [
    "5G",
    "network intrusion detection",
    "stacked ensemble",
    "latency-accuracy tradeoff",
    "5G-NIDD",
    "lightweight ML"
  ]
}
EOF

echo "[anonymise] CITATION.cff and .zenodo.json reset to anonymised forms"
echo "[anonymise] canonical forms remain in .restore-on-accept/"

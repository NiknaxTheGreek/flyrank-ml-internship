from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HTML = DOCS / "index.html"

errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

require(HTML.exists(), "docs/index.html is missing")
if HTML.exists():
    text = HTML.read_text(encoding="utf-8")
else:
    text = ""

# Canonical paper structure.
section_ids = [
    "abstract",
    "introduction",
    "data",
    "methodology",
    "results",
    "limitations",
    "recommendations",
    "reproducibility",
    "acknowledgments",
]
for sid in section_ids:
    require(f'id="{sid}"' in text, f"missing canonical section: {sid}")

# Required data credit and navigation.
require("Built on the FlyRank ML Internship dataset" in text, "exact FlyRank data-credit phrase missing")
require('href="https://flyrank.ai"' in text, "FlyRank data-credit link missing")
require("https://github.com/NiknaxTheGreek/flyrank-ml-internship" in text, "repository link missing")

# Required public figure assets.
for name in [
    "capstone_methodology_design.png",
    "capstone_model_vs_baseline.png",
    "capstone_action_playbook.png",
]:
    require((DOCS / "assets" / name).exists(), f"missing public figure asset: {name}")
    require(f'assets/{name}' in text, f"paper does not embed required figure: {name}")

# Canonical five-feature contract.
for feature in [
    "aggregate_ctr",
    "median_position",
    "position_slope_per_day",
    "position_iqr",
    "content_age_days",
]:
    require(feature in text, f"missing active feature in paper: {feature}")

# Core numerical claims must remain aligned with verified artifacts.
for snippet in [
    "2,520",
    "21 pseudonymized clients",
    "1,800 pages from 15 clients",
    "720 pages from 6 unseen clients",
    "0.665",
    "0.806",
    "0.872",
    "0.494",
    "1.379",
    "0.360",
    "0.480",
    "89.76%",
    "18 true future declines and 32 false picks",
]:
    require(snippet in text, f"missing expected verified paper value: {snippet}")

# No stale/invented methodology.
for phrase in [
    "Prediction Strength",
    "Silhouette Score",
    "Calinski-Harabasz",
    "Davies-Bouldin",
    "future_decline_magnitude_30d",
    "future_change_magnitude_30d",
]:
    require(phrase not in text, f"stale methodology language present: {phrase}")

# Public-safety checks.
for phrase in [
    "PASTE-YOUR-DEPLOYED-PAPER-URL-HERE",
    "/home/runner/",
    "localhost",
    "api_key=",
    "token=",
    "password=",
]:
    require(phrase.lower() not in text.lower(), f"unsafe/placeholder content present: {phrase}")

require(re.search(r"client_[0-9a-f]{8,}", text, re.I) is None, "pseudonymized client identifier leaked into public paper")
require(re.search(r"content_[0-9a-f]{8,}", text, re.I) is None, "pseudonymized content identifier leaked into public paper")

# Claim-language sanity.
for phrase in [
    "proves that",
    "guarantees",
    "production-ready",
    "universally generalizes",
]:
    require(phrase.lower() not in text.lower(), f"unsupported claim language present: {phrase}")

# Make the distinction between warehouse scale and modeling population explicit.
require(
    "that number describes warehouse scale, not the number of rows used to train the final models" in text,
    "warehouse-scale vs model-population distinction missing",
)
require(
    "These are not learned unsupervised clusters" in text,
    "grouping-vs-clustering distinction missing",
)

if errors:
    print("PAPER PUBLICATION CHECK: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("PAPER PUBLICATION CHECK: PASS")
print("Canonical sections:", len(section_ids))
print("Public figure assets: 3")
print("FlyRank data credit: present")
print("Private identifier scan: clear")
print("Verified methodology/result contract: present")

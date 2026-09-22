from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = {
    "assignment_2": ROOT / "work/notebooks/w01_research_question.ipynb",
    "assignment_3": ROOT / "work/notebooks/w02_ml_task_framing.ipynb",
    "assignment_4": ROOT / "work/notebooks/w03_data_contract.ipynb",
    "assignment_5": ROOT / "work/notebooks/w04_baseline_score.ipynb",
    "assignment_6": ROOT / "work/notebooks/w05_model.ipynb",
    "assignment_7": ROOT / "work/notebooks/w06_validation_audit.ipynb",
    "assignment_8": ROOT / "work/notebooks/w07_action_playbook.ipynb",
    "assignment_9": ROOT / "work/notebooks/capstone.ipynb",
}

def notebook_source(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        if isinstance(cell.get("source", []), list)
        else str(cell.get("source", ""))
        for cell in payload["cells"]
    )

sources = {name: notebook_source(path) for name, path in NOTEBOOKS.items()}

# Exact legacy formulations that contradict the executed methodology.
forbidden = {
    "formal clustering pipeline": "observed features → clustering → classification + regression → ranking / scoring",
    "clustering metric contract": "Prediction Strength",
    "silhouette metric": "Silhouette Score",
    "calinski metric": "Calinski-Harabasz",
    "davies-bouldin metric": "Davies-Bouldin",
    "fake regression target": "future_decline_magnitude_30d",
    "fake future-change magnitude target": "future_change_magnitude_30d",
    "stale feature-reduction wording": "simple interpretation across clustering, classification, and regression",
    "old task-count wording": "Three standard ML tasks support the ranking",
    "old regression pipeline wording": "future-change magnitude regression",
}

violations = []
joined = "\n".join(sources.values())
for label, phrase in forbidden.items():
    if phrase in joined:
        violations.append(f"{label}: {phrase!r}")

required = {
    "assignment_2": [
        "interpretable grouping or stratification",
        "past feature window → decision point → future outcome window",
    ],
    "assignment_3": [
        "Grouping is a **data-design step, not a target-bearing ML task**",
        "signed future-change regression",
        "future_relative_change_30d",
        "predicted decline risk + severity derived from negative predicted change → review priority",
        "Diagnostic archetypes are assigned after ranking from transparent review signals; they are not learned clusters.",
    ],
    "assignment_4": [
        "simple interpretation across classification, regression, ranking, and later human-review diagnostics",
        "future_impression_change",
    ],
    "assignment_5": [
        "Classification baseline",
        "Regression baseline",
        "Ranking baseline",
        "future_impression_change < 0",
    ],
    "assignment_6": [
        "Target: signed continuous `future_impression_change`.",
        "oof_severity = np.maximum(0.0, -oof_reg_pred)",
        "ranking_score = p_decline^gamma",
    ],
    "assignment_7": [
        "grouped_client_cv",
        "random_page_cv",
        "illegal_target_derived_feature",
    ],
    "assignment_8": [
        "the ranking converts negative predictions into decline severity",
        "research POC / human decision-support only",
        "ranking below the 0.480 rule baseline",
    ],
    "assignment_9": [
        "Grouping is descriptive, not learned clustering",
        "The selected classifier is a **Random Forest classifier**",
        "Six-client stress test",
    ],
}

missing = []
for name, phrases in required.items():
    src = sources[name]
    for phrase in phrases:
        if phrase not in src:
            missing.append(f"{name}: missing {phrase!r}")

if violations or missing:
    if violations:
        print("FORBIDDEN LEGACY LANGUAGE FOUND")
        for item in violations:
            print(" -", item)
    if missing:
        print("REQUIRED METHODOLOGY CONTRACT MISSING")
        for item in missing:
            print(" -", item)
    raise SystemExit(1)

print("METHODOLOGY CONSISTENCY CHECK: PASS")
print("Canonical pipeline:")
print(
    "grouping/stratification -> five-feature reduction -> "
    "classification + signed-change regression -> ranking -> "
    "rule-based diagnostic archetypes -> human review"
)
print("Checked notebooks:", ", ".join(NOTEBOOKS))

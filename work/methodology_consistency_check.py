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
        "below the fixed-rule baseline of **0.480**",
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


# ---------------------------------------------------------------------------
# Cross-artifact numerical / methodological contract
# ---------------------------------------------------------------------------
from math import isclose

def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

split = load_json("work/outputs/baseline_split_manifest.json")
baselines = load_json("work/outputs/multitask_baseline_benchmark.json")
model = load_json("work/outputs/assignment6_model_benchmark.json")
split_audit = load_json("work/outputs/assignment7_split_audit.json")
leakage = load_json("work/outputs/assignment7_leakage_audit.json")
playbook = load_json("work/outputs/assignment8_action_playbook_metrics.json")
paper_export = load_json("work/outputs/assignment8_paper_export.json")

contract_errors = []

def require(condition: bool, message: str):
    if not condition:
        contract_errors.append(message)

def same(a, b, label: str, tol: float = 1e-12):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        require(isclose(float(a), float(b), rel_tol=tol, abs_tol=tol), f"{label}: {a!r} != {b!r}")
    else:
        require(a == b, f"{label}: {a!r} != {b!r}")

expected_features = [
    "aggregate_ctr",
    "median_position",
    "position_slope_per_day",
    "position_iqr",
    "content_age_days",
]

# Frozen population / split contract.
require(split["splitter"] == "GroupShuffleSplit", "splitter must remain GroupShuffleSplit")
require(split["group_field"] == "client_hash_id", "split group must remain client_hash_id")
same(split["test_size"], 0.25, "test_size")
require(split["random_state"] == 42, "random_state must remain 42")
require(split["population_pages"] == 2520, "POC population must remain 2,520 pages")
require(split["population_clients"] == 21, "POC population must remain 21 clients")
require(split["train_pages"] == 1800 and split["test_pages"] == 720, "frozen page split changed")
require(len(split["train_clients"]) == 15 and len(split["test_clients"]) == 6, "frozen client counts changed")
require(split["client_overlap"] == [], "development/stress client overlap must be zero")
require(split["classification_target"] == "future_impression_change < 0", "classification target changed")
require(split["regression_target"] == "future_impression_change", "regression target changed")
require(split["ranking_relevance"] == "future_impression_change < 0", "ranking relevance changed")
require(split["ranking_k"] == 50, "ranking K must remain 50")

for artifact_name, artifact_split in [
    ("Assignment 5 baseline", baselines["split"]),
    ("Assignment 6 model", model["split"]),
]:
    same(artifact_split["test_size"], split["test_size"], f"{artifact_name} test_size")
    require(artifact_split["random_state"] == split["random_state"], f"{artifact_name} random_state mismatch")
    require(artifact_split["train_pages"] == split["train_pages"], f"{artifact_name} train_pages mismatch")
    require(artifact_split["test_pages"] == split["test_pages"], f"{artifact_name} test_pages mismatch")
    require(artifact_split["train_clients"] == len(split["train_clients"]), f"{artifact_name} train_clients mismatch")
    require(artifact_split["test_clients"] == len(split["test_clients"]), f"{artifact_name} test_clients mismatch")

# Exact five-feature contract across modeling, validation, and leakage audit.
require(model["features"] == expected_features, "Assignment 6 feature set changed")
require(split_audit["features"] == expected_features, "Assignment 7 split-audit feature set changed")
require(leakage["active_features"] == expected_features, "Assignment 7 leakage-audit feature set changed")
require(leakage["forbidden_feature_overlap"] == [], "forbidden feature overlap is no longer empty")
require(
    all(row["verdict"] == "PASS" for row in leakage["feature_audit"]),
    "at least one active feature no longer passes the leakage audit",
)
require(
    all(row["available_by"] == "2026-03-31" for row in leakage["feature_audit"]),
    "at least one feature is not available by the decision cutoff",
)

# Assignment 5 frozen baselines must be exactly the baselines used by Assignment 6.
same(baselines["classification"]["roc_auc"], model["classification"]["baseline"]["roc_auc"], "classification baseline AUC")
same(baselines["classification"]["precision"], model["classification"]["baseline"]["precision"], "classification baseline precision")
same(baselines["classification"]["recall"], model["classification"]["baseline"]["recall"], "classification baseline recall")
same(baselines["classification"]["f1"], model["classification"]["baseline"]["f1"], "classification baseline F1")

for metric in ["rmse", "mae", "median_absolute_error", "r2"]:
    same(baselines["regression"][metric], model["regression"]["baseline"][metric], f"regression baseline {metric}")

for metric in ["precision_at_50", "recall_at_50", "lift_at_50", "ndcg_at_50"]:
    same(baselines["ranking"][metric], model["ranking"]["baseline"][metric], f"ranking baseline {metric}")

# Assignment 6 grouped-development values must match Assignment 7's grouped re-run.
grouped = next(row for row in split_audit["summary"] if row["split"] == "grouped_client_cv")
random_page = next(row for row in split_audit["summary"] if row["split"] == "random_page_cv")
require(grouped["mean_client_overlap"] == 0, "grouped CV client overlap must remain zero")
require(random_page["mean_client_overlap"] == 15, "random-page audit no longer shows full client overlap")
same(grouped["classification_roc_auc"], model["classification"]["model"]["grouped_cv_roc_auc"], "grouped classification AUC")
same(grouped["regression_rmse"], model["regression"]["model"]["grouped_cv_rmse"], "grouped regression RMSE")
same(grouped["ranking_precision_at_50"], model["ranking"]["model"]["grouped_cv_precision_at_50"], "grouped ranking P@50")

# Ranking blend semantics.
require(model["ranking"]["model"]["gamma"] == 2, "ranking gamma changed")
require(model["ranking"]["model"]["lambda"] == 1, "ranking lambda changed")
require(model["ranking"]["k"] == 50, "Assignment 6 ranking K changed")
require(
    model["ranking"]["formula"] == "p_decline^gamma * (1 + lambda * normalized_predicted_decline_severity)",
    "ranking formula changed",
)
same(
    playbook["queue_definition"]["severity_scale"],
    model["ranking"]["model"]["severity_scale_from_training_oof"],
    "severity scaling",
)
require(playbook["queue_definition"]["gamma"] == model["ranking"]["model"]["gamma"], "playbook gamma mismatch")
require(playbook["queue_definition"]["lambda"] == model["ranking"]["model"]["lambda"], "playbook lambda mismatch")
require(playbook["queue_definition"]["queue_size"] == 50, "playbook queue size changed")

# Assignment 8 must carry exactly the final Assignment 6/7 evidence.
dev = playbook["intended_use_and_limits"]["development_evidence"]
stress = playbook["intended_use_and_limits"]["stress_test_evidence"]
same(dev["classification_roc_auc"], model["classification"]["model"]["grouped_cv_roc_auc"], "playbook development classification")
same(dev["regression_rmse"], model["regression"]["model"]["grouped_cv_rmse"], "playbook development regression")
same(dev["ranking_precision_at_50"], model["ranking"]["model"]["grouped_cv_precision_at_50"], "playbook development ranking")

same(stress["classification_roc_auc"], model["classification"]["model"]["roc_auc"], "stress classification AUC")
same(stress["classification_baseline_roc_auc"], model["classification"]["baseline"]["roc_auc"], "stress classification baseline")
same(stress["regression_rmse"], model["regression"]["model"]["rmse"], "stress regression RMSE")
same(stress["regression_baseline_rmse"], model["regression"]["baseline"]["rmse"], "stress regression baseline")
same(stress["ranking_precision_at_50"], model["ranking"]["model"]["precision_at_50"], "stress ranking P@50")
same(stress["ranking_baseline_precision_at_50"], model["ranking"]["baseline"]["precision_at_50"], "stress ranking baseline")

# Observability / leakage evidence must propagate unchanged into the playbook.
obs7 = leakage["population_selection"]
obs8 = playbook["intended_use_and_limits"]["observability"]
for key in [
    "march_feature_eligible_pages",
    "march_feature_eligible_clients",
    "april_observable_pages",
    "april_observable_clients",
    "march_pages_excluded_for_insufficient_april_observability",
    "pct_march_pages_retained_for_observable_outcome",
]:
    same(obs7[key], obs8[key], f"observability {key}")

# Queue composition and paper export must reconcile exactly.
require(sum(playbook["archetype_counts"].values()) == 50, "archetype counts must sum to 50")
require(set(playbook["archetype_counts"]) == set(playbook["action_map"]), "every archetype must have exactly one action mapping")
require(sum(paper_export["queue"]["review_priority_counts"].values()) == 50, "priority bands must sum to 50")
require(paper_export["queue"]["archetype_counts"] == playbook["archetype_counts"], "paper-export archetypes differ from playbook")
require(paper_export["queue"]["reason_code_counts"] == playbook["reason_code_counts"], "paper-export reasons differ from playbook")
same(
    paper_export["ranking_evidence"]["grouped_development"]["learned_precision_at_50"],
    dev["ranking_precision_at_50"],
    "paper-export grouped ranking",
)
same(
    paper_export["ranking_evidence"]["six_client_stress_test"]["learned_precision_at_50"],
    stress["ranking_precision_at_50"],
    "paper-export stress ranking",
)
same(
    paper_export["ranking_evidence"]["six_client_stress_test"]["baseline_precision_at_50"],
    stress["ranking_baseline_precision_at_50"],
    "paper-export stress ranking baseline",
)

# Guardrails are part of the methodology contract, not optional prose.
require(playbook["guardrails"]["human_review_required_for_every_row"] is True, "human review guardrail removed")
require(playbook["guardrails"]["automatic_edit_or_publish_allowed"] is False, "automatic action guardrail weakened")
require(playbook["guardrails"]["reason_codes_are_causal_claims"] is False, "reason codes incorrectly made causal")
require(playbook["guardrails"]["future_outcome_written_to_queue"] is False, "future outcome leaked into queue")
require(
    playbook["monitoring_and_retrain_policy"]["current_trigger_state"]["classification_below_frozen_baseline"] is True,
    "classification stress-test failure must remain visible",
)
require(
    playbook["monitoring_and_retrain_policy"]["current_trigger_state"]["ranking_below_frozen_baseline"] is True,
    "ranking stress-test failure must remain visible",
)
require(
    playbook["monitoring_and_retrain_policy"]["current_trigger_state"]["regression_not_better_than_frozen_baseline"] is False,
    "regression stress-test improvement state changed",
)

if contract_errors:
    print("CROSS-ARTIFACT CONTRACT FAIL")
    for item in contract_errors:
        print(" -", item)
    raise SystemExit(1)

print("CROSS-ARTIFACT CONTRACT: PASS")
print("Population/split/features/targets/baselines/results/playbook are numerically consistent.")

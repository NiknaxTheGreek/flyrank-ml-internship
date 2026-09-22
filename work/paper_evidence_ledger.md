# Assignment 9 — Verified paper evidence ledger

This file is the authoritative evidence ledger for the capstone paper. It consolidates the committed Assignments 2–8 and separates exploratory values, development-CV values, and final six-client stress-test values so the public paper does not accidentally overclaim.

## 1. Research question and decision

**Research question**

Can observable search, traffic, engagement, freshness and performance signals identify meaningful content opportunities or risks and help determine **which pages should be reviewed first, why they deserve attention, and what type of action should be considered?**

**Decision supported**

Allocate limited human content/SEO review time across a large inventory. The intended product is a ranked **human-review queue**, not an automatic editing or publishing system.

**Unit of analysis**

One pseudonymized content page at a defined decision point, using only information available by that point.

Primary source:
- `work/notebooks/w01_research_question.ipynb`

## 2. Data release and scale

Warehouse release:
- Hugging Face dataset: `FlyRank/internship-warehouse`
- build id: `flyrank_pseudonymized_warehouse_release_v20260703`
- source: `central_data_warehouse`
- export date: 2026-07-03
- daily-fact freshness cutoff: 2026-06-30
- earliest daily-fact date: 2025-01-27
- history is an unbalanced panel.

Release table sizes documented by the repository:
- `dim_clients`: 104 rows
- `dim_content`: 519,606 rows
- `fact_content_daily_performance`: **78,835,655 rows**
- `fact_content_query_90d`: 2,414,248 rows

**Allowed public-scale claim:** the project was built against a pseudonymized warehouse release containing about **78.8 million daily content-performance rows**.

**Do not say:** “the model was trained on 79 million rows.” The final proof-of-concept modeling population is much smaller and is documented below.

Starter dataset used for early framing only:
- 30,000 rows
- 44 columns
- 32 pseudonymized clients
- one row per content item.

Primary sources:
- `docs/ml-intern-dataset-and-lane-guide.md`
- `work/notebooks/w01_research_question.ipynb`

## 3. Final time contract

Decision cutoff:
- **2026-03-31**

Feature window:
- **2026-03-01 through 2026-03-31**

Outcome window:
- **2026-04-01 through 2026-04-30**

Usability rule:
- at least 20 usable GSC days in March;
- at least 20 usable GSC days in April for observable future outcome.

One source fact row means:
- `report_date × client_hash_id × content_hash_id`

Tables actually used:
- `fact_content_daily_performance` for March predictors and April outcome observations;
- `dim_content` for page creation date / content age;
- `dim_clients` for context only.

Deliberately excluded from the active model contract:
- absolute March exposure as a model predictor (used for sampling strata only);
- raw identifiers as predictive features;
- GA4 features because coverage was too sparse;
- `fact_content_query_90d` because its fixed window can overlap the future;
- mutable current-state fields whose value at the March decision point could not be guaranteed.

Primary source:
- `work/notebooks/w03_data_contract.ipynb`

## 4. Final proof-of-concept population

Balanced POC:
- **2,520 pages**
- **21 clients**
- 840 Low-exposure pages
- 840 Medium-exposure pages
- 840 High-exposure pages
- equivalently: 21 clients × 40 pages per tier × 3 tiers.

The sample is deliberately balanced to prevent large clients or high-exposure pages from dominating.

**Important limitation:** prevalence, exposure mix, calibration, and aggregate rates from this 2,520-page sample must **not** be presented as natural FlyRank population prevalence.

Broader observability audit:
- March feature-eligible pages: 106,546
- March feature-eligible clients: 37
- April-observable pages: 95,633
- April-observable clients: 37
- March pages excluded for insufficient April observability: 10,913
- retained for observable outcome: **89.7575%**

Primary sources:
- `work/notebooks/w03_data_contract.ipynb`
- `work/outputs/assignment7_leakage_audit.json`

## 5. Target definitions

Continuous outcome:

`future_impression_change = (April avg impressions/day - March avg impressions/day) / March avg impressions/day`

This uses average impressions per usable GSC day to avoid comparing raw 31-day and 30-day totals.

Classification target:
- `future_impression_change < 0`
- 1 = future decline
- 0 = no future decline

Regression target:
- `future_impression_change`

Ranking relevance:
- `future_impression_change < 0`

Ranking depth:
- **K = 50**

The April target is constructed only **after** the March feature set is locked.

Primary sources:
- `work/notebooks/w03_data_contract.ipynb`
- `work/outputs/baseline_split_manifest.json`

## 6. Final five features

Exactly five active March-only features:

1. `aggregate_ctr`
2. `median_position`
3. `position_slope_per_day`
4. `position_iqr`
5. `content_age_days`

All 2,520 selected pages have complete values for the final five.

Feature interpretation:
- `aggregate_ctr`: March click efficiency;
- `median_position`: typical March search position;
- `position_slope_per_day`: March rank movement;
- `position_iqr`: March rank stability/volatility;
- `content_age_days`: lifecycle age measured at 2026-03-31.

Assignment 7 leakage audit verdict:
- all five features PASS;
- forbidden feature overlap: none;
- all are available by 2026-03-31;
- none is label-derived;
- none overlaps the future outcome window.

Primary sources:
- `work/notebooks/w03_data_contract.ipynb`
- `work/outputs/assignment7_leakage_audit.json`

## 7. Leakage demonstration

Assignment 4 deliberately added one illegal feature:
- `observed_future_change_copy`, an exact copy of the future target.

Same grouped holdout linear-regression demonstration:
- honest grouped holdout R²: **-0.141729**
- leaked grouped holdout R²: **1.000000**

The illegal feature was then deleted.

Assignment 7 repeated the principle on classification:
- legal grouped-CV ROC-AUC: **0.665025**
- illegal target-derived feature grouped-CV ROC-AUC: **1.000000**
- jump: **0.334975**

Use this as evidence that future-derived fields can make a weak model look artificially perfect.

Primary sources:
- `work/notebooks/w03_data_contract.ipynb`
- `work/outputs/assignment7_leakage_audit.json`

## 8. Frozen train/stress-test split

Splitter:
- `GroupShuffleSplit`
- group field: `client_hash_id`
- test size: 0.25
- random state: 42

Development/training side:
- 1,800 pages
- 15 clients

Held-out six-client stress test:
- 720 pages
- 6 clients

Client overlap:
- **0**

Held-out decline prevalence:
- **0.436111**

This frozen split is the authoritative same-split comparison for the final stress test.

Primary source:
- `work/outputs/baseline_split_manifest.json`

## 9. Metrics contract

Classification:
- primary: ROC-AUC
- secondary: Precision, Recall, F1

Regression:
- primary: RMSE
- secondary: MAE, Median Absolute Error, R²

Ranking:
- primary project metric: Precision@50
- secondary: Recall@50, Lift@50, NDCG@50

Clustering was part of Assignment 3 framing, but there is no clustering benchmark in the final Assignment 6 model artifact. **Do not invent or report a final clustering result.**

Primary sources:
- `work/notebooks/w02_ml_task_framing.ipynb`
- `work/outputs/assignment6_model_benchmark.json`

## 10. Authoritative baselines on the frozen six-client stress test

### Classification baseline
Training-prior probability / majority-class baseline:
- ROC-AUC: **0.5000**
- Precision: **0.4361**
- Recall: **1.0000**
- F1: **0.6074**

### Regression baseline
Training-mean future-change baseline:
- RMSE: **1.4311**
- MAE: **0.8125**
- Median AE: **0.3884**
- R²: **-0.2394**

### Ranking baseline
Frozen low-CTR-for-position rule with staleness boost:
- Precision@50: **0.4800**
- Recall@50: **0.07643**
- Lift@50: **1.10064**
- NDCG@50: **0.48543**

Primary source:
- `work/outputs/multitask_baseline_benchmark.json`

### Number that must NOT be substituted for the same-split ranking baseline

`work/outputs/baseline_metrics.json` reports Precision@50 = **0.92** for an exploratory whole-population rule evaluation. This is not the six-client frozen stress-test comparison and must not be used in the paper's model-vs-baseline result table.

## 11. Development validation — grouped CV on the 15 development clients

Validation:
- `GroupKFold(n_splits=5)`
- performed only on the 15 development clients.

### Classification
Selected model:
- RandomForestClassifier
- grouped-CV ROC-AUC: **0.6650**
- grouped-CV baseline ROC-AUC: **0.5000**

### Regression
Selected model:
- RandomForestRegressor
- grouped-CV RMSE: **0.8063**
- grouped-CV baseline RMSE: **0.8515**

### Ranking
Selected score:
- `p_decline^gamma * (1 + lambda * normalized_predicted_decline_severity)`
- gamma = 2
- lambda = 1
- grouped-CV Precision@50: **0.8720**
- grouped-CV frozen-rule baseline Precision@50: **0.8240**

These are **development-validation results**, not final unseen-client results.

Primary source:
- `work/outputs/assignment6_model_benchmark.json`

## 12. Final six-client stress-test results

This is the most important result table for honest framing because these six clients were kept outside model selection.

| Task | Metric | Frozen baseline | Learned model | Stress-test reading |
|---|---:|---:|---:|---|
| Classification | ROC-AUC | **0.5000** | **0.4942** | learned classifier did not beat baseline |
| Regression | RMSE | **1.4311** | **1.3791** | learned regressor was slightly better on RMSE |
| Ranking | Precision@50 | **0.4800** | **0.3600** | learned ranking underperformed the rule baseline |

Additional learned stress-test values:

Classification:
- Precision: 0.4589
- Recall: 0.8185
- F1: 0.5881

Regression:
- MAE: 0.8540
- Median AE: 0.5123
- R²: -0.1508

Ranking:
- Recall@50: 0.05732
- Lift@50: 0.82548
- NDCG@50: 0.45708
- true declines in learned top 50: **18**
- false picks in learned top 50: **32**
- declines missed outside top 50: **296**

Primary sources:
- `work/outputs/assignment6_model_benchmark.json`
- `work/outputs/assignment6_error_audit.json`

## 13. Assignment 7 split audit — why the stress-test failure matters

Same frozen model families were compared under naive random-page CV and client-grouped CV on the 1,800-page development population.

Mean results:

| Metric | Random-page CV | Client-grouped CV |
|---|---:|---:|
| Classification ROC-AUC | 0.7247 | 0.6650 |
| Regression RMSE | 0.8186 | 0.8063 |
| Ranking Precision@50 | 0.9480 | 0.8720 |
| Mean client overlap | 15 | 0 |

Interpretation:
- random-page validation lets the same clients appear on both sides of each fold and produces a more optimistic classification/ranking picture;
- grouping by client removes that overlap;
- even grouped development CV was still not sufficient to guarantee transfer to the six held-out clients.

This supports an **unseen-client generalization limitation**, not a claim that the method is useless.

Primary source:
- `work/outputs/assignment7_split_audit.json`

## 14. Signal evidence for the action playbook

CTR relative to position:
- verdict: **CONFIRMED** as a diagnostic signal
- bottom-quartile observed decline rate: **0.7466**
- top-quartile observed decline rate: **0.5233**
- safe interpretation: diagnostic review cue; **not** an intervention effect.

Content age:
- verdict: **MIXED**
- youngest bucket observed decline rate: **0.5572**
- oldest bucket observed decline rate: **0.8496**
- middle bucket rates: 0.7208 and 0.6581
- safe interpretation: freshness-review cue; **not** proof of monotonic decay or benefit from refreshing.

Primary sources:
- `work/outputs/assignment8_paper_export.json`
- `work/outputs/assignment8_action_playbook_metrics.json`

## 15. Ranked human-review playbook

Queue:
- 50 pages
- P1: 10
- P2: 15
- P3: 25

Archetypes:
- `CTR_AND_STALE`: 8
- `CTR_OPPORTUNITY`: 5
- `MODEL_RISK_ONLY`: 20
- `STALE_RISK`: 17

Reason-code counts:
- `MODEL_TOP50_RISK`: 50
- `LOW_CTR_FOR_POSITION`: 13
- `STALE_366_PLUS`: 25

Action map:
- `CTR_AND_STALE` → `REVIEW_CTR_AND_CONTENT_REFRESH`
- `CTR_OPPORTUNITY` → `REVIEW_SEARCH_SNIPPET_AND_INTENT`
- `STALE_RISK` → `REVIEW_CONTENT_FRESHNESS`
- `MODEL_RISK_ONLY` → `DIAGNOSE_BEFORE_EDIT`

Every queue row:
- requires human review;
- forbids automatic editing/publishing;
- contains reason codes that are diagnostic, not causal;
- excludes the future outcome from the queue export.

Primary sources:
- `work/outputs/assignment8_paper_export.json`
- `work/outputs/assignment8_action_playbook_metrics.json`

## 16. Operational limits locked by Assignment 8

Unsupported uses include:
- automatic edit / refresh / rewrite;
- automatic delete, redirect, unpublish or publish;
- automatic title/meta change;
- treating `p_decline` as a calibrated probability;
- acting on MODEL_RISK_ONLY without diagnosis;
- treating age as proof that a refresh is required;
- treating low CTR as proof that a CTR edit will improve traffic;
- using identifiers as model features;
- training with post-decision/future leakage;
- hiding unfavorable validation;
- deploying to materially new clients without fresh validation.

Current trigger state:
- classification below frozen baseline: **true**
- regression not better than frozen baseline: **false**
- ranking below frozen baseline: **true**
- unseen-client revalidation required: **true**

Operating mode:
- **research POC / human decision-support only**

Primary source:
- `work/outputs/assignment8_action_playbook_metrics.json`

## 17. Public-safety constraints

The public paper must not expose:
- client names;
- domains;
- URLs;
- page titles;
- keywords or raw search queries;
- tokens or credentials;
- private/local paths;
- non-public identifying information.

Pseudonymized IDs are present in internal analysis, but the public paper should prefer aggregate counts and avoid listing individual page/client IDs unless strictly necessary.

Primary source:
- `DATA_USE.md`

## 18. Paper claim ladder — locked wording

### Strongest defensible headline

A five-feature content-prioritization POC showed promising grouped-development performance, but that improvement did **not** transfer consistently to six held-out clients: regression RMSE improved slightly, while classification and top-50 ranking did not beat their frozen baselines. The result supports a guarded, human-reviewed diagnostic queue and highlights unseen-client validation as a prerequisite for broader use.

### Safe claims

Safe:
- “The warehouse release contains 78.8M daily performance rows.”
- “The final POC used 2,520 balanced pages from 21 pseudonymized clients.”
- “Features were restricted to March 2026 and future outcomes to April 2026.”
- “Grouped development CV improved over baseline on all three benchmarked tasks.”
- “On six held-out clients, only RMSE improved over its frozen baseline; classification and ranking did not.”
- “CTR-relative-to-position was associated with different observed decline rates.”
- “Older content showed a higher observed decline rate in the oldest bucket, but the age pattern was mixed.”
- “Recommendations are decision-support cues requiring human review.”

Unsafe / unsupported:
- “The model was trained on 79 million rows.”
- “The model generalizes to new clients.”
- “The model reliably predicts decline for production deployment.”
- “Refreshing stale content causes recovery.”
- “Fixing CTR causes rankings/traffic to improve.”
- “The top-50 model queue beats the rule baseline on unseen clients.”
- “The score is a calibrated probability of decline.”
- any claim that unfavorable six-client results are omitted or replaced by development-CV values.

## 19. Results table to use in the public paper

The public paper should show **both** validation layers:

### A. Grouped development CV

| Task | Metric | CV baseline | Learned CV |
|---|---:|---:|---:|
| Classification | ROC-AUC | 0.500 | 0.665 |
| Regression | RMSE ↓ | 0.852 | 0.806 |
| Ranking | Precision@50 | 0.824 | 0.872 |

### B. Six-client stress test

| Task | Metric | Frozen baseline | Learned |
|---|---:|---:|---:|
| Classification | ROC-AUC | 0.500 | 0.494 |
| Regression | RMSE ↓ | 1.431 | 1.379 |
| Ranking | Precision@50 | 0.480 | 0.360 |

The paper must visually label A as **development validation** and B as **held-out client stress test**.

## 20. Source-of-truth map

Research framing:
- `work/notebooks/w01_research_question.ipynb`
- `work/notebooks/w02_ml_task_framing.ipynb`

Data contract / target / features:
- `work/notebooks/w03_data_contract.ipynb`

Frozen baselines:
- `work/notebooks/w04_baseline_score.ipynb`
- `work/outputs/multitask_baseline_benchmark.json`
- `work/outputs/baseline_split_manifest.json`

Learned models:
- `work/notebooks/w05_model.ipynb`
- `work/outputs/assignment6_model_benchmark.json`
- `work/outputs/assignment6_error_audit.json`

Validation / leakage / generalization:
- `work/notebooks/w06_validation_audit.ipynb`
- `work/outputs/assignment7_split_audit.json`
- `work/outputs/assignment7_leakage_audit.json`

Recommendations:
- `work/notebooks/w07_action_playbook.ipynb`
- `work/outputs/assignment8_paper_export.json`
- `work/outputs/assignment8_action_playbook_metrics.json`
- `work/figures/assignment8_ranking_validation.png`

Data-release/public-safety authority:
- `docs/ml-intern-dataset-and-lane-guide.md`
- `DATA_USE.md`

## 21. Status

Evidence ledger status: **VERIFIED against committed Assignment 2–8 notebooks and JSON receipts.**

This ledger should be used as the numerical and methodological source of truth when filling `work/notebooks/capstone.ipynb` and building `docs/index.html`.

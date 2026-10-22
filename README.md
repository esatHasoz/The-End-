# The-End-
Explainable AI for Network Intrusion Detection

ENS 491/492 Graduation Project — Sabancı University (FENS) Supervisor: Prof. Dr. Albert Levi · Project #457

Team: Mustafa Esad Hasözhan · Ahmet Çavuşoğlu · Selim Serhat Yılmaz

Status: Design phase (ENS 491). Plan, scope and dataset list are drafts until confirmed with the supervisor.

1. What this project is (and isn't)

This is a research / evaluation project, not a deployable IDS. We train multiple ML models on multiple network-intrusion datasets and use explainability (XAI) methods to answer one question:

Does XAI do meaningful work in cybersecurity — i.e., can it tell us whether a model has learned genuine attack behaviour or dataset shortcuts?

Research questions
RQ1 — Shortcut learning: Do NIDS models learn genuine attack signals, or do they exploit dataset artifacts (e.g., TTL, ports, timestamps, flow IDs, tool-specific fingerprints, label errors)?
RQ2 — XAI reliability: Can XAI methods reliably detect this? Are their explanations faithful, stable, and consistent with each other?
2. Datasets

Five datasets, each evaluated separately. No dataset fusion (supervisor decision). Cross-dataset experiments are train-on-A / test-on-B transfer only.

ID	Dataset	Source	Role
D1	CSE-CIC-IDS2018 (original)	CIC / AWS	Primary baseline
D2	BCCC-CSE-CIC-IDS2018	York Univ. (BCCC)	Same traffic, corrected labels/tool
D3	NF3-CSE-CIC-IDS2018	UQ (NetFlow v3)	Same traffic, different feature extractor
D4	NF3-UNSW-NB15	UQ (NetFlow v3)	Different traffic, same feature format as D3
D5	CIC IoT-DIAD 2024	UNB	Recent, IoT domain
(opt.)	CICIDS2017 (original vs. corrected)	CIC / Engelen et al.	Case study of documented flaws — pending supervisor approval

The design uses controlled comparisons so that differences in explanations can be attributed:

same traffic, different extraction tool (D1 vs D3)
same tool/format, different traffic (D3 vs D4)
original vs. corrected labels (D1 vs D2)

Experiment depth per comparison is still to be agreed with the supervisor.

To do: BCCC access form; verify label provenance of the NetFlow v3 sets; confirm which dataset pairs share mappable features (needed for cross-dataset tests).

3. Models
Model	Type
Logistic Regression	Linear, glass-box
Decision Tree	Glass-box
Random Forest	Ensemble, black-box
LightGBM	Gradient boosting, black-box
Explainable Boosting Machine (EBM)	Glass-box GBM
Neural network classifier (MLP)	Black-box
Isolation Forest	Unsupervised — control group for shortcut detection

Mixing glass-box and black-box models gives a built-in cross-check: if a glass-box model and a post-hoc explanation of a black-box model point to the same features, that's stronger evidence.

4. Explainability methods

The supervisor asked us not to rely on SHAP alone. Comparing explainers is part of the contribution (cf. the disagreement problem).

Method	Scope	Applied to
TreeSHAP	Local + global, exact for trees	All tree models, Isolation Forest
KernelSHAP / DeepSHAP	Local, model-agnostic	2–3 representative models, sampled test set
Permutation importance	Global, model-agnostic, performance-based	All models
LIME	Local surrogate	2–3 representative models, sampled test set
EBM native explanations	Intrinsic (glass-box)	EBM
Counterfactuals (DiCE)	Local	Optional, 1–2 models

Expensive explainers run only on representative models (e.g., LightGBM, MLP, Logistic Regression) to keep the schedule realistic.

5. Evaluation
Detection performance

Balanced accuracy, precision, recall, F1 (macro + per-class), false positive rate.

Explanation quality
Metric	What it checks	How
Faithfulness	Do "important" features actually matter?	Delete/mask top-k features, measure performance drop (deletion curve, ΔF1)
Stability	Is the explanation robust?	Small input noise / different seeds → rank correlation of attributions
Agreement	Do explainers agree?	Top-k overlap (Jaccard), Spearman/Kendall rank correlation
Domain alignment	Does it make security sense?	Manual review of top features against attack semantics
Shortcut-detection protocol
Screen candidate artifact features (single-feature AUROC, identity-like features).
Rank features with the XAI methods above.
Ablate: remove suspected artifacts, retrain, measure performance drop.
Transfer: train on one dataset, test on another; large generalisation loss = shortcut evidence.
Methodological safeguards (from Arp et al.)
Time-based, per-class train/val/test split to avoid leakage from random splitting.
Test set separated before any preprocessing or feature selection.
Report per-class metrics, not just accuracy.
6. Pipeline
1. Baseline training      7 models × 5 datasets             → detection metrics
2. Cheap explainers       TreeSHAP, permutation, EBM        → global rankings
3. Expensive explainers   KernelSHAP/DeepSHAP, LIME         → local attributions (subset)
4. Agreement              compare 2–3                       → overlap, rank correlation
5. Faithfulness           feature deletion/masking          → deletion curves, ΔF1
6. Stability              perturbation / seeds              → attribution variance
7. Shortcut ablation      drop artifact features, retrain   → performance drop
8. Cross-dataset          train A / test B (no fusion)      → generalisation loss
9. (Optional) DiCE        counterfactuals                   → meaningfulness of changes
10. Synthesis             combine 4–8                       → answer RQ1 & RQ2

Critical path: 1 → 2 → 4/5 → 7 → 8 → 10. Step 9 can be cut.

7. Team & roles

Everyone works end-to-end on their own datasets; each person additionally owns one shared module.

Member	Shared module ownership
Ahmet Çavuşoğlu	Data loading, cleaning, splitting
Mustafa Esad Hasözhan	Model training, tuning, model selection
Selim Serhat Yılmaz	XAI methods & explanation metrics
8. Timeline (summary)
ENS 491 (design, 14 weeks): literature review (2024+ top-venue papers), dataset acquisition & cleaning, baseline models, first explanations, proposal & interim report.
ENS 492 (implementation, 14 weeks): explainer comparison, faithfulness/stability, shortcut ablation, cross-dataset tests, synthesis, final report & presentation.
Target: core work done in ~15 working weeks (≈18 calendar weeks incl. exam weeks), since ENS 492 is our final semester.
Long compute jobs: dry-run on a small sample first, checkpoint, log, then run overnight.

The detailed weekly plan lives in the proposal document.

9. Proposed repository structure
.
├── data/              # NOT committed — raw/processed datasets (see data/README)
├── notebooks/         # exploration, EDA
├── src/
│   ├── data/          # loaders, cleaning, time-based splits
│   ├── models/        # training, tuning, model registry
│   ├── xai/           # SHAP, LIME, permutation, EBM wrappers
│   ├── metrics/       # detection + explanation metrics
│   └── experiments/   # ablation, cross-dataset, agreement runs
├── configs/           # per-dataset / per-model configs
├── results/           # metrics, figures (large files ignored)
├── reports/           # proposal, interim, final
└── README.md
10. Workflow
main is protected; work on feature branches (feature/<name>), merge via pull request with at least one review.
Datasets and large artifacts are never committed (.gitignore).
Every experiment is driven by a config file + fixed seed so results are reproducible.
11. Key references
Arp et al., Dos and Don'ts of Machine Learning in Computer Security (USENIX Security 2022) — pitfalls checklist
Engelen et al., Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study (IEEE SPW 2021) — dataset artifacts
Flood et al., Bad Design Smells in Benchmark NIDS Datasets (IEEE EuroS&P 2024)
Jacobs et al., AI/ML for Network Security: The Emperor has no Clothes (ACM CCS 2022)
Lundberg & Lee, A Unified Approach to Interpreting Model Predictions (NeurIPS 2017) — SHAP
Ribeiro et al., "Why Should I Trust You?" (KDD 2016) — LIME
Molnar, Interpretable Machine Learning (online book)

The full, verified reading list (venue, year, institution) is maintained separately.

12. Open decisions
 Experiment depth per dataset comparison — with supervisor
 CICIDS2017 as case study: yes/no — with supervisor
 Final wording of RQ1/RQ2
 Which models get the expensive explainers
 Cross-dataset pairs (depends on feature compatibility)

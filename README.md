# JOMIZOO hamster bedding research

**SYNTHETIC DATA ONLY — NOT AN ANIMAL EXPERIMENT.**

本仓库用于仓鼠垫料研究的实验设计和分析代码演练。所有示例数据均由程序生成，**不是动物实验观测、不是产品效果证据，也不能以实验结果发表**。暂无真实数据、动物伦理批准、样本量论证或获批实验方案。本仓库不提交论文、不创建伦理批准，也不宣称任何垫料安全性或最佳铺设深度。

A dependency-free Python package for reproducible planning of two provisional studies:

1. **S1:** short/long paper fibre × nominal bulk density 35/55 kg/m³, common depth 40 cm.
2. **S2:** nominal bedding depth 40/50/60 cm, long fibre and 45 kg/m³ held fixed.

These numeric levels are simulation assumptions awaiting material feasibility, welfare review and protocol finalisation. The examples use 12 hypothetical animals per condition (48 + 36), sex-balanced within a single recruitment cohort. They are not a justified future sample size. Animals are independent, singly housed experimental units; no animal handling is performed by this software.

## Quick start

Python 3.10 or later; no third-party runtime dependencies. Run from this repository:

```bash
export PYTHONPATH=src
python -m jomizoo_bedding simulate --scenario modest --seed 20261002 --output out/modest
python -m jomizoo_bedding validate out/modest
python -m jomizoo_bedding analyze out/modest --output out/modest-analysis --permutations 9999
python -m unittest discover -s tests -v
```

Optional package installation: `python -m pip install -e .`, then use `jomizoo-bedding` instead of `python -m jomizoo_bedding`. Runtime analysis remains dependency-free. Output directories must be empty; existing files are never silently overwritten.

## What is provided

- Three named scenarios (`null`, `modest`, `plateau`) with the same frozen seed `20261002`; no seed selection for favourable results.
- Row-level `SYNTHETIC_NOT_OBSERVED` provenance, fixed units, scenario and seed in every source CSV.
- SHA-256 manifests, duplicate/identity/range/unit/coverage/censoring/composition checks, and rejection of mixed observed/synthetic provenance.
- Primary endpoint: confirmed use of a self-excavated burrow **by day 14**. A negative requires complete 14-day follow-up and ≥90% endpoint-surveillance coverage. Early censoring or insufficient coverage without a confirmed event yields an unknown outcome. The coverage threshold is hypothetical and needs feasibility validation.
- Cell risks and Wilson 95% intervals; one sex-blocked Monte Carlo omnibus randomization demonstration per study with the `(extreme + 1)/(permutations + 1)` correction. Descriptive risk contrasts are not confirmatory findings.
- Descriptive Kaplan–Meier values for latency to first confirmed use. Confirmed events are retained even with low total surveillance. Event-free low-surveillance animals are excluded from this illustration; selection and informative censoring can invalidate interpretation.
- One activity-summary row per animal and one bench-summary row per independently produced batch, preventing technical replicates or animal-nights from being counted as independent animals.
- A visibly watermarked SVG figure and machine-readable analysis JSON. No synthetic figure is labelled as an observed result.

See [study design](docs/STUDY_DESIGN.md), [data dictionary](docs/DATA_DICTIONARY.md), [analysis specification](docs/ANALYSIS.md), and [synthetic data policy](docs/SYNTHETIC_DATA_POLICY.md).

## Reproduce the checked-in demonstration

```bash
export PYTHONPATH=src
python scripts/reproduce_examples.py --output out/reproduced
python scripts/verify_examples.py out/reproduced
```

The checked-in [examples](examples/synthetic/) contain all three scenarios, source tables, manifests, analysis summaries and SVG figures. Reproduction compares exact bytes with the reference artifacts. Fixed-seed bytes are expected to reproduce under the reference Python 3.12 environment; validate statistical behaviour separately on other Python versions. The CI workflow uses Python 3.12.

The simulated day-14 probabilities are inputs, not fitted experimental estimates:

| Scenario | S1 short35 / short55 / long35 / long55 | S2 depth40 / depth50 / depth60 |
|---|---|---|
| null | .65 / .65 / .65 / .65 | .70 / .70 / .70 |
| modest | .45 / .55 / .60 / .72 | .58 / .68 / .74 |
| plateau | .50 / .67 / .73 / .76 | .63 / .76 / .77 |

“Null” concerns the primary treatment response; it does not remove random variability. “Plateau” specifies hypothetical diminishing differences and does not establish an optimal depth. The bench generator uses equal means under null and a common illustrative ordered pattern under the other two scenarios. No health effects are simulated or claimed.

## Before any real study

Work with qualified veterinary/research collaborators to settle welfare review, material composition and contaminants, independent production batches, housing, stopping rules, observation validity, randomization, preregistration and a justified sample size. The software currently rejects observed-data provenance intentionally. A real-data schema and prespecified analysis must be reviewed separately; do not relabel synthetic records as observations.

The demonstration assumes one independently produced hypothetical material batch per animal. If real animals share production batches, add that clustering to allocation and analysis; subdividing one bag does not create independent production batches. A real multicohort design must preserve its actual randomization blocks, not reuse this single-cohort sex-only permutation unchanged.

## License and citation

Code and synthetic example artifacts are provided under [MIT](LICENSE). See [CITATION.cff](CITATION.cff) for software citation metadata. The repository makes no claims about publication acceptance or animal-study efficacy.

# Data dictionary — all records are SYNTHETIC_NOT_OBSERVED

UTF-8 CSV, decimal point `.`, blank cell for unknown endpoint/fraction. No personally identifiable records, animal video or real animal measurements are included. Every input row carries `data_origin`, `scenario`, and `simulation_seed`.

## animals.csv

One row per hypothetical animal, 84 default rows across independent studies.

| Field | Definition / allowed values |
|---|---|
| study | S1 or S2 |
| animal_id | unique synthetic identifier prefixed SIM- |
| condition | predefined study-specific condition label |
| sex | female / male; balanced within each condition |
| recruitment_cohort | SIM-single-cohort |
| allocation_block | sex; actual randomization and permutation block |
| fibre_structure | short / long qualitative placeholder; physical fibre dimensions await validation |
| bulk_density_kg_m3 | nominal kg/m³ (35/55 for S1;45 for S2) |
| depth_cm | nominal centimetres (40 for S1;40/50/60 for S2) |
| material_batch_id | independently produced hypothetical batch per animal, never aliquot identity |
| monitoring_coverage_fraction | total coverage fraction for endpoint surveillance, 0–1; separate from activity sampling |
| endpoint_observable | 1 when numeric coverage ≥0.90, otherwise 0; adequate-for-negative flag, not a restriction on confirmed positives |
| followup_days | follow-up duration 0–14 days |
| latency_days | first confirmed event time if event, otherwise event-free censoring time |
| event_observed | 0/1 valid first-use confirmation |
| burrow_by_day14 | 1 confirmed event;0 reliable negative;blank unknown |

Generated values and validators use explicit physical units; the validator does not silently convert alternate units. Numeric density and depth are intended nominal design values, not measurements of physical batches.

## daily_activity.csv

Fourteen scheduled rows per animal. Composite key `(animal_id, night)` must be unique. Study and condition must match the animal table. `night` is integer 1–14. `observation_minutes` is scorable monitored time, bounded 0–60. `digging_minutes + exploring_minutes + other_minutes` equals `observation_minutes`. Zero exposure denotes an unavailable sample, including post-withdrawal nights. `other_minutes` never implies inferred underground behaviour or sleep.

The derived `activity_per_animal.csv` reports observed-night count, total monitored minutes and pooled observed-time fractions. All fractions are blank when an animal has no monitored activity time. This table keeps one row per animal.

## bench.csv

Four conditions from S1, six independent batches per condition, three technical replicates per batch. `bench_batch_id` belongs to one condition only; `(bench_batch_id, tunnel_replicate)` is unique. `retention_fraction_24h` is in [0,1], a hypothetical assay readout. The derived `retention_per_independent_batch.csv` contains 24 batch means with `technical_replicates=3`.

## manifest.json

Includes schema `1.0`, synthetic-only status, scenario, seed, n per condition, units, simulation assumptions, coverage threshold and SHA-256 + row count for each source table. `analysis.json` retains the source-manifest hash and provenance. `analysis_manifest.json` hashes generated outputs.

Hashes establish byte integrity, not observational truth, welfare validity or provenance beyond the stated synthetic generation process. The CLI intentionally rejects `OBSERVED` or mixed source labels. It is not a validated real-animal-data ingestion service.

# Provisional study design — SYNTHETIC DEMONSTRATION ONLY

This is an analysis and materials-testing plan, not an approved animal protocol or completed experiment. No animal procedures should be inferred from the simulator. Densities, depths, production-batch counts, surveillance threshold, observation windows and sample sizes are hypothetical and require feasibility testing and specialist review.

## Two animal studies

| Item | S1 | S2 |
|---|---|---|
| Species proposed | Syrian hamster | Syrian hamster |
| Factors | paper fibre short/long × nominal bulk density 35/55 kg/m³ | bedding depths 40/50/60 cm |
| Fixed material parameters | depth 40 cm | long fibre, density 45 kg/m³ |
| Demonstration allocation | 12 per factorial cell = 48 | 12 per depth = 36 |
| Sex blocks | six female + six male per condition | six female + six male per condition |
| Cohort | one simulated recruitment cohort | one simulated recruitment cohort |
| Independent unit | individually housed hypothetical animal/enclosure | individually housed hypothetical animal/enclosure |
| Material batches | one independently produced hypothetical batch per animal | one independently produced hypothetical batch per animal |

The sample counts demonstrate balanced data handling, not statistical power. No animal is reused across studies. Material-batch IDs mean **independent production**, not portions from a common bag. If future animals share batches, the analysis needs clustering and allocation that prevent batch/treatment confounding. The independent-batch simulation is deliberately simple and may be impractical; it is not evidence that actual production is independent.

Before finalising material experiments, define fibre measurement and source, moisture, additives, contaminants, particle emissions, bedding volume and preparation, tunnel geometry and inspection, room/housing conditions, acclimation, sex/age inclusion, veterinary oversight, randomization concealment, masked scoring, animal welfare stopping rules and preregistration. No such approval or assay validation is claimed here.

## Primary endpoint and surveillance

The primary binary endpoint is **confirmed use of a self-excavated burrow by day 14**. It is not simply excavation, an unverified hole, or remaining in a burrow at a single day-14 inspection. The future operational definition and confirmation duration must be validated before an animal experiment.

- `1`: at least one independently verifiable event is recorded during follow-up, even if total coverage is later insufficient.
- `0`: no confirmed event, complete 14-day follow-up, and at least 90% illustrative endpoint-surveillance coverage.
- unknown: no confirmed event with early termination or inadequate endpoint-surveillance coverage.

The ≥90% rule is a placeholder feasibility assumption. Coverage alone does not guarantee detection; critical camera/entrance occlusion can invalidate a negative even with a high numeric percentage. The simplified simulator does not encode occlusion windows, missed events at individual observation times, or a full detection model. A real protocol must handle these separately. Unknown outcomes must never be recoded as failures.

Latency is time to first confirmed use. Event-free eligible animals are right-censored at the end of follow-up, at most 14 days. A confirmed event precedes any subsequent withdrawal. Synthetic administrative dropout and coverage gaps are generic code test cases, not estimated attrition rates.

## Activity measurement

The simulator schedules a 60-minute scorable activity sample on each of 14 nights. These samples are separate from primary endpoint surveillance. Missing nights have zero monitored time; zero exposure does not mean zero behaviour. Digging, exploring and other **scorable** behaviour partition the monitored minutes. `other` is not a classification of underground behaviour or sleep.

The animal summary pools observed time: summed behaviour minutes divided by summed monitored minutes. With unequal monitored durations this is exposure-weighted, not an equal-weight mean of nightly proportions. An animal without scorable exposure has blank fractions. A real instrument needs explicit unobservable intervals, classifier validation and human reliability assessment; those are outside this minimal simulator.

## Independent bench study

The implemented bench design has four fibre–density conditions, **six independently produced batches per condition**, and three technical tunnel preparations per batch: 24 independent batches and 72 technical tunnel records. Batches are not shared across conditions in this demonstration. Animal-study and bench-study batches are distinct.

The illustrative outcome is the fraction of tunnel structure retained at 24 hours. Its operational measurement, load and geometry are not yet validated. Analysis first averages technical replicates within production batch. The 72 tunnel measurements must not be described as 72 independent production replicates. Bench numbers are synthetic material performance, not animal health or welfare evidence.

## Scenarios

`null`, `modest` and `plateau` are input assumptions with a common fixed seed. Primary-event times use an exponential generator calibrated to the assumed day-14 probability. This imposes a constant latent event hazard and is not a verified behavioural model. Activity and bench variations are simple bounded stochastic examples. No selection of seed, scenario, animal or result is used to obtain statistical significance.

# Analysis specification — synthetic demonstration

## Primary analysis

For each study, known primary outcomes are summarized by condition as successes / known n. Cell-specific 95% Wilson score intervals use z=1.959963984540054. These are not simultaneous intervals, do not account for informative missingness, and are not proof of a biological effect. All-randomized missingness bounds assign every unknown outcome first to failure and then to success; they are identification bounds, not confidence intervals.

There is **one omnibus randomization demonstration per study**: four S1 cells or three S2 depth groups. The statistic is the sum over groups of `n_g * (p_g - p_overall)^2`. Condition labels are permuted within actual sex blocks among known-outcome records, preserving their observed group counts. With 9,999 permutations and a frozen seed offset (source seed +1 for S1, +2 for S2), the reported Monte Carlo p-value is `(extreme + 1)/(9999 + 1)`. Ties count as extreme. Constant outcomes return p=1; cells with no known outcomes yield no p-value. This avoids logistic-regression separation and fabricated model-convergence claims.

Missingness must be exchangeable conditional on blocks for this observed-case permutation to support a randomization interpretation. Attrition related to treatment, outcome or latent burrowing capacity invalidates that assumption. This is not an unconditional exact test under informative missingness. A future multicohort trial needs its exact randomization blocks implemented before using the pipeline; the example is one cohort, sex blocks only.

## Descriptive risk contrasts

S1 calculates equally weighted cell-risk contrasts:

- fibre: `(long35 + long55 - short35 - short55)/2`;
- density: `(short55 + long55 - short35 - long35)/2`;
- interaction: `(long55 - long35) - (short55 - short35)`.

S2 calculates 50−40, 60−40, and 60−50 cm risk differences. These are descriptive point estimates with **no inferential intervals or confirmatory pairwise p-values**. They do not establish optimality. No contrast is computed if a relevant cell has no known outcomes. There is no post hoc choosing of the most favourable comparison or seed.

## Latency

Kaplan–Meier values describe time until confirmed first use. Event times precede censoring at ties, and the risk set includes both observations at the tied time. Confirmed events remain eligible even when later total coverage is below the threshold. Event-free animals with low coverage are omitted because their full event-free follow-up is not reliable. This selection can be informative; the example is not a validated method for intermittent detection/occlusion. Noninformative selection and censoring would be needed for biological interpretation. No log-rank, Cox effect, median, or health claim is reported.

## Secondary data and independent units

Activity is first aggregated within animal using total observed behaviour time / total monitored time. With zero monitored time, fractions remain blank. The software makes no statistical test that treats 14 nights as 14 independent animals. Unobservable underground periods are not labelled sleep.

Bench retention is averaged across the three technical tunnel replicates in each independently produced batch. No batch-level regression or animal-health inference is claimed. The experiment has 24 independent bench production batches, not 72. Animal batches are separate and one independently produced hypothetical batch per animal. Actual shared-batch designs require a revised clustered analysis.

## Computational verification

Tests cover deterministic generation, all scenarios, provenance and units, hashes, allocation/identity integrity, censoring and low-coverage endpoints (including confirmed positives), missing activity, composition, duplicate nights, Wilson numeric limits, Kaplan–Meier ties, constant-outcome separation, absent-outcome groups, aggregation units and visible synthetic labelling.

The source has no third-party runtime dependencies. Python 3.12 is the byte-reproducibility reference; a fixed seed is not a cross-language or cross-version RNG specification. SHA-256 verifies byte integrity only. Biological models, animal welfare, instrument validity and real-world measurement error are unverified.

"""Dependency-free synthetic demonstration. NEVER treat output as animal observations."""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ORIGIN = "SYNTHETIC_NOT_OBSERVED"
SCHEMA = "1.0"
DAYS = 14
UNITS = {"depth_cm": "cm", "bulk_density_kg_m3": "kg/m3", "latency_days": "day", "followup_days": "day", "observation_minutes": "minute", "digging_minutes": "minute", "exploring_minutes": "minute", "other_minutes": "minute", "retention_fraction_24h": "fraction", "monitoring_coverage_fraction": "fraction"}
SCENARIOS = {
    "null": {"S1": [.65, .65, .65, .65], "S2": [.70, .70, .70]},
    "modest": {"S1": [.45, .55, .60, .72], "S2": [.58, .68, .74]},
    "plateau": {"S1": [.50, .67, .73, .76], "S2": [.63, .76, .77]},
}
CONDITIONS = {"S1": [("short_35", "short", 35, 40), ("short_55", "short", 55, 40), ("long_35", "long", 35, 40), ("long_55", "long", 55, 40)], "S2": [("depth_40", "long", 45, 40), ("depth_50", "long", 45, 50), ("depth_60", "long", 45, 60)]}
DATA_FILES = ("animals.csv", "daily_activity.csv", "bench.csv")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def simulate(output, scenario="modest", seed=20261002, n_per_condition=12):
    if scenario not in SCENARIOS:
        raise ValueError("Unknown simulation scenario")
    if n_per_condition < 2 or n_per_condition % 2:
        raise ValueError("n_per_condition must be positive, even, and >=2 (sex balance)")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory must be empty; generated files are never silently overwritten")
    output.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    provenance = {"data_origin": ORIGIN, "scenario": scenario, "simulation_seed": seed}
    animals, daily, bench = [], [], []
    for study, specs in CONDITIONS.items():
        for sex in ("female", "male"):
            allocation = [i for i in range(len(specs)) for _ in range(n_per_condition // 2)]
            rng.shuffle(allocation)
            for sequence, group in enumerate(allocation, start=1):
                condition, fibre, density, depth = specs[group]
                animal = f"SIM-{study}-{sex[0].upper()}-{sequence:03d}"
                p = SCENARIOS[scenario][study][group]
                event_time = rng.expovariate(-math.log1p(-p) / DAYS)
                followup = round(rng.uniform(4, 12), 4) if rng.random() < .05 else float(DAYS)
                # Endpoint surveillance differs from the nightly 60-minute activity sample.
                coverage = round(rng.uniform(.92, 1), 4) if rng.random() > .04 else .70
                observable = int(coverage >= .90)
                event = int(event_time <= followup and (observable or rng.random() < coverage))
                latency = round(event_time, 4) if event else followup
                primary = 1 if event else (0 if followup == DAYS and observable else "")
                animals.append(dict(provenance, study=study, animal_id=animal, condition=condition, sex=sex, recruitment_cohort="SIM-single-cohort", allocation_block=sex, fibre_structure=fibre, bulk_density_kg_m3=density, depth_cm=depth, material_batch_id=f"{animal}-INDEPENDENT-BATCH", monitoring_coverage_fraction=coverage, endpoint_observable=observable, followup_days=followup, latency_days=latency, event_observed=event, burrow_by_day14=primary))
                animal_dig = max(.015, min(.4, rng.gauss(.09 + .07*p, .025)))
                for night in range(1, DAYS + 1):
                    observed = night <= math.floor(followup) and rng.random() > .05
                    minutes = 60 if observed else 0
                    digging = round(minutes * max(0, min(.5, rng.gauss(animal_dig, .035))), 4)
                    exploring = round(minutes * max(0, min(.4, rng.gauss(.18, .025))), 4)
                    daily.append(dict(provenance, study=study, animal_id=animal, condition=condition, night=night, observation_minutes=minutes, digging_minutes=digging, exploring_minutes=exploring, other_minutes=round(minutes-digging-exploring, 4)))
    for group, (condition, fibre, density, _) in enumerate(CONDITIONS["S1"]):
        for batch in range(1, 7):
            batch_id = f"SIM-BENCH-{condition}-B{batch:02d}"
            center = .65 if scenario == "null" else [.48, .61, .68, .79][group]
            batch_mean = max(.02, min(.98, rng.gauss(center, .06)))
            for replicate in range(1, 4):
                bench.append(dict(provenance, study="BENCH", condition=condition, bench_batch_id=batch_id, tunnel_replicate=replicate, fibre_structure=fibre, bulk_density_kg_m3=density, retention_fraction_24h=round(max(0, min(1, rng.gauss(batch_mean, .035))), 5)))
    for name, rows in zip(DATA_FILES, (animals, daily, bench)):
        write_csv(output / name, rows)
    manifest = {"schema_version": SCHEMA, "data_origin": ORIGIN, "status": "SIMULATION_ONLY_NO_ANIMAL_EXPERIMENT", "scenario": scenario, "seed": seed, "n_per_condition": n_per_condition, "single_cohort": True, "units": UNITS, "endpoint_coverage_threshold": .90, "animal_material_batches": "one independently produced hypothetical batch per animal; not aliquots of one batch", "assumptions": SCENARIOS[scenario], "limitations": ["All effect sizes, density and depth levels, coverage threshold and sample sizes are planning assumptions, not observed facts or approved animal procedures.", "No seed searching; null/modest/plateau are scenarios, not biological conclusions.", "Bench batches are independent of animal material batches. Animal and batch are analysis units.", "Hashes detect accidental file changes; they do not establish the truth of any observations."], "files": {name: {"sha256": digest(output/name), "rows": len(rows)} for name, rows in zip(DATA_FILES, (animals, daily, bench))}}
    write_json(output / "manifest.json", manifest)
    return validate(output)


def numeric(row, key, lower=None, upper=None):
    try:
        value = float(row[key])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid numeric field: {key}") from exc
    if not math.isfinite(value) or (lower is not None and value < lower) or (upper is not None and value > upper):
        raise ValueError(f"Out-of-range or nonfinite field: {key}")
    return value


def validate(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("data_origin") != ORIGIN or manifest.get("schema_version") != SCHEMA:
        raise ValueError("Only explicitly SYNTHETIC_NOT_OBSERVED schema 1.0 datasets are accepted")
    if manifest.get("units") != UNITS or manifest.get("endpoint_coverage_threshold") != .90:
        raise ValueError("Unit or endpoint coverage metadata mismatch")
    if set(manifest.get("files", {})) != set(DATA_FILES) or manifest.get("scenario") not in SCENARIOS:
        raise ValueError("Dataset manifest file/scenario mismatch")
    tables = {}
    for name in DATA_FILES:
        if digest(directory/name) != manifest["files"][name]["sha256"]:
            raise ValueError(f"SHA256 mismatch: {name}")
        rows = read_csv(directory/name)
        if not rows or len(rows) != manifest["files"][name]["rows"]:
            raise ValueError(f"Empty dataset or row count mismatch: {name}")
        for row in rows:
            if row.get("data_origin") != ORIGIN or row.get("scenario") != manifest["scenario"] or row.get("simulation_seed") != str(manifest["seed"]):
                raise ValueError("Mixed, missing, or inconsistent synthetic provenance")
        tables[name] = rows
    animals = tables["animals.csv"]
    ids = {}
    counts, materials = defaultdict(int), set()
    for row in animals:
        aid = row["animal_id"]
        if aid in ids or not aid.startswith("SIM-"):
            raise ValueError("Duplicate or non-synthetic animal identity")
        ids[aid] = row
        study, condition = row["study"], row["condition"]
        spec = next((s for s in CONDITIONS.get(study, []) if s[0] == condition), None)
        if spec is None or row["fibre_structure"] != spec[1] or numeric(row, "bulk_density_kg_m3") != spec[2] or numeric(row, "depth_cm") != spec[3]:
            raise ValueError("Study/factor level or physical unit mismatch")
        if row["sex"] not in ("female", "male") or row["allocation_block"] != row["sex"] or row["recruitment_cohort"] != "SIM-single-cohort":
            raise ValueError("This demonstration requires single-cohort sex blocks")
        counts[(study, condition, row["sex"])] += 1
        if row["material_batch_id"] in materials:
            raise ValueError("Demonstration requires independent animal material batches")
        materials.add(row["material_batch_id"])
        coverage = numeric(row, "monitoring_coverage_fraction", 0, 1)
        if row["endpoint_observable"] not in ("0", "1") or int(row["endpoint_observable"]) != int(coverage >= .90):
            raise ValueError("Endpoint surveillance coverage contradiction")
        followup = numeric(row, "followup_days", 0, DAYS)
        latency = numeric(row, "latency_days", 0, followup)
        if row["event_observed"] not in ("0", "1"):
            raise ValueError("Event indicator must be binary")
        event = int(row["event_observed"])
        expected = "1" if event else ("0" if followup == DAYS and coverage >= .90 else "")
        if row["burrow_by_day14"] != expected or (not event and latency != followup):
            raise ValueError("Endpoint/event/censoring/coverage contradiction")
    n = manifest["n_per_condition"]
    expected_counts = {(study, spec[0], sex): n//2 for study, specs in CONDITIONS.items() for spec in specs for sex in ("female", "male")}
    if n < 2 or n % 2 or dict(counts) != expected_counts:
        raise ValueError("Incorrect within-sex randomized condition counts")
    daily_keys = set()
    for row in tables["daily_activity.csv"]:
        aid = row["animal_id"]
        night = numeric(row, "night", 1, DAYS)
        if night != int(night) or aid not in ids or (aid, night) in daily_keys:
            raise ValueError("Unknown identity, duplicate or invalid animal-night key")
        daily_keys.add((aid, night))
        if row["study"] != ids[aid]["study"] or row["condition"] != ids[aid]["condition"]:
            raise ValueError("Animal-night treatment mapping mismatch")
        minutes = numeric(row, "observation_minutes", 0, 60)
        parts = [numeric(row, key, 0, minutes) for key in ("digging_minutes", "exploring_minutes", "other_minutes")]
        if abs(sum(parts)-minutes) > .001 or (night > math.floor(float(ids[aid]["followup_days"])) and minutes != 0):
            raise ValueError("Activity composition or follow-up exposure mismatch")
    if daily_keys != {(aid, night) for aid in ids for night in range(1, DAYS+1)}:
        raise ValueError("Missing scheduled animal-night rows; represent missing exposure as zero")
    bench_keys, bench_groups, batch_conditions = set(), defaultdict(set), {}
    for row in tables["bench.csv"]:
        condition = row["condition"]
        spec = next((s for s in CONDITIONS["S1"] if s[0] == condition), None)
        rep = numeric(row, "tunnel_replicate", 1, 3)
        key = (row["bench_batch_id"], rep)
        if spec is None or row["fibre_structure"] != spec[1] or numeric(row, "bulk_density_kg_m3") != spec[2] or row["study"] != "BENCH" or rep != int(rep) or key in bench_keys:
            raise ValueError("Bench identity or factor mismatch")
        numeric(row, "retention_fraction_24h", 0, 1)
        if row["bench_batch_id"] in batch_conditions and batch_conditions[row["bench_batch_id"]] != condition:
            raise ValueError("A bench batch cannot belong to multiple conditions")
        batch_conditions[row["bench_batch_id"]] = condition
        bench_keys.add(key)
        bench_groups[condition].add(row["bench_batch_id"])
    if any(len(bench_groups[s[0]]) != 6 for s in CONDITIONS["S1"]) or len(bench_keys) != 72:
        raise ValueError("Expected six independent bench batches and three technical replicates per condition")
    return {"valid": True, "data_origin": ORIGIN, "animals": len(animals), "unknown_primary": sum(r["burrow_by_day14"] == "" for r in animals), "animal_nights": len(daily_keys), "independent_bench_batches": sum(map(len, bench_groups.values()))}


def wilson(successes, n, z=1.959963984540054):
    if n == 0:
        return [None, None]
    p = successes/n
    denom = 1+z*z/n
    center = (p+z*z/(2*n))/denom
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [max(0.0, center-half), min(1.0, center+half)]


def kaplan_meier(times, events):
    """Events precede censoring at ties; censoring remains descriptive here."""
    pairs = list(zip(times, events))
    survival, curve = 1.0, [{"day": 0.0, "survival": 1.0, "at_risk": len(pairs), "events": 0}]
    for time in sorted(set(times)):
        risk = sum(t >= time for t, _ in pairs)
        deaths = sum(t == time and e == 1 for t, e in pairs)
        if deaths:
            survival *= 1-deaths/risk
            curve.append({"day": time, "survival": survival, "at_risk": risk, "events": deaths})
    return curve


def permutation_test(rows, iterations=9999, seed=20261003):
    """Observed-case, within-sex randomization demonstration with +1 correction."""
    if iterations < 1:
        raise ValueError("Permutation count must be >=1")
    known = [r for r in rows if r["burrow_by_day14"] != ""]
    labels = [r["condition"] for r in known]
    outcomes = [int(r["burrow_by_day14"]) for r in known]
    groups = sorted(set(r["condition"] for r in rows))
    if not known or set(labels) != set(groups):
        return {"p_value": None, "reason": "One or more condition cells have no observable primary outcomes", "iterations": iterations}
    def statistic(values):
        buckets = defaultdict(list)
        for label, value in zip(values, outcomes):
            buckets[label].append(value)
        overall = sum(outcomes)/len(outcomes)
        return sum(len(v)*(sum(v)/len(v)-overall)**2 for v in buckets.values())
    observed = statistic(labels)
    blocks = [[i for i, r in enumerate(known) if r["allocation_block"] == sex] for sex in ("female", "male")]
    rng, extreme = random.Random(seed), 0
    for _ in range(iterations):
        permuted = labels.copy()
        for indexes in blocks:
            subset = [labels[i] for i in indexes]
            rng.shuffle(subset)
            for i, label in zip(indexes, subset):
                permuted[i] = label
        extreme += statistic(permuted) >= observed-1e-12
    return {"p_value": (extreme+1)/(iterations+1), "statistic": observed, "iterations": iterations, "seed": seed, "known_n": len(known), "method": "sex-blocked observed-case Monte Carlo omnibus; +1 correction", "limitation": "Requires exchangeable missingness conditional on blocks; not an unconditional exact test under informative missingness."}


def aggregate_daily(rows):
    buckets = defaultdict(list)
    for row in rows:
        buckets[row["animal_id"]].append(row)
    result = []
    for aid, group in sorted(buckets.items()):
        exposure = sum(float(r["observation_minutes"]) for r in group)
        result.append({"data_origin": ORIGIN, "study": group[0]["study"], "animal_id": aid, "condition": group[0]["condition"], "observed_nights": sum(float(r["observation_minutes"]) > 0 for r in group), "total_monitored_minutes": exposure, **{key.replace("_minutes", "_fraction"): (sum(float(r[key]) for r in group)/exposure if exposure else "") for key in ("digging_minutes", "exploring_minutes", "other_minutes")}})
    return result


def aggregate_bench(rows):
    buckets = defaultdict(list)
    for row in rows:
        buckets[row["bench_batch_id"]].append(row)
    return [{"data_origin": ORIGIN, "condition": group[0]["condition"], "bench_batch_id": batch, "technical_replicates": len(group), "mean_retention_fraction_24h": statistics.mean(float(r["retention_fraction_24h"]) for r in group)} for batch, group in sorted(buckets.items())]


def primary_svg(path, results):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620">', '<rect width="1100" height="620" fill="white"/>', '<style>text{font-family:Arial,sans-serif;fill:#162338}</style>', '<text x="45" y="36" font-size="23">Synthetic planning scenarios: confirmed burrow use by day 14</text>', '<text x="45" y="64" font-size="15">Cell risk and Wilson 95% interval; unknown outcomes excluded; no biological conclusions</text>']
    for panel, study in enumerate(("S1", "S2")):
        left = 75+panel*540
        parts += [f'<text x="{left}" y="106" font-size="20">{study}</text>', f'<path d="M{left} 145 V470 H{left+420}" stroke="#516277" fill="none"/>']
        for tick in (0, .25, .5, .75, 1):
            y = 470-tick*300
            parts += [f'<line x1="{left}" y1="{y}" x2="{left+420}" y2="{y}" stroke="#e3e8ee"/>', f'<text x="{left-35}" y="{y+5}" font-size="13">{tick:.2f}</text>']
        for i, (condition, row) in enumerate(results[study]["conditions"].items()):
            x = left+65+i*100
            if row["risk"] is not None:
                y = 470-row["risk"]*300
                low, high = row["wilson_95"]
                parts += [f'<line x1="{x}" y1="{470-high*300}" x2="{x}" y2="{470-low*300}" stroke="#276c9e" stroke-width="3"/>', f'<circle cx="{x}" cy="{y}" r="6" fill="#276c9e"/>']
            parts += [f'<text x="{x}" y="498" font-size="13" text-anchor="middle">{html.escape(condition)}</text>', f'<text x="{x}" y="522" font-size="12" text-anchor="middle">known n={row["known_n"]}</text>', f'<text x="{x}" y="540" font-size="12" text-anchor="middle">unknown={row["unknown_n"]}</text>']
    parts += ['<text x="550" y="310" text-anchor="middle" font-size="50" fill="#bb1f36" style="fill:#bb1f36;opacity:.20" transform="rotate(-13 550 310)">SYNTHETIC — NOT OBSERVED</text>', '<text x="45" y="585" font-size="17" style="fill:#b51f35">SIMULATION ONLY · No animals studied · No ethical approval claimed · No efficacy evidence</text>', '</svg>']
    Path(path).write_text("\n".join(parts)+"\n", encoding="utf-8")


def analyze(directory, output, permutations=9999):
    validation = validate(directory)
    directory, output = Path(directory), Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Analysis output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((directory/"manifest.json").read_text())
    animals = read_csv(directory/"animals.csv")
    results = {}
    for study, specs in CONDITIONS.items():
        subset = [r for r in animals if r["study"] == study]
        cells, curves = {}, {}
        for condition, *_ in specs:
            group = [r for r in subset if r["condition"] == condition]
            known = [int(r["burrow_by_day14"]) for r in group if r["burrow_by_day14"] != ""]
            successes, total, n = sum(known), len(group), len(known)
            cells[condition] = {"randomized_n": total, "known_n": n, "unknown_n": total-n, "successes": successes, "risk": successes/n if n else None, "wilson_95": wilson(successes, n), "all_randomized_missingness_bounds": [successes/total, (successes+total-n)/total]}
            # Inadequate endpoint surveillance cannot be treated as reliable event-free follow-up.
            eligible = [r for r in group if r["endpoint_observable"] == "1" or r["event_observed"] == "1"]
            curves[condition] = {"included_n": len(eligible), "excluded_low_coverage_n": len(group)-len(eligible), "curve": kaplan_meier([float(r["latency_days"]) for r in eligible], [int(r["event_observed"]) for r in eligible])}
        risks = [cells[s[0]]["risk"] for s in specs]
        contrasts = {}
        if all(p is not None for p in risks):
            if study == "S1":
                a,b,c,d = risks
                contrasts = {"long_minus_short_equal_density_weight": (c+d-a-b)/2, "55_minus_35_equal_fibre_weight": (b+d-a-c)/2, "interaction_difference_in_risk_differences": d-c-b+a}
            else:
                contrasts = {"50_minus_40": risks[1]-risks[0], "60_minus_40": risks[2]-risks[0], "60_minus_50": risks[2]-risks[1]}
        results[study] = {"conditions": cells, "descriptive_risk_contrasts_no_inferential_ci": contrasts, "primary_omnibus": permutation_test(subset, permutations, manifest["seed"]+(1 if study == "S1" else 2)), "descriptive_kaplan_meier": curves}
    animal_activity = aggregate_daily(read_csv(directory/"daily_activity.csv"))
    bench_batches = aggregate_bench(read_csv(directory/"bench.csv"))
    write_csv(output/"activity_per_animal.csv", animal_activity)
    write_csv(output/"retention_per_independent_batch.csv", bench_batches)
    result = {"data_origin": ORIGIN, "status": "SYNTHETIC_DEMONSTRATION_NOT_EXPERIMENTAL_RESULTS", "scenario": manifest["scenario"], "source_manifest_sha256": digest(directory/"manifest.json"), "validation": validation, "studies": results, "limitations": ["No observed animal data, ethical approval, product efficacy, optimal depth or sample-size justification.", "Primary analyses use known outcomes; complete follow-up plus >=90% endpoint surveillance is required for a negative. Coverage criterion is hypothetical and requires validation.", "Kaplan–Meier retains confirmed events even at low coverage and excludes low-coverage event-free animals; selection and censoring must be noninformative to interpret as a survival estimator. No inferential latency comparisons.", "Daily observations are aggregated within animal; tunnel replicates within independently produced batch. No pseudoreplication as animals or batches.", "Monte Carlo omnibus is within sex in a single cohort. Informative missingness invalidates randomization interpretation; bounds are descriptive sensitivity checks.", "Risk contrasts are descriptive and have no inferential intervals or multiplicity-adjusted claims. Cell Wilson intervals are not simultaneous.", "Parameters and all three fixed-seed scenarios are assumptions. Real multicohort or shared-batch designs require a revised analysis before data collection."]}
    write_json(output/"analysis.json", result)
    primary_svg(output/"SYNTHETIC_primary_endpoint.svg", results)
    lines = ["# SYNTHETIC — NOT OBSERVED", "", "These are software demonstration outputs, not experimental findings. No animals were studied. No ethical approval, product efficacy, optimal depth, or power claim is made.", "", f"Scenario: **{manifest['scenario']}**. Seed: `{manifest['seed']}`. Data origin: `{ORIGIN}`.", "", "| Study | Condition | Known / allocated | Successes | Unknown | Risk (Wilson 95% CI) |", "|---|---|---:|---:|---:|---|"]
    for study, payload in results.items():
        for condition, cell in payload["conditions"].items():
            lo, hi = cell["wilson_95"]
            interval = f"{cell['risk']:.3f} ({lo:.3f}, {hi:.3f})" if cell["risk"] is not None else "not estimable"
            lines.append(f"| {study} | {condition} | {cell['known_n']} / {cell['randomized_n']} | {cell['successes']} | {cell['unknown_n']} | {interval} |")
    lines += ["", "Monte Carlo p-values and descriptive contrasts are in `analysis.json`; they diagnose the simulator and must not be cited as biological evidence.", "", "Secondary analysis units: one row per animal (activity), one row per independently produced material batch (bench). Time without activity coverage is not scored as zero behaviour. Underground inactivity is not classified as sleep.", "", *[f"- {warning}" for warning in result["limitations"]], "", "![SYNTHETIC figure](SYNTHETIC_primary_endpoint.svg)"]
    (output/"SYNTHETIC_report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    write_json(output/"analysis_manifest.json", {"data_origin": ORIGIN, "files": {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()}})
    return {"data_origin": ORIGIN, "status": "analysis_complete", "scenario": manifest["scenario"], "output": str(output)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="SYNTHETIC ONLY: study planning and reproducible analysis demonstration")
    subs = parser.add_subparsers(dest="command", required=True)
    sim = subs.add_parser("simulate")
    sim.add_argument("--output", required=True)
    sim.add_argument("--scenario", choices=sorted(SCENARIOS), default="modest")
    sim.add_argument("--seed", type=int, default=20261002)
    sim.add_argument("--n-per-condition", type=int, default=12)
    val = subs.add_parser("validate")
    val.add_argument("directory")
    ana = subs.add_parser("analyze")
    ana.add_argument("directory")
    ana.add_argument("--output", required=True)
    ana.add_argument("--permutations", type=int, default=9999)
    args = parser.parse_args(argv)
    try:
        if args.command == "simulate":
            result = simulate(args.output, args.scenario, args.seed, args.n_per_condition)
        elif args.command == "validate":
            result = validate(args.directory)
        else:
            result = analyze(args.directory, args.output, args.permutations)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Validation/action failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0

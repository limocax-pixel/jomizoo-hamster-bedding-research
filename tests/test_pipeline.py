import csv
import json
import math
import tempfile
import unittest
from pathlib import Path
from jomizoo_bedding.cli import (ORIGIN, aggregate_bench, aggregate_daily, analyze, digest, kaplan_meier, permutation_test, read_csv, simulate, validate, wilson, write_csv, write_json)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        simulate(self.data, n_per_condition=4)

    def tearDown(self):
        self.tmp.cleanup()

    def change(self, filename, callback):
        rows = read_csv(self.data / filename)
        callback(rows)
        write_csv(self.data / filename, rows)
        manifest = json.loads((self.data / "manifest.json").read_text())
        manifest["files"][filename] = {"sha256": digest(self.data / filename), "rows": len(rows)}
        write_json(self.data / "manifest.json", manifest)

    def test_reproducible_bytes(self):
        second = self.root / "second"
        simulate(second, n_per_condition=4)
        for name in ("animals.csv", "daily_activity.csv", "bench.csv", "manifest.json"):
            self.assertEqual((self.data/name).read_bytes(), (second/name).read_bytes())

    def test_all_scenarios_validate(self):
        for scenario in ("null", "modest", "plateau"):
            directory = self.root / scenario
            result = simulate(directory, scenario=scenario, n_per_condition=2)
            self.assertTrue(result["valid"])
            self.assertEqual(result["animals"], 14)
            self.assertEqual(result["independent_bench_batches"], 24)

    def test_hash_tampering(self):
        with (self.data/"animals.csv").open("a") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(ValueError, "SHA256"):
            validate(self.data)

    def test_mixed_provenance_even_with_updated_hash(self):
        self.change("animals.csv", lambda rows: rows[0].update(data_origin="OBSERVED"))
        with self.assertRaisesRegex(ValueError, "provenance"):
            validate(self.data)

    def test_units_not_silently_converted(self):
        path = self.data/"manifest.json"
        manifest = json.loads(path.read_text())
        manifest["units"]["depth_cm"] = "mm"
        write_json(path, manifest)
        with self.assertRaisesRegex(ValueError, "Unit"):
            validate(self.data)

    def test_unknown_early_censoring_not_failure(self):
        self.change("animals.csv", lambda rows: rows[0].update(followup_days=13, latency_days=13, event_observed=0, burrow_by_day14=0))
        with self.assertRaisesRegex(ValueError, "censoring"):
            validate(self.data)

    def test_inadequate_surveillance_not_negative(self):
        self.change("animals.csv", lambda rows: rows[0].update(monitoring_coverage_fraction=.7, endpoint_observable=0, followup_days=14, latency_days=14, event_observed=0, burrow_by_day14=0))
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate(self.data)

    def test_confirmed_positive_does_not_require_high_total_coverage(self):
        self.change("animals.csv", lambda rows: rows[0].update(monitoring_coverage_fraction=.7, endpoint_observable=0, followup_days=14, latency_days=2, event_observed=1, burrow_by_day14=1))
        self.assertTrue(validate(self.data)["valid"])
        out = self.root / "positive-analysis"
        analyze(self.data, out, permutations=9)
        payload = json.loads((out/"analysis.json").read_text())
        source = read_csv(self.data/"animals.csv")[0]
        curve = payload["studies"][source["study"]]["descriptive_kaplan_meier"][source["condition"]]["curve"]
        self.assertTrue(any(point["day"] == 2 for point in curve))

    def test_all_missing_secondary_observation_is_not_zero_behavior(self):
        def zero_exposure(rows):
            for row in rows:
                row.update(observation_minutes=0, digging_minutes=0, exploring_minutes=0, other_minutes=0)
        self.change("daily_activity.csv", zero_exposure)
        self.assertTrue(validate(self.data)["valid"])
        output = self.root/"all-missing-activity"
        analyze(self.data, output, permutations=9)
        summary = read_csv(output/"activity_per_animal.csv")
        self.assertEqual(len(summary), 28)
        self.assertTrue(all(r["digging_fraction"] == "" and r["observed_nights"] == "0" for r in summary))

    def test_nonfinite_and_negative_time(self):
        self.change("animals.csv", lambda rows: rows[0].update(latency_days="nan"))
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            validate(self.data)

    def test_duplicate_night_key(self):
        self.change("daily_activity.csv", lambda rows: rows.append(rows[0].copy()))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(self.data)

    def test_activity_composition(self):
        self.change("daily_activity.csv", lambda rows: rows[0].update(digging_minutes=61))
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_balanced_allocation_and_material_batches(self):
        self.change("animals.csv", lambda rows: rows[0].update(material_batch_id=rows[1]["material_batch_id"]))
        with self.assertRaisesRegex(ValueError, "independent animal material"):
            validate(self.data)

    def test_wilson_numeric_reference(self):
        self.assertAlmostEqual(wilson(0, 10)[1], .2775327998628892)
        self.assertAlmostEqual(wilson(10, 10)[0], .7224672001371107)
        self.assertEqual(wilson(0, 0), [None, None])

    def test_km_tied_events_before_censoring(self):
        curve = kaplan_meier([1, 2, 2, 3], [1, 1, 0, 1])
        self.assertEqual([p["survival"] for p in curve], [1.0, .75, .5, 0.0])
        self.assertEqual(kaplan_meier([2, 14], [0, 0])[-1]["survival"], 1)

    def test_constant_binary_outcomes_separation_safe(self):
        rows = read_csv(self.data/"animals.csv")
        for value in ("0", "1"):
            subset = [dict(r, burrow_by_day14=value) for r in rows if r["study"] == "S1"]
            self.assertEqual(permutation_test(subset, iterations=99)["p_value"], 1.0)

    def test_unknown_group_no_test(self):
        rows = read_csv(self.data/"animals.csv")
        rows = [dict(r, burrow_by_day14="" if r["condition"] == "short_35" else "1") for r in rows if r["study"] == "S1"]
        self.assertIsNone(permutation_test(rows, iterations=9)["p_value"])

    def test_no_pseudoreplication(self):
        activity = aggregate_daily(read_csv(self.data/"daily_activity.csv"))
        bench = aggregate_bench(read_csv(self.data/"bench.csv"))
        self.assertEqual(len(activity), 28)
        self.assertEqual(len(bench), 24)
        self.assertTrue(all(b["technical_replicates"] == 3 for b in bench))
        first = activity[0]
        raw = [r for r in read_csv(self.data/"daily_activity.csv") if r["animal_id"] == first["animal_id"]]
        expected = sum(float(r["digging_minutes"]) for r in raw)/sum(float(r["observation_minutes"]) for r in raw)
        self.assertAlmostEqual(first["digging_fraction"], expected)

    def test_analysis_deterministic_and_watermarked(self):
        first, second = self.root/"analysis1", self.root/"analysis2"
        analyze(self.data, first, permutations=99)
        analyze(self.data, second, permutations=99)
        self.assertEqual((first/"analysis.json").read_bytes(), (second/"analysis.json").read_bytes())
        self.assertIn("SYNTHETIC — NOT OBSERVED", (first/"SYNTHETIC_primary_endpoint.svg").read_text())
        report = json.loads((first/"analysis.json").read_text())
        self.assertEqual(report["data_origin"], ORIGIN)
        self.assertNotIn("NaN", (first/"analysis.json").read_text())

    def test_no_overwrite(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            simulate(self.data)


if __name__ == "__main__":
    unittest.main()

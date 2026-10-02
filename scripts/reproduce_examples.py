"""Generate all frozen examples without overwriting existing directories."""
import argparse
from pathlib import Path
from jomizoo_bedding.cli import analyze, simulate

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
for scenario in ("null", "modest", "plateau"):
    directory = args.output / scenario
    simulate(directory, scenario=scenario, seed=20261002)
    analyze(directory, directory / "analysis", permutations=9999)
    print(f"SYNTHETIC: reproduced {scenario}")

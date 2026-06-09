import os
import random
import traceback

import numpy as np
from faker import Faker

from data_generation.config.constants import RAW_DIR
from data_generation.context.context_factory import build_base_context
from data_generation.context.context_updater import refresh_context
from data_generation.load_generators import load_all_generators
from data_generation.pipeline.dependency_graph import DEPENDENCIES
from data_generation.pipeline.toposort import topo_sort
from data_generation.registry import REGISTRY

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

fake = Faker()
fake.seed_instance(42)
random.seed(42)
np.random.seed(42)

os.makedirs(RAW_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def run_generation():

    print("=" * 60)
    print(" MegaMart Data Generator (DAG MODE)")
    print("=" * 60)

    load_all_generators()

    ctx = build_base_context()

    order = topo_sort(DEPENDENCIES)

    print(f"\nOUTPUT DIRECTORY: {RAW_DIR}")

    print("\nEXECUTION ORDER:")
    for o in order:
        print(" -", o)

    print("\nGENERATING RAW VERSIONS:")

    errors = []

    for generator_name in order:
        try:

            fn = REGISTRY.get(generator_name)

            if fn is None:
                raise ValueError(f"{generator_name} not registered")

            fn(ctx)

            refresh_context(ctx, generator_name)

        except Exception as e:
            print(f"✗ {generator_name} failed: {e}")
            traceback.print_exc()
            errors.append((generator_name, str(e)))

    print("\n" + "=" * 60)

    if errors:
        print(f"{len(errors)} failures:")
        for name, err in errors:
            print(f"- {name}: {err}")
    else:
        print("✓ ALL GENERATORS COMPLETED")

    print("=" * 60)


if __name__ == "__main__":
    run_generation()

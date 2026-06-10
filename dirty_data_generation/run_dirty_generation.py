import os
import random
import traceback

import numpy as np
from faker import Faker

from dirty_data_generation.config.constants import (
    CLEAN_TABLES,
    DIRTY_DIR,
    DIRTY_PLAN,
)
from dirty_data_generation.context.context_factory import build_base_context
from dirty_data_generation.load_generators import load_all_generators
from dirty_data_generation.registry import REGISTRY

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

fake = Faker()
random.seed(42)
fake.seed_instance(42)
np.random.seed(42)

os.makedirs(DIRTY_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════


def run_dirty_generation():
    print("=" * 60)
    print("  MegaMart Dirty Data Generator")
    print("=" * 60)

    load_all_generators()

    ctx = build_base_context()

    print(f"\nOUTPUT DIRECTORY: {DIRTY_DIR}\n")

    print("TABLES LEFT CLEAN (no dirty version needed):")
    for t in CLEAN_TABLES:
        print(f"  ✓ {t}")

    print("\nGENERATING TABLES:")

    errors = []
    results = []

    for filename, handler_name in DIRTY_PLAN.items():
        try:
            fn = REGISTRY.get(handler_name)

            if fn is None:
                raise ValueError(f"{handler_name} not registered")

            result = fn(ctx)
            if result:
                results.append(
                    {
                        "raw": filename,
                        "dirty": result["file"],
                        "dirty_rows": result["rows"],
                    }
                )

        except Exception as e:
            print(f"  ✗ {filename} failed: {e}")
            traceback.print_exc()
            errors.append((filename, str(e)))

    if errors:
        print(f"  ⚠ {len(errors)} table(s) skipped (files not found or errors above)")
        for name, err in errors:
            print(f"- {name}: {err}")
    else:
        for r in results:
            print(
                f"  ✓ {r['raw']:}"
                f" → "
                f"{r['dirty']:}  "
                f"({r['dirty_rows']:,} rows)"
            )

        print("\n" + "=" * 60)
        print("✓ All Dirty Tables Generated Successfully")

    print("=" * 60)


if __name__ == "__main__":
    run_dirty_generation()

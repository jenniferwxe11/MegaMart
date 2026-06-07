import os

from data_generation.config.constants import RAW_DIR


def save(df, filename):
    path = os.path.join(RAW_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  ✓ {filename}  ({len(df):,} rows)")

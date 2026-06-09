import os

from dirty_data_generation.config.constants import DIRTY_DIR


def save(df, filename):
    path = os.path.join(DIRTY_DIR, filename)
    df.to_csv(path, index=False)

    return {
        "file": filename,
        "rows": len(df),
    }

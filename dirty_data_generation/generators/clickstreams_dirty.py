import random
from typing import Any, Callable

import pandas as pd

from dirty_data_generation.config.constants import BOT_PROB, DUP_PROB
from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.registry import register
from dirty_data_generation.utils.clickstreams_dirty_helpers import (
    assign_corruption_budget,
    assign_session_profile,
    break_cart_persistence,
    duplicate_event,
    field_corruption,
    inject_bot_traffic,
    messy_search_term,
    mismatch_fields,
    missing_fields,
    orphan_sessions,
    populate_wrong_fields,
    time_anomaly,
    wrong_event_sequence,
)
from dirty_data_generation.utils.io_utils import save

Row = dict[str, Any]
CorruptionFunc = Callable[..., Row]


@register("dirty_clickstreams")
def dirty_clickstreams(ctx: GenerationContext):
    df = ctx.clickstreams.clickstreams_df.copy()
    session_profiles = {
        session_id: assign_session_profile() for session_id in df["session_id"].unique()
    }

    dirty_rows = []
    previous_row = None

    for session_id, session_df in df.groupby("session_id"):
        session_rows = session_df.to_dict("records")
        intensity = session_profiles[session_id]

        for row in session_rows:
            dirty_row = row.copy()
            dirty_row["error_types"] = []
            budget = assign_corruption_budget(intensity)

            if budget == 0:
                dirty_rows.append(dirty_row)
                previous_row = dirty_row
                continue

            CORRUPTION_FUNCS: list[CorruptionFunc] = [
                missing_fields,
                populate_wrong_fields,
                mismatch_fields,
                field_corruption,
                time_anomaly,
                break_cart_persistence,
                messy_search_term,
                wrong_event_sequence,
            ]

            funcs = random.sample(
                CORRUPTION_FUNCS, k=min(budget, len(CORRUPTION_FUNCS))
            )

            for func in funcs:
                if func.__name__ == "time_anomaly":
                    dirty_row = func(dirty_row, previous_row)
                elif func.__name__ == "wrong_event_sequence":
                    dirty_row = func(previous_row, dirty_row, session_rows)
                    break
                elif func.__name__ in ("mismatch_fields", "populate_wrong_fields"):
                    dirty_row = func(ctx, dirty_row)
                else:
                    dirty_row = func(dirty_row)

                dirty_rows.append(dirty_row)

            # Controlled duplication
            if random.random() < DUP_PROB[intensity]:
                # Duplicate row
                dup_row = duplicate_event(dirty_row)
                if dup_row is not None:
                    dirty_rows.append(dup_row)

            # Bot injection
            if random.random() < BOT_PROB[intensity]:
                bot_rows = inject_bot_traffic(ctx, dirty_row)
                if bot_rows:
                    dirty_rows.extend(bot_rows)

            previous_row = dirty_row

    # Orphan sessions — sessions with no landing event
    dirty_rows.extend(orphan_sessions(ctx))

    df_dirty = pd.DataFrame(dirty_rows)

    return save(df_dirty, "clickstreams_dirty.csv")

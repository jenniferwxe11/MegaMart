import ast
import json

import pandas as pd

from tests.schema_tests.schemas import TABLE_CONTRACTS

TYPE_CHECKERS = {
    "string": lambda s: s.dropna().apply(lambda x: isinstance(x, str)).all(),
    "int": lambda s: (
        s.dropna()
        .apply(
            lambda x: isinstance(x, (int,)) or (isinstance(x, float) and x.is_integer())
        )
        .all()
    ),
    "float": lambda s: s.dropna().apply(lambda x: isinstance(x, (float, int))).all(),
    "bool": lambda s: s.dropna().isin([True, False]).all(),
    "list[string]": lambda s: s.dropna().apply(_is_list_of_strings).all(),
    "list[dict]": lambda s: s.dropna().apply(_is_list_of_dicts).all(),
}


def _is_list_of_strings(x):
    if isinstance(x, list):
        return all(isinstance(i, str) for i in x)
    if isinstance(x, str):
        try:
            parsed = json.loads(x)
            return isinstance(parsed, list) and all(isinstance(i, str) for i in parsed)
        except Exception:
            try:
                parsed = ast.literal_eval(x)
                return isinstance(parsed, list) and all(
                    isinstance(i, str) for i in parsed
                )
            except Exception:
                return False
    return False


def _is_list_of_dicts(x):
    if isinstance(x, str):
        try:
            x = json.loads(x.replace("'", '"'))
        except Exception:
            return False

    return isinstance(x, list) and all(isinstance(i, dict) for i in x)


def test_schema_contracts_column_types(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        type_rules = contract.get("types", {})
        df = dataframes[table]

        for col, expected_type in type_rules.items():
            checker = TYPE_CHECKERS[expected_type]

            assert checker(df[col]), (
                f"{table}.{col} expected {expected_type}, "
                f"got sample={df[col].head(3).tolist()}"
            )


def test_schema_contracts_date_columns(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        for col in contract.get("date_columns", []):

            series = dataframes[table][col]

            parsed = pd.to_datetime(series, errors="coerce")

            assert (
                parsed[series.notna()].notna().all()
            ), f"{table}.{col} contains invalid dates"


def test_schema_contracts_datetime_columns(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        df = dataframes[table]

        for col in contract.get("datetime_columns", []):

            parsed = pd.to_datetime(df[col], errors="coerce")

            assert (
                parsed[df[col].notna()].notna().all()
            ), f"{table}.{col} contains invalid datetime values"


def test_schema_contracts_primary_keys_unique(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        pk = contract.get("pk")

        if not pk:
            continue

        df = dataframes[table]
        assert not df.duplicated(
            subset=pk
        ).any(), f"{table} contains duplicate primary keys: {pk}"


def test_schema_contracts_unique_columns(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        for col in contract.get("unique_columns", []):
            df = dataframes[table]
            assert not df[df[col].notna()].duplicated(subset=[col]).any()


def test_schema_contracts_unique_combinations(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        for cols in contract.get("unique_combinations", []):
            df = dataframes[table]
            duplicates = df.duplicated(subset=cols, keep=False)

            assert (
                not duplicates.any()
            ), f"{table} has duplicate combinations for {cols}"


def test_schema_contracts_bridge_unique_combinations(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        bridge_rules = contract.get("bridge_unique_combinations", {})

        if not bridge_rules:
            continue

        df = dataframes[table]

        for list_col, unique_cols in bridge_rules.items():
            parent_col = unique_cols[0]
            bridge_col = unique_cols[1]
            rows = []

            for _, row in df.iterrows():
                values = row[list_col] or []
                for value in values:
                    rows.append(
                        {
                            parent_col: row[parent_col],
                            bridge_col: str(value).replace('"', "").strip(),
                        }
                    )

            bridge_df = pd.DataFrame(rows)

            duplicates = bridge_df.duplicated(subset=unique_cols, keep=False)

            assert not duplicates.any(), (
                f"{table}: duplicate bridge combinations " f"found for {unique_cols}"
            )


def test_schema_contracts_foreign_keys_valid(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        if "fk" not in contract:
            continue

        df = dataframes[table]

        for col, (ref_table, ref_col) in contract["fk"].items():
            assert df[col].dropna().isin(dataframes[ref_table][ref_col]).all()


def test_schema_contracts_list_foreign_keys(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        rules = contract.get("list_fk", {})
        df = dataframes[table]

        for col, (ref_table, ref_col) in rules.items():
            values = (
                df[col]
                .explode()
                .dropna()
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.strip()
            )

            values = values[values != ""]

            valid = set(dataframes[ref_table][ref_col].dropna().astype(str))

            invalid = values[~values.isin(valid)]

            assert invalid.empty, (
                f"{table}.{col} contains invalid references "
                f"to {ref_table}.{ref_col}"
            )


def test_schema_contracts_required_columns_exist(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        assert all(c in dataframes[table].columns for c in contract["required"])


def test_schema_contracts_accepted_values(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        df = dataframes[table]

        for col, allowed in contract.get("accepted_values", {}).items():
            invalid = ~df[col].dropna().isin(allowed)

            assert (
                not invalid.any()
            ), f"{table}.{col} contains invalid values. Allowed: {allowed}"


def test_schema_contracts_regex_columns(dataframes):
    for table, contract in TABLE_CONTRACTS.items():
        rules = contract.get("regex", {})
        df = dataframes[table]

        for col, pattern in rules.items():

            series = df[col]

            series = series[series.notna() & (series != "")]

            assert series.astype(str).str.fullmatch(pattern).all()


def test_schema_contracts_list_dict_foreign_keys(dataframes):
    """
    Check that IDs nested inside list[dict] columns reference valid rows.
    """
    for table, contract in TABLE_CONTRACTS.items():
        rules = contract.get("list_dict_fk", {})
        df = dataframes[table]

        for col, rule in rules.items():
            id_key = rule["id_key"]
            ref_table = rule["ref_table"]
            ref_col = rule["ref_col"]

            valid = set(dataframes[ref_table][ref_col].dropna().astype(str))

            values = (
                df[col]
                .explode()
                .dropna()
                .apply(
                    lambda x, id_key=id_key: (
                        x.get(id_key) if isinstance(x, dict) else None
                    )
                )
                .dropna()
                .astype(str)
            )

            invalid = values[~values.isin(valid)]
            assert invalid.empty, (
                f"{table}.{col}['{id_key}'] contains invalid references "
                f"to {ref_table}.{ref_col}: {invalid.unique().tolist()}"
            )


def test_schema_contracts_list_dict_bridge_unique(dataframes):
    """
    Check that (parent_id, nested_id) combinations are unique within list[dict] columns.
    """
    for table, contract in TABLE_CONTRACTS.items():
        rules = contract.get("list_dict_bridge_unique", {})
        df = dataframes[table]

        for col, rule in rules.items():
            id_key = rule["id_key"]
            parent_col = rule["parent_col"]
            bridge_col = rule["bridge_col"]

            rows = []
            for _, row in df.iterrows():
                for entry in row[col] or []:
                    if isinstance(entry, dict) and id_key in entry:
                        rows.append(
                            {
                                parent_col: row[parent_col],
                                bridge_col: str(entry[id_key]),
                            }
                        )

            if not rows:
                continue

            bridge_df = pd.DataFrame(rows)
            duplicates = bridge_df.duplicated(
                subset=[parent_col, bridge_col], keep=False
            )
            assert not duplicates.any(), (
                f"{table}.{col}: duplicate ({parent_col}, {bridge_col}) "
                f"combinations found"
            )

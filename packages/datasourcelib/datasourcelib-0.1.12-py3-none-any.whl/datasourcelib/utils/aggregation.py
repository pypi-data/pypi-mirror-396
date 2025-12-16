
import pandas as pd
from string import Formatter
from typing import Iterable, Any, Dict, List, Optional, Union

def _placeholders(fmt: str) -> List[str]:
    """
    Extract top-level placeholder names from a format string.
    e.g., 'Number {i} is {fname}' -> ['i', ' """
    return [field_name for _, field_name, _, _ in Formatter().parse(fmt) if field_name]

def _safe_str(x) -> str:
    return "" if pd.isna(x) else str(x).strip()

def generate_grouped_summaries(
    df: pd.DataFrame,
    aggregation_field: str,
    row_format: str,
    *,
    header_format: str = "{group_value} has {count} record{plural}.",
    constants: Optional[Dict[str, Union[str, int, float]]] = None,
    drop_empty_groups: bool = True,
    sort_by: Optional[Union[str, Iterable[str]]] = None,
    validate: bool = True
) -> List[Dict[str, Any]]:
    """
    Build grouped summaries strictly when `aggregation_field` exists in `df` and is non-empty.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataset.
    aggregation_field : str
        Column name to group by. Must exist in `df`.
    row_format : str
        Format string applied per row within a group.
        You may use placeholders for any df columns, plus:
          - {i}: 1-based sequence number within group
          - constants you provide (e.g., {title_prefix})
    headertr, optional
        Format string for group headers. Available placeholders:
          - {group_value}: the group key
          - {count}: number of rows in the group
          - {plural}: '' when count==1 else 's'
        Default: "{group_value} has {count} record{plural}."
    constants : dict, optional
        Additional fixed values to be merged into each row's format context.
        Example: {"title_prefix": "Mr"}
    drop_empty_groups : bool, optional
        If True, rows with blank/empty group values are discarded before grouping.
    sort_by : str | Iterable[str] | None, optional
        If provided, sorts rows within each group by these columns before formatting.
    validate : bool, optional
        If True, checks that all placeholders used in `row_format` and `header_format`
        are available (in df columns or computed context). Raises ValueError if missing.

    Returns
    -------
    List[str]
        One formatted string per group (header + row lines joined with spaces).

    Raises
    ------
    ValueError
        - If `aggregation_field` is missing or empty
        - If no non-empty values exist for `aggregation_field` (with drop_empty_groups=True)
        - If required placeholders are missing when `validate=True`
    KeyError
        - If columns referenced in `sort_by` are missing
    """
    # Basic checks
    if df.empty:
        return []

    agg_field = (aggregation_field or "").strip()
    if not agg_field:
        return df.to_dict("records")
    if agg_field not in df.columns:
        raise ValueError(f"aggregation_field '{agg_field}' not found in DataFrame columns: {list(df.columns)}")

    # Prepare working frame
    working = df.copy()
    working[agg_field] = working[agg_field].astype(str).str.strip()

    if drop_empty_groups:
        working = working[working[agg_field].astype(bool)]

    if working.empty:
        raise ValueError(f"No rows with non-empty values found for aggregation_field '{agg_field}'.")

    # Optional sort within groups
    if sort_by is not None:
        sort_cols = [sort_by] if isinstance(sort_by, str) else list(sort_by)
        missing_sort = [c for c in sort_cols if c not in working.columns]
        if missing_sort:
            raise KeyError(f"sort_by columns not found in DataFrame: {missing_sort}")
        working = working.sort_values(sort_cols, kind="stable")

    # Validation of placeholders (if requested)
    if validate:
        df_cols = set(working.columns)
        row_keys = set(_placeholders(row_format))
        header_keys = set(_placeholders(header_format))
        # Context keys provided by the function
        provided_keys = {"i", "group_value", "count", "plural"}
        constant_keys = set((constants or {}).keys())

        missing_row = [k for k in row_keys if k not in df_cols and k not in constant_keys and k not in provided_keys]
        missing_header = [k for k in header_keys if k not in provided_keys and k not in constant_keys and k not in df_cols]
        if missing_row:
            raise ValueError(
                f"row_format references missing keys: {missing_row}. "
                f"Ensure these are either df columns or in `constants`."
            )
        if missing_header:
            raise ValueError(
                f"header_format references missing keys: {missing_header}. "
                f"Use only {{group_value}}, {{count}}, {{plural}} or provide constants."
            )

    # Build summaries per group
    summaries = []
    for group_value, group_df in working.groupby(agg_field, sort=True):
        group_df = group_df.reset_index(drop=True)
        count = len(group_df)
        plural = "" if count == 1 else "s"

        header_ctx = {
            "group_value": _safe_str(group_value),
            "count": count,
            "plural": plural,
            **(constants or {}),
        }
        header = header_format.format(**header_ctx)

        lines = []
        for i, row in enumerate(group_df.to_dict(orient="records"), start=1):
            # Row context = df row + sequence + constants (constants override df if same key)
            row_ctx = {k: _safe_str(v) for k, v in row.items()}
            row_ctx.update({"i": i})
            if constants:
                # Constants override row values with same keys
                row_ctx.update(constants)

            lines.append(row_format.format(**row_ctx))

        content = header + " " + " ".join(lines)
        summaries.append(
            {"content" : content, "id": group_value}
            )

    return summaries

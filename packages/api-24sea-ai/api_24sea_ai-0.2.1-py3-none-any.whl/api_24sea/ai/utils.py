# -*- coding: utf-8 -*-
"""Utility functions for the `api_24sea.ai` package."""
import logging
import math
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from api_24sea import exceptions as E


def process_models_overview(
    m_list: List[Dict[str, Optional[Union[str, int]]]]
) -> pd.DataFrame:
    """Process the models overview list into a DataFrame with additional
    columns. Renames some columns for clarity.

    List of operations:

    - Rename `project_id` to `site`
    - Rename `location_id` to `location`
    - Rename `model_group_id` to `model_group`
    - Rename `name` to `model`
    - Add `statistic`, `site_id`, `location_id`, and `short_hand` columns by
      splitting the `model` name.
    - Rename `units` to `unit_str`
    - Expand rows where `location` is a list/tuple into multiple rows.
    - For rows where `location_id` is 'FLT', derive `location_id` from
      `location` by removing the `site_id` prefix.

    Parameters
    ----------
    m_list : list of dict
        List of models overview dictionaries.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame with additional columns.

    Raises
    ------
    E.ProfileError
        If the model names do not match the expected format.
    """
    df = pd.DataFrame(m_list)
    if df.empty:
        return df
    # Rename project_id to site
    if "project_id" in df.columns:
        df.rename(columns={"project_id": "site"}, inplace=True)
    if "location_id" in df.columns:
        df.rename(columns={"location_id": "location"}, inplace=True)
    if "model_group_id" in df.columns:
        df.rename(columns={"model_group_id": "model_group"}, inplace=True)
    if "name" in df.columns:
        df.rename(columns={"name": "model"}, inplace=True)
    # Add statistic, site_id, location_id, and short_hand columns by
    # splitting the model name.
    # short_hand is the final part, it can contain underscores
    if "model" in df.columns:
        split_model = df["model"].str.split("_", expand=True)
        if split_model.shape[1] >= 5:
            df["statistic"] = split_model.iloc[:, 0]
            df["short_hand"] = (
                split_model.iloc[:, 3:]
                .fillna("")
                .agg("_".join, axis=1)
                .str.rstrip("_")
                .values
            )
            df["location_id"] = split_model.iloc[:, 2]
            df["site_id"] = split_model.iloc[:, 1]
        elif split_model.shape[1] == 4:
            df["statistic"] = split_model.iloc[:, 0]
            df["short_hand"] = split_model.iloc[:, 3]
            df["location_id"] = split_model.iloc[:, 2]
            df["site_id"] = split_model.iloc[:, 1]
        else:
            raise E.ProfileError(
                "\033[31;1mThere was an issue processing the "
                "models overview. The model names do not "
                "match the expected format. Please check your "
                f"input data.\n{m_list}\033[0m"
            )
    if "units" in df.columns:
        df.rename(columns={"units": "unit_str"}, inplace=True)
    is_list = df["location"].apply(lambda x: isinstance(x, (list, tuple)))
    df_expanded = pd.concat(
        [df.loc[~is_list], df.loc[is_list].explode("location")],
        ignore_index=True,
    )
    df_expanded["location"] = df_expanded["location"].str.upper()
    # For floating locations (FLT), derive location_id from location by removing the site_id prefix
    if "location_id" in df_expanded.columns:
        is_flt = df_expanded["location_id"].astype(str).str.upper() == "FLT"
        if is_flt.any():

            def _derive_loc_id(row):
                site_id = str(row.get("site_id", "")).upper()
                loc = str(row.get("location", "")).upper()
                return (
                    loc.replace(site_id, "", 1)
                    if site_id and loc.startswith(site_id)
                    else loc
                )

            df_expanded.loc[is_flt, "location_id"] = df_expanded.loc[
                is_flt
            ].apply(_derive_loc_id, axis=1)

    return df_expanded


def sanitize_for_json(obj: Any) -> Any:
    """
    Sanitize a Python object for JSON serialization.
    Recursively processes dictionaries and lists, converting values that are not
    JSON-friendly (e.g., pandas missing values, NaT, NaN, or non-finite floats)
    to None.

    Parameters
    ----------
    obj : Any
        The object to sanitize. Can be a scalar, list, or dictionary. Nested
        lists and dictionaries are traversed recursively.

    Returns
    -------
    Any
        A sanitized object where:

        - pandas- or NumPy-style missing values (e.g., NaN, NA, NaT) are
          replaced with None.
        - non-finite floats (inf, -inf, nan) are replaced with None.
        - dictionaries and lists are returned with their contents sanitized.
        - other objects are returned unchanged.

    Notes
    -----
    - Only dictionaries and lists are traversed recursively. Other container
      types (e.g., tuples, sets) are returned as-is.
    - This function assumes pandas is available; values are checked with
      `pandas.isna` and `pandas.NaT`. Non-finite floats are detected via
      `math.isfinite`.

    Examples
    --------
    >>> sanitize_for_json({"x": float("inf"), "y": [float("nan"), 1.0]})
    {'x': None, 'y': [None, 1.0]}
    >>> import pandas as pd
    >>> sanitize_for_json({"ts": pd.NaT, "v": pd.NA})
    {'ts': None, 'v': None}
    """

    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    if obj is pd.NaT:
        return None
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def aipi_predictions_to_dataframe(pred) -> pd.DataFrame:
    """
    Convert model predictions into a pandas DataFrame.

    Parameters
    ----------
    pred : list of (list of dict or dict or Response)
        Iterable of prediction groups. Each group is typically a list of dicts.
        Each dict should contain exactly two fields: a timestamp key and one
        metric key (the metric name). Items may also be Response-like objects
        exposing .json(), or dicts that wrap the list under one of the keys
        {'predictions', 'data', 'result', 'results', 'items'}. A single dict
        with a timestamp field is treated as a one-row group.

    Returns
    -------
    pandas.DataFrame
        DataFrame indexed by the union of timestamps (UTC). One column per
        metric name. If duplicate metric names occur, numeric suffixes are
        appended to make them unique.

    Notes
    -----
    - Timestamp key is detected among {'timestamp', 'time', 'ts'} or inferred
      from keys containing 'time' or 'ts'.
    - Invalid or duplicate timestamps within a group are dropped (keep last).
    - Unknown or empty groups are skipped with a logged message.

    Raises
    ------
    ValueError
        If a Response-like item fails to parse via .json(), or when a dict
        wrapper does not contain a known list key.
    TypeError
        If a prediction element has an unsupported type or a group is not a
        list of dicts.
    """
    # Resolve logger if available in the notebook, else fallback to module logger
    _log = globals().get("logger", None)
    if _log is None:
        _log = logging.getLogger(__name__)

    def _extract_list_of_dicts(item):
        # Unwrap Response-like objects
        if hasattr(item, "json") and callable(getattr(item, "json")):
            try:
                item = item.json()
            except Exception as exc:
                # fmt: off
                raise ValueError("Failed to parse .json() from prediction "
                                 f"item: {exc}") from exc
                # fmt: on
        # If it's a dict, try common containers
        if isinstance(item, dict):
            for k in ("predictions", "data", "result", "results", "items"):
                if k in item and isinstance(item[k], list):
                    return item[k]
            # Or a single prediction dict itself
            if any(k in item for k in ("timestamp", "time", "ts")):
                return [item]
            # fmt: off
            raise ValueError("Prediction dict did not contain a known list key "
                             "or a timestamp field.")
            # fmt: on

        # Already a list of dicts
        if isinstance(item, list):
            return item

        raise TypeError(f"Unsupported prediction element type: {type(item)}")

    # Normalize to list[list[dict]]
    groups: list[list[dict]] = []
    for idx, item in enumerate(pred or []):
        lod = _extract_list_of_dicts(item)
        if not lod:
            _log.warning(f"Predictions group #{idx} is empty; skipping.")
            continue
        if not isinstance(lod[0], dict):
            raise TypeError(f"Predictions group #{idx} is not a list of dicts.")
        groups.append(lod)

    columns = {}
    for g_idx, lod in enumerate(groups):
        # Determine timestamp key
        ts_key = None
        for cand in ("timestamp", "time", "ts"):
            if cand in lod[0]:
                ts_key = cand
                break
        if ts_key is None:
            # Try to infer any key that looks like timestamp
            candidates = [k for k in lod[0].keys() if "time" in k or "ts" in k]
            if candidates:
                ts_key = candidates[0]
        if ts_key is None:
            # fmt: off
            _log.warning(f"Group #{g_idx}: no timestamp-like key found; "
                         "skipping.")
            # fmt: on
            continue

        # Determine metric key (the non-timestamp key). Prefer a stable common
        # key across rows.
        non_ts_keys = set()
        for d in lod:
            non_ts_keys.update([k for k in d.keys() if k != ts_key])
        if not non_ts_keys:
            _log.warning(f"Group #{g_idx}: no metric key found; skipping.")
            continue
        if len(non_ts_keys) > 1:
            # fmt: off
            _log.info(f"Group #{g_idx}: multiple metric keys detected "
                      f"{sorted(non_ts_keys)}; using the first.")
            # fmt: on
        metric_key = sorted(non_ts_keys)[0]
        metric_name = metric_key  # base column name

        # Build DataFrame for this group
        df_g = pd.DataFrame(lod)
        # Keep only the two relevant columns; tolerate missing in some rows
        cols = [c for c in (ts_key, metric_key) if c in df_g.columns]
        if len(cols) < 2:
            # fmt: off
            _log.warning(f"Group #{g_idx}: missing required columns {ts_key} "
                         f"or {metric_key}; skipping.")
            # fmt: on
            continue

        # Coerce timestamps to UTC datetime, drop invalids and duplicates
        df_g[ts_key] = pd.to_datetime(df_g[ts_key], utc=True, errors="coerce")
        df_g = (
            df_g.dropna(subset=[ts_key])
            .drop_duplicates(subset=[ts_key], keep="last")
            .set_index(ts_key)
        )

        # Ensure unique column name if collisions happen
        name = metric_name
        dup_i = 1
        while name in columns:
            name = f"{metric_name}__{dup_i}"
            dup_i += 1

        # Rename the series to the disambiguated name
        s = df_g[metric_key].rename(name)
        columns[name] = s

    if not columns:
        return pd.DataFrame()

    # Use the dict so keys (unique names) become the DataFrame columns
    df = pd.concat(columns, axis=1)
    df.index.name = "timestamp"
    df = df.sort_index()
    return df

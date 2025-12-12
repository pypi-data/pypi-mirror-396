# -*- coding: utf-8 -*-
"""Data signals types."""
import datetime
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy

from api_24sea import exceptions as E  # type: ignore[attr-defined]
from api_24sea import utils as U  # type: ignore[attr-defined]

from . import utils as AIU


# Shared base class for data signal schemas
class AIPredictionsInputSchema(U.BaseModel):
    """
    Shared base schema for ai input requests.
    Includes common fields and validation logic for timestamp, sites, locations,
    models, and headers. Inherit from this class to create specific schemas for
    data retrieval and stats retrieval.
    """

    start_timestamp: Union[datetime.datetime, str]
    end_timestamp: Union[datetime.datetime, str]
    sites: Optional[Union[str, List[str]]] = None
    locations: Optional[Union[str, List[str]]] = None
    models: Union[str, List[str]]
    as_dict: Optional[bool] = False
    as_star_schema: Optional[bool] = False
    headers: Optional[Dict[str, str]] = {"accept": "application/json"}

    @U.field_validator("start_timestamp", "end_timestamp", mode="before")
    def validate_timestamp(cls, v: Union[datetime.datetime, str]) -> str:
        """Validate and format timestamp input."""
        if isinstance(v, str):
            try:
                datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ").astimezone(
                    datetime.timezone.utc
                )
            except Exception:
                try:
                    from shorthand_datetime import parse_shorthand_datetime

                    return parse_shorthand_datetime(v).strftime(  # type: ignore
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                except Exception as exc:
                    raise ValueError(
                        "\033[31mIncorrect start timestamp format, expected "
                        "one of the following formats:"
                        "\n               \033[1m• 'YYYY-MM-DDTHH:MM:SSZ'"
                        "\033[22m, \n               \033[1m• shorthand_datetime"
                        "-compatible string\033[22m "
                        "(https://pypi.org/project/shorthand-datetime/), or, "
                        "\n               "
                        "\033[1m• datetime.datetime\033[22m object.\033[0m\n\n"
                        "Exception originated from\n" + str(exc)
                    )
        if isinstance(v, datetime.datetime):
            return v.strftime("%Y-%m-%dT%H:%M:%SZ")
        return v

    @U.field_validator("sites", "locations", mode="before")
    def validate_sites_locations(cls, v):
        """Validate and format sites and locations input."""
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            v = [str(item).lower() for item in v]
        return v

    @U.field_validator("models", mode="before")
    def validate_models(cls, v):
        """Validate and format models input."""
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            # fmt: off
            v = [item.replace(" ", ".*")
                    #  .replace("_", ".*")
                     .replace("-", ".*") for item in v]
            # fmt: on
        return "|".join(v)

    @U.field_validator("headers", mode="before")
    def validate_headers(cls, v):
        """Validate and format headers input."""
        if v is None:
            return {"accept": "application/json"}
        return v

    @property
    def query_str(self) -> str:
        """Build a query string based on self."""
        return build_query_str(self)

    # @lru_cache
    def get_selected_models(
        self, df: Optional[pd.DataFrame], log: bool = True
    ) -> pd.DataFrame:
        """Calculate the selected models DataFrame based on a df (models
        overview) and the query object."""
        if df is None:
            raise ValueError("The provided DataFrame cannot be None.")
        return get_selected_models(self, df, log)

    # @lru_cache
    def group_models(self, df: Optional[pd.DataFrame]) -> DataFrameGroupBy:
        """Group models by site and location."""
        if df is None:
            raise ValueError("The provided DataFrame cannot be None.")
        s_m = self.get_selected_models(df, False)
        return s_m.assign(
            site=lambda x: x["site"].str.lower(),
            location=lambda x: x["location"].str.upper(),
        ).groupby(["site", "location"])


def build_query_str(query: AIPredictionsInputSchema) -> str:
    """
    Build a query string based on the provided BaseDataSignalSchema instance.

    Parameters
    ----------
    query : BaseDataSignalSchema
        The query object containing the filtering criteria.

    Returns
    -------
    str
        The constructed query string.
    """
    if query.sites is None and query.locations is None:
        return "slug.str.contains(@query.models, case=False, regex=True)"
    elif query.sites is None and query.locations is not None:
        return (
            "(location.str.lower() == @query.locations or location_id.str.lower() == @query.locations) "
            "and slug.str.contains(@query.models, case=False, regex=True)"
        )
    elif query.locations is None and query.sites is not None:
        return (
            "(site.str.lower() == @query.sites or site_id.str.lower() == @query.sites) "
            "and slug.str.contains(@query.models, case=False, regex=True)"
        )
    else:
        return (
            "(site_id.str.lower() == @query.sites or site.str.lower() == @query.sites) "
            "and (location.str.lower() == @query.locations or location_id.str.lower() == @query.locations) "
            "and slug.str.contains(@query.models, case=False, regex=True)"
        )


class ModelsOverviewDjangoResponseSchema(U.BaseModel):
    """Schema for the models overview response."""

    name: str
    slug: str
    project_id: str
    location_id: str
    model_group_id: str
    latest_version: int
    description: str
    units: str
    start_validity: str
    training_date: str
    db_connector: str
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None

    @U.field_validator("latest_version", mode="before")
    def coerce_latest_version(cls, v):
        if v is None:
            raise ValueError("The 'latest_version' field is required.")
        return int(v)

    # fmt: off
    @U.field_validator("name", "slug", "project_id", "location_id",
                       "model_group_id", "description", "units",
                       "start_validity", "training_date", "db_connector",
                       "start_timestamp", "end_timestamp", mode="before")
    def ensure_string(cls, v):
        if v is None:
            return None
        return str(v)
    @U.field_validator("start_validity", "training_date",
                       "start_timestamp", "end_timestamp", mode="before")
    # fmt: on
    def validate_iso8601_timestamps(cls, v, field):
        if v is None:
            if field.field_name in ("start_timestamp", "end_timestamp"):
                return None
            raise ValueError(f"The '{field.field_name}' field cannot be None.")
        try:
            if isinstance(v, datetime.datetime):
                dt = v
            else:
                from shorthand_datetime import parse_shorthand_datetime

                dt = parse_shorthand_datetime(str(v))  # type: ignore
            if isinstance(dt, datetime.datetime):
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                else:
                    dt = dt.astimezone(datetime.timezone.utc)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            # Fallback to string if parser returned a non-datetime value
            return str(dt)
        except Exception as exc:
            # fmt: off
            raise ValueError("Invalid ISO8601 timestamp for "
                             f"'{field.field_name}': {v}. {exc}") from exc
            # fmt: on

    # @classmethod
    # def validate(
    #     cls, data: List[Dict[str, Optional[Union[str, int]]]]
    # ) -> List[Dict[str, Optional[Union[str, int]]]]:
    #     """Validate a list of model overview dictionaries."""
    #     validated_data: List[Dict[str, Optional[Union[str, int]]]] = []
    #     for item in data:
    #         validated_item = cls(**item)
    #         validated_data.append(validated_item.dict())
    #     return validated_data


class AIPIPredictionsInputSchema(U.BaseModel):
    """Schema for the AIPI predictions input.

    Validates and normalizes the inputs of `core.AsyncAPI.get_aipi_predictions`:

    - ``models`` can be a string or list of strings; coerced to a non-empty list
      of stripped strings.
    - ``data`` can be a pandas DataFrame or a list of dictionaries; validated
      and exposed as a JSON-serializable payload via `payload()`.
    - ``timeout`` is an integer in seconds.
    """

    models: Union[str, List[str]]
    data: List[Dict[str, Any]]
    timeout: int = 1800

    @U.field_validator("models", mode="before")
    def normalize_models(cls, v):
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            v = [str(m).strip() for m in v if str(m).strip()]
        if not v:
            raise ValueError("At least one model must be provided.")
        return v

    @U.field_validator("data", mode="before")
    def validate_data(cls, v):
        if isinstance(v, pd.DataFrame):
            if v.empty:
                raise ValueError("`data` DataFrame cannot be empty.")
            if "timestamp" not in v.columns:
                raise ValueError(
                    "`data` DataFrame must contain a 'timestamp' column."
                )
            return v
        if isinstance(v, list):
            if not v:
                raise ValueError("`data` list cannot be empty.")
            if not all(isinstance(item, dict) for item in v):
                raise ValueError(
                    "`data` must be a pandas DataFrame or a list of "
                    "dictionaries."
                )
            if not all("timestamp" in item for item in v):
                raise ValueError(
                    "Each dictionary in `data` list must contain a 'timestamp' "
                    "key."
                )
            return v
        raise ValueError(
            "`data` must be a pandas DataFrame or a list of dictionaries."
        )

    def payload(self) -> Any:
        """Return a sanitized list-of-dicts payload for HTTP JSON body.

        Coerce keys to strings to satisfy typing and API requirements.
        """
        if isinstance(self.data, pd.DataFrame):
            records = self.data.to_dict(orient="records")
            # Drop 'timestamp' column coming from DataFrame as server may infer
            # it separately
            normalized: List[Dict[str, Any]] = [
                {str(k): v for k, v in rec.items() if str(k) != "timestamp"}
                for rec in records
            ]
        else:
            # For list input, preserve the dictionaries as-is
            # (including 'timestamp')
            normalized = [
                {str(k): v for k, v in rec.items()} for rec in self.data
            ]
        return AIU.sanitize_for_json(normalized)


def get_selected_models(
    query: AIPredictionsInputSchema,
    models_overview: pd.DataFrame,
    log: bool = True,
) -> pd.DataFrame:
    """
    Extract the selected models DataFrame based on the models_overview,
    and the query object.

    Parameters
    ----------
    models_overview : pd.DataFrame
        The models overview DataFrame.
    query_str : str
        The query string to filter models.
    log : bool, optional
        Whether to log the selected models, by default True.

    Returns
    -------
    pd.DataFrame
        The filtered and sorted models DataFrame.
    """
    selected = models_overview.query(query.query_str).sort_values(
        ["site", "location", "model_group", "short_hand", "statistic"],
        ascending=[True, True, False, True, True],
    )
    if log:
        logging.info("\033[32;1mModels selected for the query:\033[0m\n")
        logging.info(selected[["model", "unit_str", "site", "location"]])
    if selected.empty:
        raise E.DataSignalsError(
            "\033[31;1mNo models found for the given query.\033[0m"
            "\033[33;1m\nHINT:\033[22m Check \033[2msites\033[22m, "
            "\033[2mlocations\033[22m, and \033[2mmodels\033[22m "
            "provided.\033[0m\n\n"
            "Provided:\n"
            f"  • sites: {query.sites}\n"
            f"  • locations: {query.locations}\n"
            f"  • models: {query.models}\n"
        )
    return selected


class AISchemasInputSchema(U.BaseModel):
    """
    Schema for the AI schemas input.

    Validates and normalizes the inputs of `core.AsyncAPI.get_schemas`:

    - ``models`` can be a string or list of strings; coerced to a non-empty list
      of stripped strings.
    - ``sites`` can be a string or list of strings; coerced to a list of
      stripped lowercase strings, or None.
    - ``locations`` can be a string or list of strings; coerced to a list of
      stripped lowercase strings, or None.
    - ``timeout`` is an integer in seconds.
    - ``as_dict`` is a boolean indicating whether to return the response as a
      list of dictionaries (True) or as a pandas DataFrame (False).
    - ``headers`` is a dictionary of HTTP headers to include in the request.
    """

    models: Union[str, List[str]]
    sites: Optional[Union[str, List[str]]] = None
    locations: Optional[Union[str, List[str]]] = None
    timeout: int = 30
    as_dict: Optional[bool] = False
    headers: Optional[Dict[str, str]] = {"accept": "application/json"}

    @U.field_validator("models", mode="before")
    def normalize_models(cls, v):
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            v = [str(m).strip() for m in v if str(m).strip()]
        if not v:
            raise ValueError("At least one model must be provided.")
        return v

    @U.field_validator("sites", "locations", mode="before")
    def normalize_sites_locations(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            v = [str(item).lower().strip() for item in v if str(item).strip()]
        if not v:
            return None
        return v

    @U.field_validator("headers", mode="before")
    def validate_headers(cls, v):
        if v is None:
            return {"accept": "application/json"}
        return v

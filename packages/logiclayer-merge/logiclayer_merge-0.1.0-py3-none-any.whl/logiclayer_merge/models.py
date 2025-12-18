from collections.abc import Sequence
from typing import Literal, Optional, TypedDict, Union

import hashlib
import polars as pl
from pydantic import Field, model_validator
from pydantic import BaseModel as PydanticBaseModel
from tesseract_olap.query import DataMultiQuery, DataRequest
from tesseract_olap.schema import SchemaTraverser, DataType
from tesseract_olap.backend.models import Result


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


JoinStrategy = Literal[
    "inner",
    "left",
    "right",
    "full",
    "semi",
    "anti",
    "cross",
    "outer",
]


class JoinOnColumns(BaseModel):
    """Specifies the columns to be used in a merge operation, when their names are different."""

    left_on: Union[str, list[str]]
    right_on: Union[str, list[str]]


class JoinIntent(BaseModel):
    """Specifies the intent of the user to perform a Join operation between 2 datasets."""

    on: Union[str, list[str], JoinOnColumns, None] = None
    how: JoinStrategy = "left"
    suffix: Optional[str] = None
    validate_relation: Literal["m:m", "m:1", "1:m", "1:1"] = "m:m"
    join_nulls: bool = False
    coalesce: Optional[bool] = None


class PaginationIntent(BaseModel):
    limit: int = 0
    offset: int = 0


class MultiRequest(BaseModel):
    """Describes a request done by the user."""

    requests: list[DataRequest]
    joins: list[JoinIntent] = Field(default_factory=list)
    pagination: PaginationIntent = Field(default_factory=PaginationIntent)

    @model_validator(mode="before")
    @classmethod
    def parse_request(cls, value: object):
        if isinstance(value, dict):
            requests = value.get("queries") or value.get("requests", [])
            if not isinstance(requests, Sequence):
                msg = "Invalid 'requests' parameter: it must be a list of dictionaries containing the request parameters of the queries to be merged."
                raise ValueError(msg)

            request_count = len(requests)
            if not request_count > 1:
                msg = "At least 2 DataRequest objects are required to perform a join operation."
                raise ValueError(msg)

            joins = value.get("joins", [])
            if not isinstance(joins, Sequence):
                msg = "Invalid 'joins' parameter. It must be a list of dictionaries with the parameters to use."
                raise ValueError(msg)

            if not joins:
                joins = [{}] * (request_count - 1)
            elif len(joins) == 1:
                joins = list(joins) * (request_count - 1)
            elif len(joins) == request_count - 1:
                pass
            else:
                msg = f"Invalid 'joins' parameter. It must be a list of objects with the parameters to use; this list must contain 1 object (if you intend to apply the same parameters to all queries), {request_count - 1} objects (one per each step of this join operation), or left empty/unset to let the server attempt to guess the parameters."
                raise ValueError(msg)

            return {
                "requests": requests,
                "joins": joins,
                "pagination": value.get("pagination", "0,0"),
            }
        return value

    def build_query(self, schema: SchemaTraverser) -> "DataMultiQuery":
        """Generate a DataMultiQuery object from the params in this request."""
        return DataMultiQuery.from_requests(schema, self.requests, self.joins)


class _JoinParameters(TypedDict, total=False):
    """Describe the keyword args needed for a polars.DataFrame.join operation."""

    on: Union[str, list[str]]
    coalesce: Optional[bool]
    join_nulls: bool
    left_on: Union[str, list[str]]
    right_on: Union[str, list[str]]
    suffix: str
    validate: Literal["m:m", "m:1", "1:m", "1:1"]


class JoinStep:
    data: pl.DataFrame
    keys: list[str]
    statuses: list[str]

    def __init__(
        self,
        data: pl.DataFrame,
        *,
        keys: list[str],
        statuses: list[str],
    ):
        self.data = data
        self.keys = keys
        self.statuses = statuses

    def join_with(self, result: Result, join: JoinIntent):
        params: _JoinParameters = {
            "suffix": join.suffix or "_",
            "validate": join.validate_relation,
            "join_nulls": join.join_nulls,
            "coalesce": join.coalesce,
        }

        if isinstance(join.on, (str, list)):
            params.update(on=join.on)
        elif isinstance(join.on, JoinOnColumns):
            params.update(left_on=join.on.left_on, right_on=join.on.right_on)

        return JoinStep(
            self.data.join(result.data, how=join.how, **params),
            keys=[*self.keys, result.cache["key"]],
            statuses=[*self.statuses, result.cache["status"]],
        )

    def get_result(self, pagi: PaginationIntent):
        df = self.data

        cache_key = "/".join(self.keys).encode("utf-8")
        return Result(
            data=df.slice(pagi.offset, pagi.limit or None),
            columns={
                k: DataType.from_polars(v) for k, v in dict(zip(df.columns, df.dtypes)).items()
            },
            cache={
                "key": hashlib.md5(cache_key, usedforsecurity=False).hexdigest(),
                "status": ",".join(self.statuses),
            },
            page={"limit": pagi.limit, "offset": pagi.offset, "total": df.height},
        )

    @classmethod
    def new(cls, result: Result):
        return cls(
            result.data,
            keys=[result.cache["key"]],
            statuses=[result.cache["status"]],
        )


class QueryRequest(BaseModel):
    url: str
    data: Optional[str] = None
    headers: Optional[str] = None


class MergeParams(BaseModel):
    query_left : QueryRequest
    query_right: QueryRequest
    pagination: PaginationIntent = Field(default_factory=PaginationIntent)
    join: JoinIntent


class CubeRequest(BaseModel):
    cube_name: list[str]
    locale: str
    show_all: Optional[bool] = False


class ColumnsRequest(BaseModel):
    columns: list[str]


class FileParams(BaseModel):
    filename: str
    annotations: dict

    def get_annotations(self):
        return self.annotations
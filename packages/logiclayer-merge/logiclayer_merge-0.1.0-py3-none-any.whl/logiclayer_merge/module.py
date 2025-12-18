from typing import Annotated, Optional

import datetime
import logiclayer as ll
import polars as pl
import httpx
from urllib.parse import urlparse

from fastapi import Depends, Header, Query, status
from fastapi.responses import JSONResponse
from tesseract_olap import OlapServer
from tesseract_olap.logiclayer.response import data_response, ResponseFormat
from tesseract_olap.schema.public import TesseractSchema, TesseractCube
from tesseract_olap.schema import DataType

from src.logiclayer_merge import __title__, __version__
from src.logiclayer_merge.models import JoinStep, MultiRequest, MergeParams, CubeRequest, ColumnsRequest, Result, FileParams
from src.logiclayer_merge.exceptions import DomainNotAllowedException, InvalidUrlException


def auth_token(
    header_auth: Annotated[Optional[str], Header(alias="authorization")] = None,
    header_jwt: Annotated[Optional[str], Header(alias="x-tesseract-jwt")] = None,
    query_token: Annotated[Optional[str], Query(alias="token")] = None,
):
    if header_jwt:
        return ll.AuthToken(ll.AuthTokenType.JWTOKEN, header_jwt)
    if query_token:
        return ll.AuthToken(ll.AuthTokenType.SEARCHPARAM, query_token)
    if header_auth:
        if header_auth.startswith("Bearer "):
            return ll.AuthToken(ll.AuthTokenType.JWTOKEN, header_auth[7:])
        if header_auth.startswith("Basic "):
            return ll.AuthToken(ll.AuthTokenType.BASIC, header_auth[6:])
        if header_auth.startswith("Digest "):
            return ll.AuthToken(ll.AuthTokenType.DIGEST, header_auth[7:])
    return None


class MergeModule(ll.LogicLayerModule):
    """Endpoint merging module.

    Allows to merge the results of other LogicLayer modules in a single response.
    """

    def __init__(self, olap: Optional[OlapServer] = None, allowed_domains: Optional[str] = "", **kwargs):
        super().__init__(**kwargs)
        self.tesseract = olap
        self.cubes = None
        self.adjacency_list = None
        self.ad_cube_measure = None
        self.cube_to_measures = None
        self.allowed_domains = allowed_domains

    def startup_tasks(self):
        """Startup tasks."""
        self.set_allowed_domains()
        self.set_cubes()
        self.build_adjacency_list()
        self.preprocess_cube()

    def set_allowed_domains(self):
        """Set the allowed domains for this module."""
        if self.allowed_domains != "":
            self.allowed_domains = self.allowed_domains.split(',')

    def set_cubes(self, cubes: list[str] = None):
        """Set the cube registry for this module."""
        if cubes is None:
            cubes = None
        self.cubes = TesseractSchema.from_entity(self.tesseract.schema, show_all=True).cubes

    def build_adjacency_list(self):
        adjacency_list = {}
        for cube in self.cubes:
            cube_name = cube.name
            adjacency_list[cube_name] = []
            levels = [
                level 
                for dim in cube.dimensions 
                for hier in dim.hierarchies
                for level in hier.levels]
            for lvl in levels:
                level_name = lvl.name
                adjacency_list[cube_name].append(level_name)
        reversed_adj = {}
        for cube, lvl in adjacency_list.items():
            for level in lvl:
                reversed_adj[level] = reversed_adj.get(level, []) + [cube]

        self.adjacency_list =  {**adjacency_list, **reversed_adj}

    def preprocess_cube(self):
        ad_cube_measure = {}
        cube_to_measures = {}

        for c in self.cubes:
            for m in c.measures:
                ad_cube_measure[c.name] = ad_cube_measure.get(c.name, []) +[m.name+ "@"+c.name]
                cube_to_measures[c.name] = cube_to_measures.get(c.name, []) +[m.name]
        
        self.ad_cube_measure = ad_cube_measure
        self.cube_to_measures = cube_to_measures

    @ll.route("GET", "/")
    def status(self) -> ll.ModuleStatus:
        """Return the current status of the internals of this module."""
        return ll.ModuleStatus(module=__title__, version=__version__, debug=self.debug, status="ok")

    @ll.route("POST", "/query.{extension}")
    def multiquery_data(
        self,
        extension: ResponseFormat,
        params: MultiRequest,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ):
        """Execute a request for joining data from the server."""
        # Add role data to all params, overwrite possible user injections
        roles = self.auth.get_roles(token)
        for request in params.requests:
            request.roles = roles

        query = params.build_query(self.tesseract.schema)

        with self.tesseract.session() as session:
            result = session.fetch_dataframe(query.initial)
            step = JoinStep.new(result)

            for query_right, join_params in query.join_with:
                result = session.fetch_dataframe(query_right)
                join_params.suffix = f"_{query_right.cube.name}"
                step = step.join_with(result, join_params)

        result = step.get_result(params.pagination)

        return data_response(
            query,
            result,
            extension
        )

    @ll.route("GET", "/structures")
    def get_data_structures(
        self, 
    ):
        """Send adjacency list and cube to measures mapping"""
        return JSONResponse(content=
            {
                "ad_cube_measure": self.ad_cube_measure,
                "cube_to_measures": self.cube_to_measures,
                "adjacency_list": self.adjacency_list,
            },
        )

    @ll.route("GET", "/cubes")
    def get_cubes(
        self,
    ):
        """send available cubes"""
        return self.cubes
    
    @ll.route("GET", "/allowed")
    def get_allowed_domains(
        self,
    ):
        """send allowed domains"""
        return self.allowed_domains

    @ll.route("POST", "/cubes/dimensions_measures")
    def get_cubes_dim(
        self,
        r: CubeRequest
    ):
        """For selected cubes send dimensions and measures"""
        try:
            data = []
            for cube in r.cube_name:
                cube = self.tesseract.schema.get_cube(cube)
                cube= TesseractCube.from_entity(cube, locale=r.locale, show_all=r.show_all)
                data.append(cube)
            return data

        except:
            return JSONResponse({"Status": "ok", "Message": "Cube not found"})

    @ll.route("POST", "/cubes/merge_options")
    def get_merge_options(
        self,
        r: ColumnsRequest
    ):
        """for dimensions selected send available cubes to merge on or available cubes+measures"""
        try:
            option_sets = list(set.intersection(*[set(self.adjacency_list.get(c, [])) for c in r.columns]))
            if option_sets:
                measures_lists = [self.cube_to_measures.get(c, []) for c in option_sets]
                option_measures = list(set.intersection(*[set(measures) for measures in measures_lists]))
            else:
                option_measures = []
            return JSONResponse({"option_sets": option_sets, "option_measures": option_measures})

        except:
            return JSONResponse({"Status": "ok", "Message": "No Match Found"})

    @ll.route("POST", "/cubes/merge.{extension}")
    async def merge_cubes(
        self,
        extension: ResponseFormat,
        merge_params: MergeParams
    ):
        try:
            join_params = merge_params.join
            left_params = merge_params.query_left
            right_params = merge_params.query_right
            pagi = merge_params.pagination
            df, annotations = await self.fetch_query(left_params.url, left_params.data, left_params.headers)
            df2, annotations2 = await self.fetch_query(right_params.url, right_params.data, right_params.headers)

            date = datetime.datetime.now(tz=datetime.timezone.utc)

            query = FileParams(
                filename = f"datajoin_{date.strftime(r'%Y-%m-%d_%H-%M-%S')}",
                annotations = {"query_left": annotations, "query_right": annotations2}
            )

            step = JoinStep(data=df, keys=[], statuses=[])

            result = Result(
                data=df2, 
                columns={
                    k: DataType.from_polars(v) for k, v in dict(zip(df.columns, df.dtypes)).items()
                },
                cache={"key": "", "status": ""}
            )

            step = step.join_with(result, join_params)

            result = step.get_result(pagi)

            return data_response(
                query,
                result,
                extension
            )

        except Exception as e:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={"Query left": str(merge_params.query_left),
                                 "Query right": str(merge_params.query_right),
                                 "Error": str(e)})

    async def fetch_query(self, url, data, headers):

        self._validate_url(url)

        async with httpx.AsyncClient() as client:
            r = await client.get(url=url, auth=data, headers=headers)
            content_type = r.headers.get("content-type", "")

            if "text/csv" in content_type or content_type.endswith("/csv"):
                return pl.read_csv(r.content, separator=",", has_header=True, infer_schema_length=1000), "Not Available"
            elif "application/json" in content_type:
                json_data = r.json()
                return pl.DataFrame(json_data["data"]), json_data["annotations"]
            else:
                return "Format not Supported"

    def _validate_url(self, url: str) -> None:
        """Validate URL and raise appropriate exceptions"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise InvalidUrlException(url, "Missing scheme or network location")
        except Exception:
            raise InvalidUrlException(url, "Malformed URL")

        # Check domain
        domain = parsed.netloc.split(':')[0]
        valid_domains = [d for d in self.allowed_domains if d and isinstance(d, str)]

        if not any(
            domain.endswith(f".{allowed}") or domain == allowed
            for allowed in valid_domains
        ):
            raise DomainNotAllowedException(domain, valid_domains, source=url)
from datetime import datetime
from typing import Literal, Never, cast, overload

import planetary_computer as pc
import requests
from rasterio.crs import CRS
from shapely.geometry import box, shape

from glidergun._grid import Grid
from glidergun._stack import Stack, stack
from glidergun._types import Extent

url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"


class ItemBase(dict):
    def __init__(self, d: dict, extent: "Extent", crs: CRS):
        super().__init__(d)
        self.extent = extent
        self.crs = crs

    @property
    def id(self) -> str:
        return self["id"]

    @property
    def datetime(self) -> datetime:
        return datetime.fromisoformat(self["properties"]["datetime"])

    def get_url(self, name: str) -> str:
        assets = self["assets"]
        if name not in assets:
            raise ValueError(f"Asset '{name}' not found in item assets: {list(assets.keys())}")
        url = assets[name]["href"]
        return pc.sign(url)

    def download(self, name: str | list[str]) -> Grid | Stack:
        if isinstance(name, list):
            return stack([cast(Grid, self.download(n)) for n in name])
        s = stack(self.get_url(name), self.extent, self.crs)
        if len(s.grids) == 1:
            return s.grids[0]
        return s


class Item[TGrid: str, TStack: str](ItemBase):
    @overload
    def download(self, name: TGrid) -> Grid: ...

    @overload
    def download(self, name: TStack) -> Stack: ...

    @overload
    def download(self, name: list[TGrid]) -> Stack: ...

    def download(self, name):
        return super().download(name)


@overload
def search(
    collection: Literal["landsat-c2-l2"],
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
    *,
    cloud_cover: float | None = None,
) -> list[
    Item[
        Literal[
            "qa",
            "red",
            "blue",
            "drad",
            "emis",
            "emsd",
            "trad",
            "urad",
            "atran",
            "cdist",
            "green",
            "nir08",
            "lwir11",
            "swir16",
            "swir22",
            "coastal",
            "qa_pixel",
            "qa_radsat",
            "qa_aerosol",
        ],
        Never,
    ]
]: ...


@overload
def search(
    collection: Literal["sentinel-2-l2a"],
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
    *,
    cloud_cover: float | None = None,
) -> list[
    Item[
        Literal[
            "AOT",
            "B01",
            "B02",
            "B03",
            "B04",
            "B05",
            "B06",
            "B07",
            "B08",
            "B09",
            "B11",
            "B12",
            "B8A",
            "SCL",
            "WVP",
        ],
        Literal["visual"],
    ]
]: ...


@overload
def search( # type: ignore
    collection: Literal["naip"],
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
) -> list[Item[Never, Literal["image"]]]: ...


@overload
def search(
    collection: Literal["cop-dem-glo-30"],
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
) -> list[Item[Literal["data"], Never]]: ...


@overload
def search(
    collection: str,
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
) -> list[ItemBase]: ...


def search(
    collection: str,
    extent: tuple[float, float, float, float] | list[float],
    query: dict | None = None,
    *,
    cloud_cover: float | None = None,
):
    xmin, ymin, xmax, ymax = extent
    search_extent = Extent(xmin, ymin, xmax, ymax)
    search_polygon = box(xmin, ymin, xmax, ymax)

    response = requests.post(
        url,
        json={
            "bbox": list(extent),
            "collections": [collection],
            "query": {"eo:cloud_cover": {"lt": cloud_cover}} | (query or {}) if cloud_cover else query or {},
        },
    )

    response.raise_for_status()

    features = []

    for feature in response.json()["features"]:
        if search_polygon.within(shape(feature["geometry"])):
            crs = CRS.from_epsg(feature["properties"]["proj:epsg"])
            projected_extent = search_extent.project(from_crs=CRS.from_epsg(4326), to_crs=crs)
            features.append(Item(feature, projected_extent, crs))

    return features

# Standard Libraries
import logging
from dataclasses import dataclass
from typing import Literal

# Dependencies
from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GeographicBoundsError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PointModel(BaseModel):
    """Representation of a ordered pair"""

    x: float
    y: float

    def astuple(self):
        return (self.x, self.y)


@dataclass
class Bounds:
    """Representation of a bounding box"""

    left: float
    bottom: float
    right: float
    top: float


class GeotransformModel(BaseModel):
    """
    Object representing an affine geotransform matrix.

    Parameters
    ----------
    upperleft: PointModel
        Map coordinates of the upper left point of the raster.
    xres: float
        east-west resolution of the raster in map_unit/pixel.
    row_rotation: float
        Amount of rotation for the rows. Usually 0.
    yres: float
        north-south resolution of the raster in map_unit/pixel.
    col_rotation
        Amount of rotation for the columns. Usually 0.
    """

    upperleft: PointModel
    xres: float
    row_rotation: float
    yres: float
    col_rotation: float

    @classmethod
    def fromgdal(
        cls, gdal_transform: tuple[float, float, float, float, float, float]
    ) -> "GeotransformModel":
        """Creates a GeotransformModel from a GDAL-style geotransform."""
        upper_left_pt = PointModel(x=gdal_transform[0], y=gdal_transform[3])
        return cls(
            upperleft=upper_left_pt,
            xres=gdal_transform[1],
            row_rotation=gdal_transform[2],
            yres=gdal_transform[5],
            col_rotation=gdal_transform[4],
        )

    def togdal(self) -> tuple[float, float, float, float, float, float]:
        """Returns a GDAL-style geotransform."""
        return (
            self.upperleft.x,
            self.xres,
            self.row_rotation,
            self.upperleft.y,
            self.yres,
            self.col_rotation,
        )

    def get_bbox(self, height: int, width: int):
        """Given the height and width of a raster, return a bounding box."""
        return Bounds(
            left=self.upperleft.x,
            bottom=self.upperleft.y + height * self.yres,
            right=self.upperleft.x + width * self.xres,
            top=self.upperleft.y,
        )

    def pixel_to_map(
        self,
        xpixel: float,
        ypixel: float,
        convention: Literal["globe", "hemi"] = "hemi",
    ) -> tuple[float, float]:
        """Convert a pixel coordinate point to a map coordinate point."""
        xmap = (
            self.upperleft.x + xpixel * self.xres + ypixel * self.row_rotation
        )
        ymap = (
            self.upperleft.y + ypixel * self.yres + xpixel * self.col_rotation
        )

        if convention == "globe":
            if xmap < 0:
                xmap += 360
        return xmap, ymap

    def map_to_pixel(self, xmap: float, ymap: float) -> tuple[float, float]:
        """Convert a map coordinate point to a pixel coordinate point."""
        _scaler = (self.xres * self.yres) - (
            self.col_rotation * self.row_rotation
        )
        xpixel = (
            (self.yres * xmap)
            - (self.upperleft.x * self.yres)
            - ((self.row_rotation * self.yres) / self.xres) * ymap
            + (self.row_rotation * self.upperleft.y)
        ) / _scaler
        ypixel = (
            (self.xres * ymap)
            - (self.upperleft.y * self.xres)
            - ((self.col_rotation * self.xres) / self.yres) * xmap
            + (self.col_rotation * self.upperleft.x)
        ) / _scaler

        if xpixel < 0:
            raise GeographicBoundsError(
                f"{xmap} is beyond the left X bound: {self.upperleft.x}"
            )
        if ypixel < 0:
            raise GeographicBoundsError(
                f"{ymap} is beyond the top bound: {self.upperleft.y}"
            )
        return xpixel, ypixel


class BaseGeolocationModel(BaseModel):
    """
    Contains all information about the geolocation of a raster or point.
    """

    crs: str
    geotransform: GeotransformModel


class PointGeolocation(BaseGeolocationModel):
    map_point: PointModel
    pixel_point: PointModel

    @classmethod
    def from_base(
        cls,
        geoloc: BaseGeolocationModel,
        location: tuple[float, float],
        location_type: Literal["map", "pixel"],
    ) -> "PointGeolocation":
        if location_type == "map":
            map_pt = location
            pixel_pt = geoloc.geotransform.map_to_pixel(*location)
        elif location_type == "pixel":
            map_pt = geoloc.geotransform.pixel_to_map(*location)
            pixel_pt = location
        return cls(
            crs=geoloc.crs,
            geotransform=geoloc.geotransform,
            map_point=PointModel(x=map_pt[0], y=map_pt[1]),
            pixel_point=PointModel(x=pixel_pt[0], y=pixel_pt[1]),
        )


class RasterGeolocation(BaseGeolocationModel):
    height: int
    width: int
    bounds: Bounds = Field(default=Bounds(left=0, bottom=0, right=0, top=0))

    @model_validator(mode="after")
    def set_bounds(self) -> "RasterGeolocation":
        self.bounds = self.geotransform.get_bbox(self.height, self.width)
        return self

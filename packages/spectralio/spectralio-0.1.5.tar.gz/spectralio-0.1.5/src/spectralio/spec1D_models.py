# Standard Libraries
from enum import StrEnum
from typing import Literal

# Dependencies
from pydantic import BaseModel, Field
import numpy as np
from shapely.geometry import Point

# Relative Imports
from .geospatial_models import (
    BaseGeolocationModel,
    PointGeolocation,
    PointModel,
)
from .wvl_models import WvlModel

type Spec1DFileLiteral = Literal["rawspec"] | Literal["pntspec"] | Literal[
    "geospec"
]


class Spec1DFileTypes(StrEnum):
    RAW = ".rawspec"
    PNT = ".pntspec"
    GEO = ".geospec"


class Spectrum1D(BaseModel):
    """
    Object representing a single spectrum.

    Attributes
    ----------
    name: str
        Name of the spectrum.
    spectrum: list[float]
        Data of the spectrum (e.g. Reflectance, Emissivity, Transmittance)
    wavelength: WvlModel
        Wavelength Object corresponding to the spectrum.

    Notes
    -----
    See wvl_models.py for information on the Wavelength Object.
    """

    name: str
    spectrum: list[float]
    wavelength: WvlModel
    bbl_applied: bool = Field(default=False)

    @classmethod
    def empty(cls) -> "Spectrum1D":
        return cls(
            name="null",
            spectrum=[],
            wavelength=WvlModel.default_bbl([0], "um"),
        )

    def applybbl(self):
        self.spectrum = list(np.asarray(self.spectrum)[self.wavelength.bbl])
        self.bbl_applied = True


class PointSpectrum1D(Spectrum1D):
    """
    Object representing a spectrum pulled from a non-georeferenced spectral
    cube.

    Attributes
    ----------
    name: str
        Name of the spectrum.
    spectrum: list[float]
        Data of the spectrum (e.g. Reflectance, Emissivity, Transmittance)
    wavelength: WvlModel
        Wavelength Object corresponding to the spectrum.
    point: PointModel
        Just a standard X, Y ordered pair object.

    Notes
    -----
    See wvl_models.py for information on the Wavelength Object.
    See geospatial_models.py for information on the PointModel Object.
    """

    pixel: PointModel

    @classmethod
    def from_pixel_coord(
        cls, x: float, y: float, spec1d: Spectrum1D
    ) -> "PointSpectrum1D":
        return cls(
            name=spec1d.name,
            spectrum=spec1d.spectrum,
            wavelength=spec1d.wavelength,
            pixel=PointModel(x=x, y=y),
        )


class GeoSpectrum1D(Spectrum1D):
    """
    Object representing a spectrum pulled from a non-georeferenced spectral
    cube.

    Attributes
    ----------
    name: str
        Name of the spectrum.
    spectrum: list[float]
        Data of the spectrum (e.g. Reflectance, Emissivity, Transmittance)
    wavelength: WvlModel
        Wavelength Object corresponding to the spectrum.
    point: PointGeolocation
        Just a standard X, Y ordered pair object.

    Notes
    -----
    See wvl_models.py for information on the Wavelength Object.
    See geospatial_models.py for information on the PointModel Object.
    """

    point: PointGeolocation

    @classmethod
    def from_pixel_coord(
        cls,
        x: float,
        y: float,
        geoloc: BaseGeolocationModel,
        spec1d: Spectrum1D,
    ):
        return cls(
            name=spec1d.name,
            spectrum=spec1d.spectrum,
            wavelength=spec1d.wavelength,
            point=PointGeolocation.from_base(
                geoloc=geoloc, location=(x, y), location_type="pixel"
            ),
        )

    @classmethod
    def from_map_coord(
        cls,
        x: float,
        y: float,
        geoloc: BaseGeolocationModel,
        spec1d: Spectrum1D,
    ) -> "GeoSpectrum1D":
        return cls(
            name=spec1d.name,
            spectrum=spec1d.spectrum,
            wavelength=spec1d.wavelength,
            point=PointGeolocation.from_base(
                geoloc=geoloc, location=(x, y), location_type="map"
            ),
        )

    @classmethod
    def from_point_spec(
        cls, geoloc: BaseGeolocationModel, spec1d: PointSpectrum1D
    ) -> "GeoSpectrum1D":
        return cls(
            name=spec1d.name,
            spectrum=spec1d.spectrum,
            wavelength=spec1d.wavelength,
            point=PointGeolocation.from_base(
                geoloc=geoloc,
                location=(spec1d.pixel.x, spec1d.pixel.y),
                location_type="map",
            ),
        )

    def location_str(self) -> str:
        """Returns a formatted string of location data."""
        return (
            f"({self.point.pixel_point.y}, {self.point.pixel_point.x})  --> "
            f"({self.point.map_point.y:.2f}, {self.point.map_point.y:.2f})"
        )

    def map_location(self) -> tuple[float, float]:
        """Returns a tuple containing the map point (y, x)"""
        return (self.point.map_point.y, self.point.map_point.x)

    def pixel_location(self) -> tuple[float, float]:
        """Returns a tuple containing the pixel point (x, y)"""
        return (self.point.pixel_point.x, self.point.pixel_point.y)

    def shapely_geometry(self) -> Point:
        return Point(self.point.map_point.astuple())

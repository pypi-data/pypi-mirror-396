"""
# `spectralio`

I/O operations for working with spectral data in python.

---

## Implemented File Types
- .rawspec
- .pntspec
- .geospec
- .specgrp
- .spcub
- .geospcub
- .wvl
"""

from .reading import (
    read_spec1D,
    read_group,
    read_spec3D,
    read_wvl,
    read_geodata,
)
from .writing import (
    write_spec1D,
    write_group,
    write_spec3D,
    write_wvl,
    write_geodata,
    write_from_object,
)
from .shapefiles import make_points, make_polygons

from .wvl_models import WvlModel
from .spec1D_models import Spectrum1D, PointSpectrum1D, GeoSpectrum1D
from .specgroup_models import SpectrumGroup
from .spec3D_models import Spectrum3D, GeoSpectrum3D
from .geospatial_models import (
    BaseGeolocationModel,
    PointGeolocation,
    RasterGeolocation,
)

__all__ = [
    "read_spec1D",
    "read_group",
    "read_spec3D",
    "read_wvl",
    "read_geodata",
    "write_spec1D",
    "write_group",
    "write_spec3D",
    "write_wvl",
    "write_geodata",
    "write_from_object",
    "WvlModel",
    "Spectrum1D",
    "PointSpectrum1D",
    "GeoSpectrum1D",
    "SpectrumGroup",
    "Spectrum3D",
    "GeoSpectrum3D",
    "make_points",
    "make_polygons",
    "BaseGeolocationModel",
    "PointGeolocation",
    "RasterGeolocation",
]

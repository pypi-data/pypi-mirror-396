# Standard Library
from typing import Literal, TypeAlias
from pathlib import Path
import os

WvlUnit: TypeAlias = Literal["nm", "um", "m", "v"]
type PathLike = str | Path | os.PathLike
# SpectrumLike: TypeAlias = (
#     Spectrum1D
#     | PointSpectrum1D
#     | GeoSpectrum1D
#     | Spectrum3D
#     | GeoSpectrum3D
#     | SpectrumGroup
# )

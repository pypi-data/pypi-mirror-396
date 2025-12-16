# Standard Libraries
from enum import StrEnum
from typing import Literal, Optional

# Dependencies
from pydantic import BaseModel, Field, model_validator
import rasterio as rio  # type: ignore
from rasterio.windows import Window  # type: ignore
import numpy as np

# Relative Imports
from .custom_types import PathLike
from .geospatial_models import BaseGeolocationModel
from .wvl_models import WvlModel


type Spec3DFileLiteral = Literal["spcub"] | Literal["geospcub"]


class Spec3DFileTypes(StrEnum):
    RAW = ".spcub"
    GEO = ".geospcub"


class Spectrum3D(BaseModel):
    name: str
    wavelength: WvlModel
    nrows: int
    ncols: int
    nbands: int = Field(default=0)
    raster_fp: PathLike

    @model_validator(mode="after")
    def set_nbands(self) -> "Spectrum3D":
        self.nbands = self.wavelength.nbands
        return self

    def load_raster(
        self,
        pixel_window: Optional[tuple[int, int, int, int]] = None,
        bbl: bool = True,
    ) -> np.ndarray:
        """
        Load raster data from absolute file path stored in the file.

        Parameters
        ----------
        pixel_window: 4-tuple of int, optional
            A window tuple, (col_offset, row_offset, width, height). Default
            is None. Provide this argument to read a partial amount of the
            larger array.

        Returns
        -------
        np.ndarray
            Loaded array.
        """
        if pixel_window is not None:
            w = Window(*pixel_window)  # type: ignore
            with rio.open(self.raster_fp, "r") as f:
                arr = f.read(window=w)
        else:
            with rio.open(self.raster_fp, "r") as f:
                arr = f.read()

        arr = np.transpose(arr, (1, 2, 0))
        if bbl:
            arr = arr[:, :, self.wavelength.bbl]
        return arr


class GeoSpectrum3D(Spectrum3D):
    geodata: BaseGeolocationModel

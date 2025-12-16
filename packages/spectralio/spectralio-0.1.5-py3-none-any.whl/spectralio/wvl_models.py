# Standard Libraries
import logging
from typing import Optional

# Dependencies
from pydantic import BaseModel, Field, model_validator
import numpy as np

# Relative Imports
from .custom_types import WvlUnit

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WvlModel(BaseModel):
    """
    Object representing the wavelength values of a spectrum.

    Attributes
    ----------
    values: list[float]
        Wavelength values.
    unit: WvlUnit
        Unit of the wavelengths. Options are:

        - "nm": nanometers
        - "um": microns
        - "m": meters
        - "v": wavenumber

    bbl: boolean list
        Band Band List. If value in the list is False, this indicates a bad
        band. All True values indicates no bad bands.
    resolution: float
        Average spectral resolution.
    nbands: float
        Number of spectral bands.
    """

    values: list[float]
    unit: WvlUnit
    bbl: list[bool]
    resolution: float = Field(default=0.0)
    nbands: int = Field(default=0)
    ngoodbands: int = Field(default=0)

    @model_validator(mode="after")
    def set_resolution(self):
        arr = np.asarray(self.values)
        self.resolution = float((np.max(arr) - np.min(arr)) / arr.size)
        self.nbands = int(len(self.values))
        self.ngoodbands = int(np.count_nonzero(np.asarray(self.bbl)))
        return self

    @classmethod
    def default_bbl(cls, values: list[float], unit: WvlUnit) -> "WvlModel":
        return cls(values=values, unit=unit, bbl=[True] * len(values))

    @classmethod
    def fromarray(
        cls,
        values: np.ndarray,
        unit: WvlUnit,
        bbl: Optional[list[bool]] = None,
    ) -> "WvlModel":
        if bbl is None:
            bbl = [True] * values.size
        return cls(values=list(values), unit=unit, bbl=bbl)

    def __array__(self):
        return np.asarray(self.values)

    def __getitem__(self, idx):
        return np.asarray(self.values)[idx]

    def __setitem__(self, idx, value):
        arr = np.asarray(self.values)
        arr[idx] = value
        self.values = arr.tolist()

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"ArrayLike({self.values})"

    def asarray(self, bbl: bool = True):
        """
        Returns an array of wavelength values.

        Parameters
        ----------
        bbl: bool, optional
            If true (default), applies bad band mask to eliminate any band
            bands specified in `bbl`.
        """
        if bbl:
            return np.asarray(self.values)[np.asarray(self.bbl)]
        else:
            return np.asarray(self.values)

    def applybbl(self):
        """
        Removes bad bands from wavelength values list.
        """
        return [i for i in self.asarray(bbl=True)]

    def to_nm(self):
        """
        Converts the wavelength values to nanometers.
        """
        arr = np.asarray(self.values)
        if self.unit == "nm":
            pass
        elif self.unit == "um":
            arr *= 10**3
        elif self.unit == "m":
            arr *= 10**9
        elif self.unit == "v":
            arr = 10**9 / arr

        self.values = list(arr)
        self.unit = "nm"
        logger.debug(f"{id(self)} was converted to nm")

    def to_um(self):
        """
        Converts the wavelength values to microns.
        """
        arr = np.asarray(self.values)
        if self.unit == "nm":
            arr *= 10**-3
        elif self.unit == "um":
            pass
        elif self.unit == "m":
            arr *= 10**6
        elif self.unit == "v":
            arr = 10**6 / arr

        self.values = list(arr)
        self.unit = "um"
        logger.debug(f"{id(self)} was converted to um")

    def to_m(self):
        """
        Converts the wavelength values to meters.
        """
        arr = np.asarray(self.values)
        if self.unit == "nm":
            arr *= 10**-9
        elif self.unit == "um":
            arr *= 10**-6
        elif self.unit == "m":
            pass
        elif self.unit == "v":
            arr = 1 / arr

        self.values = list(arr)
        self.unit = "m"
        logger.debug(f"{id(self)} was converted to m")

    def to_v(self):
        """
        Converts the wavelength values to wavenumber.
        """
        arr = np.asarray(self.values)
        if self.unit == "nm":
            arr = 10**9 / arr
        elif self.unit == "um":
            arr = 10**6 / arr
        elif self.unit == "m":
            arr = 1 / arr
        elif self.unit == "v":
            pass

        self.values = list(arr)
        self.unit = "v"
        logger.debug(f"{id(self)} was converted to v")

    def convert_to(self, unit: WvlUnit):
        if unit == "nm":
            self.to_nm()
        elif unit == "um":
            self.to_um()
        elif unit == "m":
            self.to_m()
        elif unit == "v":
            self.to_v()

    def find(
        self, wvl_guess: float | int, unit: WvlUnit
    ) -> tuple[np.int32 | np.int64, float]:
        """
        Finds the wavelength and index closest to a guess value.

        Parameters
        ----------
        wvl_guess: float
            Estimate of the wavelength to find.
        unit: WvlUnit
            Unit of the wavelength guess.

        Returns
        -------
        index: int
            Index of the found wavelength.
        exact_wvl_value: float
            Exact value of the found wavelength.
        """
        _current_unit = self.unit
        self.convert_to(unit)
        arr = self.asarray()
        idx = np.argmin(abs(arr - wvl_guess))
        self.convert_to(_current_unit)
        return idx, self.values[idx]

# Standard Libraries
import logging
from typing import overload, Literal

# Relative Imports
from .wvl_models import WvlModel
from .spec1D_models import (
    Spectrum1D,
    GeoSpectrum1D,
    PointSpectrum1D,
    Spec1DFileLiteral,
)
from .spec3D_models import Spectrum3D, GeoSpectrum3D, Spec3DFileLiteral
from .specgroup_models import SpectrumGroup
from .geospatial_models import BaseGeolocationModel
from ._errors import FileTypeError
from .custom_types import PathLike, Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_geodata(geodata_fp: PathLike) -> BaseGeolocationModel:
    file_suff = Path(geodata_fp).suffix
    if file_suff != ".geodata":
        raise FileTypeError(
            f"The file type should be .geodata not {file_suff}."
        )
    with open(geodata_fp, "r") as f:
        json_str = f.read()
    return BaseGeolocationModel.model_validate_json(json_str)


@overload
def read_spec1D(
    spec1d_fp: PathLike, kind: Literal["rawspec"]
) -> Spectrum1D: ...


@overload
def read_spec1D(
    spec1d_fp: PathLike, kind: Literal["pntspec"]
) -> PointSpectrum1D: ...


@overload
def read_spec1D(
    spec1d_fp: PathLike, kind: Literal["geospec"]
) -> GeoSpectrum1D: ...


def read_spec1D(spec1d_fp: PathLike, kind: Spec1DFileLiteral):
    if kind == "rawspec":
        with open(spec1d_fp, "r") as f:
            json_str = f.read()
        spec_model = Spectrum1D.model_validate_json(json_str)
        return spec_model
    elif kind == "pntspec":
        with open(spec1d_fp, "r") as f:
            json_str = f.read()
        spec_model = PointSpectrum1D.model_validate_json(json_str)
        return spec_model
    elif kind == "geospec":
        with open(spec1d_fp, "r") as f:
            json_str = f.read()
        spec_model = GeoSpectrum1D.model_validate_json(json_str)
        return spec_model


def read_group(specgroup_fp: PathLike):
    file_suff = Path(specgroup_fp).suffix
    if file_suff != ".specgrp":
        raise FileTypeError(f"The file type should be .wvl not {file_suff}.")
    with open(specgroup_fp, "r") as f:
        json_str = f.read()
    group_model = SpectrumGroup.model_validate_json(json_str)
    return group_model


@overload
def read_spec3D(spec3d_fp: PathLike, kind: Literal["spcub"]) -> Spectrum3D: ...


@overload
def read_spec3D(
    spec3d_fp: PathLike, kind: Literal["geospcub"]
) -> GeoSpectrum3D: ...


def read_spec3D(spec3d_fp: PathLike, kind: Spec3DFileLiteral):
    if kind == "spcub":
        with open(spec3d_fp, "r") as f:
            json_str = f.read()
        spec_model = Spectrum3D.model_validate_json(json_str)
        return spec_model
    if kind == "geospcub":
        with open(spec3d_fp, "r") as f:
            json_str = f.read()
        spec_model = GeoSpectrum3D.model_validate_json(json_str)
        return spec_model


def read_wvl(wvl_fp: PathLike) -> WvlModel:
    """
    Read a .wvl file into a WvlModel object.

    Parameters
    ----------
    wvl_fp: File path to .wvl file.

    Returns
    -------
    WvlModel object.
    """
    file_suff = Path(wvl_fp).suffix
    if file_suff != ".wvl":
        raise FileTypeError(f"The file type should be .wvl not {file_suff}.")
    with open(wvl_fp, "r") as f:
        json_str = f.read()
    wvl_model = WvlModel.model_validate_json(json_str)
    return wvl_model

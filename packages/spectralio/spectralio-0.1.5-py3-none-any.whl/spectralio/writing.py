# Standard Libraries
import logging
from typing import Optional, Literal

# Dependencies
import numpy as np
import rasterio as rio  # type: ignore

# Relative Imports
from .custom_types import PathLike, Path, WvlUnit
from .wvl_models import WvlModel
from .spec1D_models import (
    Spectrum1D,
    GeoSpectrum1D,
    PointSpectrum1D,
    Spec1DFileTypes,
)
from .specgroup_models import SpectrumGroup
from .spec3D_models import Spectrum3D, GeoSpectrum3D, Spec3DFileTypes
from .geospatial_models import (
    PointModel,
    PointGeolocation,
    GeotransformModel,
    BaseGeolocationModel,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def resolve_wvlmodel(wvl: WvlModel | PathLike):
    """Returns a WvlModel from an input that is either a WvlModel or a Path."""
    # Creating Wavelength Model
    if isinstance(wvl, WvlModel):
        logger.debug("WvlModel object was provided.")
        wvlmodel = wvl
    else:
        if not Path(wvl).exists():  # Ensuring wvl file existence.
            logger.error("Wavelength file not found: %s", wvl)
            raise FileNotFoundError(f"{wvl} does not exist.")
        logger.debug("Reading wavelength file: %s", wvl)
        with open(wvl, "r") as f:
            json_str = f.read()
        wvlmodel = WvlModel.model_validate_json(json_str)

    return wvlmodel


def write_geodata(
    crs: str,
    geotransform: tuple[float, float, float, float, float, float],
    fp: PathLike,
):
    gtrans = GeotransformModel.fromgdal(geotransform)
    logger.debug("Creating geotransform model for crs=%s", crs)
    geodatamodel = BaseGeolocationModel(crs=crs, geotransform=gtrans)
    json_str = geodatamodel.model_dump_json(indent=2)
    out_path = Path(fp).with_suffix(".geodata")
    with open(out_path, "w") as f:
        f.write(json_str)
    logger.info("Wrote geodata file: %s", out_path)


def write_spec1D(
    spec_vals: np.ndarray | list,
    wvl: PathLike | WvlModel,
    name: str,
    fp: PathLike,
    *,
    location: Optional[tuple[float, float]] = None,
    location_type: Literal["pixel", "map"] = "pixel",
    geodata_fp: PathLike | None = None,
) -> None:
    """
    Writes a spectrum to one of three different file types based on provided
    spatial information.

    Parameters
    ----------
    spec_vals: ArrayLike
        Spectrum data values.
    wvl: PathLike or WvlModel
        Either a wavelength model object or a path to a .wvl file.
    name: str
        Name of the spectrum.
    fp: PathLike
        File path to save the spectrum to. File extension not included.
    location: 2-tuple of float, optional
        Location of the spectrum. Default is None.
    location_type: str, optional
        Specifies map coordinates or pixel coordinates. Either "pixel" or
        "map", respectively, default is "pixel".
    geodata_fp: PathLike, optional
        File path to saved .geodata file.

    Notes
    -----
    Depending on the input arguments, different file types will be returned:

    - If `location` is None, a .rawspec file will be created. This file has no
    spatial information associated with it, but is just a raw spectrum.

    - If `geodata_fp` is None, a .pntspec file will be created. This file
    records the pixel value that the spectrum was pulled from. In this
    scenario, `location_type` must be "pixel".

    - If `geodata_fp` is provided, a .geospec file will be created. This file
    records the pixel value and the map coordinate of the spectrum.
    """
    # Ensuring spec_vals is a list of floats for compatibility.
    if isinstance(spec_vals, np.ndarray):
        spec_vals = list(spec_vals)

    logger.debug(
        "write_spec1D called: name=%s fp=%s location=%s location_type=%s"
        "geodata_fp=%s",
        name,
        fp,
        location,
        location_type,
        geodata_fp,
    )

    wvlmodel = resolve_wvlmodel(wvl)

    # Loading geodata if it is provided
    if geodata_fp is not None:
        if not Path(geodata_fp).exists():  # Ensuring geodata file existence.
            logger.error("Geodata file not found: %s", geodata_fp)
            raise FileNotFoundError(f"{geodata_fp} does not exist.")

        logger.debug("Reading geodata file: %s", geodata_fp)
        # Creating geolocation model
        with open(geodata_fp, "r") as f:
            json_str = f.read()
        geodata = BaseGeolocationModel.model_validate_json(json_str)
    else:
        geodata = None

    if location is None:
        specmodel = Spectrum1D(
            name=name, spectrum=spec_vals, wavelength=wvlmodel
        )
        file_suffix = Spec1DFileTypes.RAW
    else:
        # Handling a georeferenced 1D spectrum.
        if geodata is not None:
            if location_type == "map":
                geopt = PointGeolocation.from_base(
                    geodata, (location[1], location[0]), location_type
                )
            elif location_type == "pixel":
                geopt = PointGeolocation.from_base(
                    geodata, location, location_type
                )

            specmodel = GeoSpectrum1D(
                name=name, spectrum=spec_vals, wavelength=wvlmodel, point=geopt
            )
            file_suffix = Spec1DFileTypes.GEO
        else:
            if location_type == "map":
                raise ValueError(
                    "If the location is in map coordinates, a file path to a "
                    ".geodata file must be provided."
                )
            specmodel = PointSpectrum1D(
                name=name,
                spectrum=spec_vals,
                wavelength=wvlmodel,
                pixel=PointModel(x=location[0], y=location[1]),
            )
            file_suffix = Spec1DFileTypes.PNT

    if Path(fp).is_dir():
        save_path = Path(fp, f"{name}").with_suffix(file_suffix)
    else:
        save_path = Path(fp).with_suffix(file_suffix)

    final_json_str = specmodel.model_dump_json(indent=2)
    with open(save_path, "w") as f:
        f.write(final_json_str)
    logger.info("Wrote spec1D file: %s", save_path)

    return None


def write_group(
    spec_group: np.ndarray | list[list[float]],
    spec_locations: list[tuple[int, int]],
    wvl: PathLike | WvlModel,
    name: str,
    fp: PathLike,
) -> None:

    wvlmodel = resolve_wvlmodel(wvl)

    spectra: list[PointSpectrum1D] = []
    if isinstance(spec_group, np.ndarray):
        # Checking size of spec_group array
        spec_data: list[list[float]] = []
        if spec_group.shape[1] != wvlmodel.nbands:
            raise ValueError(
                "The size of a spec_group array should be NxB where B is "
                f"the number of bands ({wvlmodel.nbands}). It is"
                f"currently {spec_group.shape}."
            )
        for n in range(spec_group.shape[0]):
            spec_data.append(list(spec_group[n, :]))
    else:
        spec_data = spec_group

    for n, spec in enumerate(spec_data):
        spectra.append(
            PointSpectrum1D(
                name=f"{name}_{n:04d}",
                spectrum=spec,
                wavelength=wvlmodel,
                pixel=PointModel(
                    x=spec_locations[n][0], y=spec_locations[n][1]
                ),
            )
        )

    grp_obj = SpectrumGroup(
        name=name,
        spectra=spectra,
        spectra_pts=spec_locations,
        wavelength=wvlmodel,
    )
    json_str = grp_obj.model_dump_json(indent=2)

    if Path(fp).is_dir():
        save_path = Path(fp, name).with_suffix(".specgrp")
    else:
        save_path = Path(fp).with_suffix(".specgrp")
    with open(save_path, "w") as f:
        f.write(json_str)
        logger.debug(f"Wrote SpectrumGroup to {save_path}.")

    return None


def write_spec3D(
    name: str,
    wvl: PathLike | WvlModel,
    raster_fp: PathLike,
    fp: PathLike,
    *,
    geodata_fp: Optional[PathLike] = None,
) -> None:
    wvlmodel = resolve_wvlmodel(wvl)
    with rio.open(raster_fp, "r") as f:
        height: int = f.height
        width: int = f.width
        count: int = f.count
    if count != wvlmodel.nbands:
        raise ValueError(
            f"Loaded raster data ({count}) does not have the same number of "
            f"bands as the wavelength data ({wvlmodel.nbands})."
        )
    if geodata_fp is None:
        spec3dmodel = Spectrum3D(
            name=name,
            wavelength=wvlmodel,
            nrows=height,
            ncols=width,
            raster_fp=raster_fp,
        )
        file_suffix = Spec3DFileTypes.RAW
    else:
        with open(geodata_fp, "r") as f:
            geojson_str = f.read()
        geodat = BaseGeolocationModel.model_validate_json(geojson_str)
        spec3dmodel = GeoSpectrum3D(
            name=name,
            wavelength=wvlmodel,
            nrows=height,
            ncols=width,
            raster_fp=raster_fp,
            geodata=geodat,
        )
        file_suffix = Spec3DFileTypes.GEO

    if Path(fp).is_dir():
        save_path = Path(fp, name).with_suffix(file_suffix)
    else:
        save_path = Path(fp).with_suffix(file_suffix)

    json_str = spec3dmodel.model_dump_json(indent=2)
    with open(save_path, "w") as f:
        f.write(json_str)


def write_wvl(
    wvl_values: np.ndarray | list,
    wvl_unit: WvlUnit,
    fp: PathLike,
    bbl: Optional[np.ndarray | list] = None,
) -> None:
    # Ensuring wvl_values is a list
    if isinstance(wvl_values, np.ndarray):
        wvl_values = list(wvl_values)

    # Creating WvlModel
    if bbl is None:
        bbl_vals = list(np.ones(len(wvl_values), dtype=bool))
    else:
        if isinstance(bbl, np.ndarray):
            bbl_vals = list(bbl)
        else:
            bbl_vals = bbl

    wvl = WvlModel(values=wvl_values, unit=wvl_unit, bbl=bbl_vals)

    # Dumping data to JSON
    json_string = wvl.model_dump_json(indent=2)
    out_path = Path(fp).with_suffix(".wvl")
    with open(out_path, "w") as f:
        f.write(json_string)
    logger.info("Wrote wavelength file: %s", out_path)


def write_from_object(spectrum_like_obj, save_fp: PathLike) -> None:
    json_str = spectrum_like_obj.model_dump_json(indent=2)
    suffix: str = ""
    if (
        isinstance(spectrum_like_obj, Spectrum1D)
        and not isinstance(spectrum_like_obj, PointSpectrum1D)
        and not isinstance(spectrum_like_obj, GeoSpectrum1D)
    ):
        suffix = Spec1DFileTypes.RAW
    elif isinstance(spectrum_like_obj, PointSpectrum1D):
        suffix = Spec1DFileTypes.PNT
    elif isinstance(spectrum_like_obj, GeoSpectrum1D):
        suffix = Spec1DFileTypes.GEO
    elif isinstance(spectrum_like_obj, Spectrum3D):
        suffix = Spec3DFileTypes.RAW
    elif isinstance(spectrum_like_obj, GeoSpectrum3D):
        suffix = Spec3DFileTypes.GEO
    elif isinstance(spectrum_like_obj, SpectrumGroup):
        suffix = ".specgrp"
    else:
        raise ValueError("Invalid Spectrum Like Object")

    with open(Path(save_fp).with_suffix(suffix), "w") as f:
        f.write(json_str)

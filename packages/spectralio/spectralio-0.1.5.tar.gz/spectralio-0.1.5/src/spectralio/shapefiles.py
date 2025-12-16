# Dependencies
from shapely.geometry import mapping
import fiona  # type: ignore

# Relative Imports
from .custom_types import Path, PathLike
from .spec1D_models import GeoSpectrum1D
from .specgroup_models import SpectrumGroup
from .reading import read_geodata


def make_points(
    spectra: list[GeoSpectrum1D] | SpectrumGroup,
    output_path: PathLike,
    group_geodata_fp: PathLike | None = None,
):
    schema = {
        "geometry": "Point",
        "properties": {"name": "str", "id": "int"},
    }
    fiona_config = {"crs": None, "driver": "ESRI Shapefile", "schema": schema}
    if isinstance(spectra, SpectrumGroup):
        if group_geodata_fp is None:
            raise ValueError(
                "If a Spectrum Group is used to make points, a geodata path"
                " must be provided."
            )
        spectra_list: list[GeoSpectrum1D] = []
        geodata = read_geodata(geodata_fp=group_geodata_fp)
        for pnt_spec in spectra.spectra:
            geospec = GeoSpectrum1D.from_point_spec(geodata, pnt_spec)
            spectra_list.append(geospec)
    elif isinstance(spectra, list):
        spectra_list = spectra

    if Path(output_path).is_dir():
        for spec in spectra_list:
            fiona_config["crs"] = spec.point.crs
            save_file = Path(output_path, spec.name).with_suffix(".shp")
            with fiona.open(save_file, "w", **fiona_config) as c:
                c.write(
                    {
                        "geometry": mapping(spec.shapely_geometry()),
                        "properties": {"name": spec.name, "id": 1},
                    }
                )
    elif Path(output_path):
        save_file = Path(output_path).with_suffix(".shp")
        fiona_config["crs"] = spectra_list[0].point.crs
        with fiona.open(save_file, "w", **fiona_config) as c:
            for n, spec in enumerate(spectra_list):
                c.write(
                    {
                        "geometry": mapping(spec.shapely_geometry()),
                        "properties": {"name": spec.name, "id": n},
                    }
                )


def make_polygons(
    spectra: list[SpectrumGroup], geodata_fp: PathLike, output_path: PathLike
):
    geodata = read_geodata(geodata_fp)
    schema = {
        "geometry": "Polygon",
        "properties": {"name": "str", "id": "int", "nspectra": "int"},
    }
    fiona_config = {
        "crs": geodata.crs,
        "driver": "ESRI Shapefile",
        "schema": schema,
    }
    if Path(output_path).is_dir():
        for spec in spectra:
            save_file = Path(output_path, spec.name).with_suffix(".shp")
            with fiona.open(save_file, "w", **fiona_config) as c:
                c.write(
                    {
                        "geometry": mapping(spec.shapely_geometry(geodata)),
                        "properties": {
                            "name": spec.name,
                            "id": 1,
                            "nspectra": spec.nspectra,
                        },
                    }
                )
    elif Path(output_path):
        save_file = Path(output_path).with_suffix(".shp")
        with fiona.open(save_file, "w", **fiona_config) as c:
            for n, spec in enumerate(spectra):
                c.write(
                    {
                        "geometry": mapping(spec.shapely_geometry(geodata)),
                        "properties": {
                            "name": spec.name,
                            "id": n,
                            "nspectra": spec.nspectra,
                        },
                    }
                )

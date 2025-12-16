# Dependencies
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, model_validator
import numpy as np
from shapely.geometry import Polygon
from alphashape import alphashape  # type: ignore

# Relative Imports
from .custom_types import PathLike, Path
from .spec1D_models import PointSpectrum1D, Spec1DFileTypes
from .geospatial_models import BaseGeolocationModel
from .wvl_models import WvlModel

# from .geospatial_models import Bounds


@dataclass
class GroupStats:
    mean: np.ndarray
    median: np.ndarray
    stdev: np.ndarray
    error_bounds: tuple[np.ndarray, np.ndarray] = field(init=False)

    def __post_init__(self):
        self.error_bounds = (self.mean - self.stdev, self.mean + self.stdev)


class SpectrumGroup(BaseModel):
    name: str
    spectra: list[PointSpectrum1D]
    spectra_pts: list[tuple[int, int]]
    wavelength: WvlModel
    polygon_vertices: list[tuple[float, float]] = Field(default=[])
    nspectra: int = Field(default=0)
    bbl_applied: bool = Field(default=False)

    @model_validator(mode="after")
    def set_nspectra(self) -> "SpectrumGroup":
        if self.name == "null":
            return self
        self.nspectra = len(self.spectra)
        poly: Polygon = alphashape(self.spectra_pts, alpha=0.9)  # type: ignore
        self.polygon_vertices = [
            (i, j) for i, j in zip(poly.exterior.xy[0], poly.exterior.xy[1])
        ]
        return self

    @classmethod
    def empty(cls) -> "SpectrumGroup":
        return cls(
            name="null",
            spectra=[],
            spectra_pts=[],
            wavelength=WvlModel.default_bbl([0], "um"),
        )

    def applybbl(self):
        for i in self.spectra:
            i.applybbl()
        self.bbl_applied = True

    def asarray(self) -> np.ndarray:
        if self.bbl_applied:
            _nbands = self.spectra[0].wavelength.ngoodbands
        else:
            _nbands = self.spectra[0].wavelength.nbands
        group_array = np.empty((self.nspectra, _nbands), dtype=np.float32)
        for n, i in enumerate(self.spectra):
            group_array[n, :] = i.spectrum
        return group_array

    def export_to_directory(self, out_dir: PathLike) -> None:
        for i in self.spectra:
            json_str = i.model_dump_json(indent=2)
            with open(
                Path(out_dir, i.name).with_suffix(Spec1DFileTypes.PNT)
            ) as f:
                f.write(json_str)

    def create_mask(self, height: int, width: int) -> np.ndarray:
        mask_arr = np.zeros((height, width), dtype=np.bool)
        x_pts: list[int] = []
        y_pts: list[int] = []
        for spec in self.spectra:
            x_pts.append(int(spec.pixel.x))
            y_pts.append(int(spec.pixel.y))
        x_pts_arr = np.asarray(x_pts)
        y_pts_arr = np.asarray(y_pts)

        mask_arr[x_pts_arr, y_pts_arr] = True

        return mask_arr

    def get_stats(self) -> GroupStats:
        arr = self.asarray()

        return GroupStats(
            mean=np.mean(arr, axis=0),
            median=np.median(arr, axis=0),
            stdev=np.std(arr, axis=0, ddof=1),
        )

    def get_vertices_arr(self) -> np.ndarray:
        vert_arr = np.empty((len(self.polygon_vertices), 2))

        for n, i in enumerate(self.polygon_vertices):
            vert_arr[n, :] = i

        return vert_arr

    def shapely_geometry(self, geodata: BaseGeolocationModel) -> Polygon:
        new_verts: list[tuple[float, float]] = []
        for vert in self.polygon_vertices:
            new_verts.append(geodata.geotransform.pixel_to_map(*vert))
        return Polygon(new_verts)

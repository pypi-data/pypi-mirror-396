import os

import msgpack
import numpy as np
from skimage.measure import marching_cubes

from cvsx2mvsx.etl.load.encoders.lattice import lattice_to_bcif
from cvsx2mvsx.etl.transform.common import (
    fetch_contour_level,
    get_hex_color,
    get_opacity,
    get_segment_description,
    get_segment_label,
    get_segment_tooltip,
    get_segmentation_annotations,
    get_segmentation_descriptions,
)
from cvsx2mvsx.models.cvsx.entry import CVSXEntry
from cvsx2mvsx.models.cvsx.lattice import LatticeCif
from cvsx2mvsx.models.internal.segment import InternalMeshSegment, InternalVolumeSegment
from cvsx2mvsx.models.internal.segmentation import (
    InternalMeshSegmentation,
    InternalVolumeSegmentation,
)


def find_objects(
    array: np.ndarray, max_label: int = 0
) -> list[tuple[slice, ...] | None]:
    if max_label == 0:
        max_label = array.max()

    objects = [None] * max_label

    coords = np.nonzero(array)

    if len(coords[0]) == 0:
        return objects

    values = array[coords]

    sort_idx = np.argsort(values)
    sorted_values = values[sort_idx]

    unique_labels, split_indices = np.unique(sorted_values, return_index=True)

    ndim = array.ndim

    for i, label in enumerate(unique_labels):
        if label == 0:
            continue

        if label > max_label:
            continue

        start_idx = split_indices[i]
        end_idx = (
            split_indices[i + 1] if i + 1 < len(split_indices) else len(sorted_values)
        )

        group_indices = sort_idx[start_idx:end_idx]

        slices = []
        for dim in range(ndim):
            dim_coords = coords[dim][group_indices]
            slices.append(slice(dim_coords.min(), dim_coords.max() + 1))

        objects[label - 1] = tuple(slices)

    return objects


def smooth_3d_volume_integer(volume: np.ndarray, iterations: int = 1) -> np.ndarray:
    if iterations <= 0:
        return volume

    current = volume.astype(np.uint16)
    scratch = np.zeros_like(current)

    for _ in range(iterations):
        padded = np.pad(current, pad_width=1, mode="edge")
        np.multiply(padded[1:-1, 1:-1, 1:-1], 2, out=scratch)
        scratch += padded[2:, 1:-1, 1:-1]
        scratch += padded[:-2, 1:-1, 1:-1]
        scratch += padded[1:-1, 2:, 1:-1]
        scratch += padded[1:-1, :-2, 1:-1]
        scratch += padded[1:-1, 1:-1, 2:]
        scratch += padded[1:-1, 1:-1, :-2]
        scratch += 4
        scratch //= 8
        current[:] = scratch

    return current.astype(np.uint8)


def smooth_3d_volume_float(volume: np.ndarray, iterations: int = 1) -> np.ndarray:
    vol = volume.astype(np.float32)
    for _ in range(iterations):
        padded = np.pad(vol, pad_width=1, mode="edge")

        center = padded[1:-1, 1:-1, 1:-1]
        xp = padded[2:, 1:-1, 1:-1]
        xn = padded[:-2, 1:-1, 1:-1]
        yp = padded[1:-1, 2:, 1:-1]
        yn = padded[1:-1, :-2, 1:-1]
        zp = padded[1:-1, 1:-1, 2:]
        zn = padded[1:-1, 1:-1, :-2]

        vol = (2 * center + xp + xn + yp + yn + zp + zn) / 8.0

    return vol


class LatticeTransformer:
    def __init__(
        self,
        cvsx_entry: CVSXEntry,
        out_dir_path: str,
        lattice_to_mesh: bool,
    ) -> None:
        self._cvsx_entry = cvsx_entry
        self._out_dir_path = out_dir_path
        self._lattice_to_mesh = lattice_to_mesh

    def run(self) -> list[InternalMeshSegmentation]:
        if not self._cvsx_entry.index.latticeSegmentations:
            return []

        mvsx_segmentations: list[InternalMeshSegmentation] = []
        segmentation_annotations = get_segmentation_annotations(self._cvsx_entry)

        for proxy in self._cvsx_entry.files_proxy.lattice_segmentations:
            segmentation_id = proxy.metadata.segmentationId
            timeframe_id = proxy.metadata.timeframeIndex
            lattice_cif: LatticeCif = proxy.load()

            full_volume_data = self._reshape_cif_to_xyz(
                lattice_cif.segmentation_block.segmentation_data_3d.values,
                lattice_cif.segmentation_block.volume_data_3d_info,
            )

            max_id = int(np.max(full_volume_data))
            slices = find_objects(full_volume_data, max_label=max_id)

            segment_ids = set(
                lattice_cif.segmentation_block.segmentation_data_table.segment_id
            )

            mvsx_segments: list[InternalMeshSegment] = []

            for segment_id in segment_ids:
                if segment_id == 0:
                    continue

                obj_slice = (
                    slices[segment_id - 1] if (segment_id - 1) < len(slices) else None
                )

                if obj_slice is None:
                    continue

                annotation = segmentation_annotations.get((segmentation_id, segment_id))
                self._validate_annotation(
                    annotation, timeframe_id, segment_id, segmentation_id
                )

                color = get_hex_color(annotation)
                opacity = get_opacity(annotation)

                if color is None:
                    color = "white"
                if opacity is None:
                    opacity = 1

                if self._lattice_to_mesh:
                    mvsx_segment = self._create_mesh(
                        full_volume_data=full_volume_data,
                        obj_slice=obj_slice,
                        lattice_cif=lattice_cif,
                        timeframe_id=timeframe_id,
                        segmentation_id=segmentation_id,
                        segment_id=segment_id,
                        color=color,
                        opacity=opacity,
                    )
                else:
                    mvsx_segment = self._create_volume(
                        lattice_cif=lattice_cif,
                        full_volume_data=full_volume_data,
                        timeframe_id=timeframe_id,
                        segmentation_id=segmentation_id,
                        segment_id=segment_id,
                        color=color,
                        opacity=opacity,
                    )
                mvsx_segments.append(mvsx_segment)

            del full_volume_data
            del lattice_cif
            del slices

            if self._lattice_to_mesh:
                mvsx_segmentation = InternalMeshSegmentation(
                    timeframe_id=timeframe_id,
                    segmentation_id=segmentation_id,
                    segments=mvsx_segments,
                )
            else:
                mvsx_segmentation = InternalVolumeSegmentation(
                    timeframe_id=timeframe_id,
                    segmentation_id=segmentation_id,
                    segments=mvsx_segments,
                )
            mvsx_segmentations.append(mvsx_segmentation)

        return mvsx_segmentations

    def _create_mesh(
        self,
        full_volume_data,
        segment_id,
        obj_slice,
        lattice_cif,
        timeframe_id,
        segmentation_id,
        color,
        opacity,
    ):
        voxel, origin, _ = self.get_spatial_parameters(lattice_cif)
        vertices, indices, triangle_groups = self.get_mesh_data_cropped(
            full_volume_data,
            segment_id,
            obj_slice,
            voxel_size=voxel,
            origin=origin,
        )

        source_filepath = (
            f"segmentations/lattice/{timeframe_id}_{segmentation_id}_{segment_id}.json"
        )
        fullpath = os.path.join(self._out_dir_path, source_filepath)
        dirname = os.path.dirname(fullpath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(fullpath, "wb") as f:
            msgpack.pack(
                {
                    "vertices": vertices.ravel().tolist(),
                    "indices": indices.ravel().tolist(),
                    "triangle_groups": triangle_groups.ravel().tolist(),
                },
                f,
            )

        cvsx_desciptions = get_segmentation_descriptions(
            self._cvsx_entry,
            "lattice",
            segmentation_id,
            segment_id,
        )
        if len(cvsx_desciptions) == 0:
            label = None
            tooltip = None
            description = None
        else:
            label = get_segment_label(cvsx_desciptions)
            tooltip = get_segment_tooltip(
                cvsx_desciptions,
                segmentation_id,
                segment_id,
            )
            description = get_segment_description(
                cvsx_desciptions,
                segmentation_id,
                segment_id,
            )

        return InternalMeshSegment(
            source_filepath=source_filepath,
            timeframe_id=timeframe_id,
            segmentation_id=segmentation_id,
            segment_id=segment_id,
            color=color,
            opacity=opacity,
            instance=np.eye(4).ravel().tolist(),
            label=label,
            tooltip=tooltip,
            description=description,
        )

    def _create_volume(
        self,
        segment_id,
        lattice_cif: LatticeCif,
        full_volume_data: np.ndarray,
        timeframe_id,
        segmentation_id,
        color,
        opacity,
    ):
        lattice_cif = self.get_lattice_segment(
            lattice_cif, full_volume_data, segment_id
        )
        data = lattice_to_bcif(lattice_cif)

        source_filepath = (
            f"segmentations/lattice/{timeframe_id}_{segmentation_id}_{segment_id}.bcif"
        )
        fullpath = os.path.join(self._out_dir_path, source_filepath)
        dirname = os.path.dirname(fullpath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(fullpath, "wb") as f:
            f.write(data)

        cvsx_desciptions = get_segmentation_descriptions(
            self._cvsx_entry,
            "lattice",
            segmentation_id,
            segment_id,
        )
        if len(cvsx_desciptions) == 0:
            label = None
            tooltip = None
            description = None
        else:
            label = get_segment_label(cvsx_desciptions)
            tooltip = get_segment_tooltip(
                cvsx_desciptions,
                segmentation_id,
                segment_id,
            )
            description = get_segment_description(
                cvsx_desciptions,
                segmentation_id,
                segment_id,
            )

        absolute_isovalue = fetch_contour_level(self._cvsx_entry)

        return InternalVolumeSegment(
            source_filepath=source_filepath,
            timeframe_id=timeframe_id,
            segmentation_id=segmentation_id,
            segment_id=segment_id,
            color=color,
            opacity=opacity,
            channel_id=str(segment_id),
            absolute_isovalue=absolute_isovalue,
            relative_isovalue=1,
            show_faces=True,
            show_wireframe=False,
            label=label,
            tooltip=tooltip,
            description=description,
        )

    def _reshape_cif_to_xyz(self, values, info):
        nx, ny, nz = info.sample_count_0, info.sample_count_1, info.sample_count_2

        arr = np.asarray(values).reshape((nz, ny, nx))
        return arr.transpose((2, 1, 0))

    def get_mesh_data_cropped(
        self,
        full_data: np.ndarray,
        segment_id: int,
        obj_slice: tuple[slice, slice, slice],
        voxel_size: np.ndarray,
        origin: np.ndarray,
        smooth_iterations: int = 1,
    ):
        cropped_view = full_data[obj_slice]

        mask = (cropped_view == segment_id).astype(np.uint8) * 255

        if smooth_iterations and smooth_iterations > 0:
            mask = smooth_3d_volume_integer(mask, iterations=smooth_iterations)

        padded_mask = np.pad(mask, 1, mode="constant")

        try:
            verts, faces, *_ = marching_cubes(padded_mask, level=128)
        except (RuntimeError, ValueError):
            return np.array([]), np.array([]), np.array([])

        verts -= 1

        offset_x = obj_slice[0].start
        offset_y = obj_slice[1].start
        offset_z = obj_slice[2].start

        verts[:, 0] += offset_x
        verts[:, 1] += offset_y
        verts[:, 2] += offset_z

        verts[:, 0] *= voxel_size[0]
        verts[:, 1] *= voxel_size[1]
        verts[:, 2] *= voxel_size[2]

        verts[:, 0] += origin[0]
        verts[:, 1] += origin[1]
        verts[:, 2] += origin[2]

        verts_rounded = np.round(verts.astype(np.float64), 2)
        faces = faces[:, ::-1]
        triangle_groups = np.zeros(len(faces), dtype=np.int32)

        return verts_rounded, faces, triangle_groups

    def get_lattice_segment(
        self,
        lattice_cif: LatticeCif,
        full_volume_data: np.ndarray,
        segment_id: int,
        smooth_iterations: int = 1,
    ) -> LatticeCif | None:
        segment_cif = lattice_cif.model_copy(deep=True)
        info = segment_cif.segmentation_block.volume_data_3d_info

        data = full_volume_data

        data_3d_values = np.where(data == segment_id, 1.0, 0.0)

        padded = np.pad(
            data_3d_values,
            ((1, 1), (1, 1), (1, 1)),
            mode="constant",
            constant_values=0.0,
        )

        if smooth_iterations and smooth_iterations > 0:
            padded = smooth_3d_volume_float(padded, iterations=smooth_iterations)

        orig_dims = np.array(
            [
                float(info.dimensions_0),
                float(info.dimensions_1),
                float(info.dimensions_2),
            ]
        )
        orig_counts = np.array(
            [info.sample_count_0, info.sample_count_1, info.sample_count_2],
            dtype=np.float32,
        )

        voxel_size = orig_dims / orig_counts

        info.sample_count_0 = int(info.sample_count_0 + 2)
        info.sample_count_1 = int(info.sample_count_1 + 2)
        info.sample_count_2 = int(info.sample_count_2 + 2)

        info.origin_0 = float(info.origin_0) - float(voxel_size[0])
        info.origin_1 = float(info.origin_1) - float(voxel_size[1])
        info.origin_2 = float(info.origin_2) - float(voxel_size[2])

        info.dimensions_0 = float(orig_dims[0] + 2.0 * voxel_size[0])
        info.dimensions_1 = float(orig_dims[1] + 2.0 * voxel_size[1])
        info.dimensions_2 = float(orig_dims[2] + 2.0 * voxel_size[2])

        info.min_sampled = float(padded.min())
        info.max_sampled = float(padded.max())
        info.mean_sampled = float(padded.mean())
        info.sigma_sampled = float(padded.std())

        padded_for_cif = np.transpose(padded, (2, 1, 0)).ravel()
        segment_cif.segmentation_block.segmentation_data_3d.values = padded_for_cif

        return segment_cif

    def get_spatial_parameters(
        self,
        lattice_cif: LatticeCif,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Extracts voxel size and origin instead of creating a 4x4 matrix.
        """
        downsampling_level = (
            lattice_cif.segmentation_block.volume_data_3d_info.sample_rate
        )
        sampling_info = (
            self._cvsx_entry.metadata.volumes.volume_sampling_info.boxes.get(
                downsampling_level
            )
        )
        if sampling_info is None:
            raise ValueError(f"Downsampling level {downsampling_level} not found.")

        vx, vy, vz = sampling_info.voxel_size
        ox, oy, oz = sampling_info.origin
        dx, dy, dz = sampling_info.grid_dimensions

        voxel_size = np.array([vx, vy, vz], dtype=np.float64)
        origin = np.array([ox, oy, oz], dtype=np.float64)
        dimension = np.array([dx, dy, dz], dtype=np.float64)

        return voxel_size, origin, dimension

    def _validate_annotation(
        self, annotation, timeframe_id, segment_id, segmentation_id
    ):
        if not annotation:
            return

        assert annotation.segment_kind == "lattice"
        assert annotation.segment_id == segment_id
        assert annotation.segmentation_id == segmentation_id

        t = annotation.time
        if isinstance(t, int):
            assert t == timeframe_id
        elif isinstance(t, list):
            if all(isinstance(x, int) for x in t):
                assert timeframe_id in t
            elif all(
                isinstance(x, tuple)
                and len(x) == 2
                and all(isinstance(i, int) for i in x)
                for x in t
            ):
                assert any(start <= timeframe_id <= end for start, end in t)
            else:
                raise TypeError("annotation.time list contains unsupported types")
        else:
            raise TypeError("annotation.time must be int or list")

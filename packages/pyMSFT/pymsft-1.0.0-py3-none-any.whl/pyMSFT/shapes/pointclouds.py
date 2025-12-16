from .shapes import ShapeTemplate3D, ShapeTemplate2D
from .. import xp, np, GPU_USED
from typing import Union

__all__ = ["PointCloud"]


class PointCloud(ShapeTemplate3D):
    name = 'PointCloud'

    def __init__(self, *, xcoords: np.ndarray, ycoords: np.ndarray, zcoords: np.ndarray, types: np.ndarray = None,
                 complex_atomic_ff: Union[np.ndarray, complex], wavelength: float,
                 box_min: float = None, box_max: float = None,
                 rescaled_box_size: float = None, rescaling_factor: float = None, **kwargs):
        """
        Create a voxelized 3D point cloud from atomic coordinates.
        Based on CXRO X-Ray database https://henke.lbl.gov/optical_constants/ or https://doi.org/10.1006/adnd.1993.1013.
        Parameters
        ----------
        xcoords: np.ndarray
            x coordinates of the points in nm.
        ycoords: np.ndarray
            y coordinates of the points in nm.
        zcoords: np.ndarray
            z coordinates of the points in nm.
        types: np.ndarray, optional
            Integer array of the same length as xcoords, ycoords, zcoords, indicating the atom type of each point.
            0 corresponds to the first type, 1 to the second type, and so on. If None, all points are assumed to be of the same type.
        complex_atomic_ff: np.ndarray or complex
            If types is provided, this should be an array of complex atomic form factors corresponding to each type.
            If types is not provided, this should be a single complex number representing the form factor for all points.
        box_min: float, optional
            Minimum coordinate value for the bounding box in nm. If None, it will be set to the minimum of the coordinates.
        box_max: float, optional
            Maximum coordinate value for the bounding box in nm. If None, it will be set to the maximum of the coordinates.
        wavelength: float
            Wavelength of the incident radiation in nm.
        rescaled_box_size: float, optional
            If provided, the bounding box will be rescaled to this size in nm.
        rescaling_factor: float, optional
            If provided, the bounding box will be rescaled by this factor.
        kwargs: dict
            Additional keyword arguments for the ShapeTemplate3D base class.
        """

        if types is None:
            single_type = True
            if ~np.iscomplex(complex_atomic_ff):
                raise Exception('For unspecified type, complex_atomic_ff must be a complex.')
        else:
            single_type = False
            if types.min() != 0:
                raise Exception('Type counting must start with 0.')

        if box_min is None:
            box_min = np.min([xp.min(xcoords), xp.min(ycoords), xp.min(zcoords)])
            perform_min_outofbounds = False
        else:
            perform_min_outofbounds = True
        if box_max is None:
            box_max = np.max([xp.max(xcoords), xp.max(ycoords), xp.max(zcoords)])
            perform_max_outofbounds = False
        else:
            perform_max_outofbounds = True

        if rescaling_factor is not None and rescaled_box_size is not None:
            raise Exception('Only one of effective_box_scaling and effective_box_size can be specified.')
        if rescaling_factor is not None:
            rescaled_box_size = rescaling_factor * (box_max - box_min)

        if rescaled_box_size is not None:
            kwargs['box_size'] = rescaled_box_size
        else:
            kwargs['box_size'] = box_max - box_min

        super().__init__(**kwargs)
        internal_box_size = box_max - box_min
        box_delta = internal_box_size / (self.resolution - 1)
        xcoords, ycoords, zcoords = self.apply_rotation(x_axis=xcoords, y_axis=ycoords, z_axis=zcoords)

        if perform_max_outofbounds:
            outofbounds = np.invert((xcoords >= box_max) + (ycoords >= box_max) + (zcoords >= box_max))
            xcoords = xcoords[outofbounds]
            ycoords = ycoords[outofbounds]
            zcoords = zcoords[outofbounds]
            if not single_type:
                types = types[outofbounds]

        if perform_min_outofbounds:
            outofbounds = np.invert((xcoords <= box_min) + (ycoords <= box_min) + (zcoords <= box_min))
            xcoords = xcoords[outofbounds]
            ycoords = ycoords[outofbounds]
            zcoords = zcoords[outofbounds]
            if not single_type:
                types = types[outofbounds]

        rel = 2.8179403227E-15 * 1E9  # classical electron radius in nm
        xindices = ((xcoords - box_min) / box_delta).astype(int)
        yindices = ((ycoords - box_min) / box_delta).astype(int)
        zindices = ((zcoords - box_min) / box_delta).astype(int)

        self._density = np.zeros((self.resolution, self.resolution, self.resolution), dtype=complex)
        # Note the use of conjugate! This is due to the inconsistent definition of the refractive index according to CXRO
        # (n = 1 - delta + i * beta) for the form factors themselves and (n = 1 - delta - i * beta) in the paper.
        if single_type:
            particle_contribution = 1 / (2 * xp.pi) * rel * 1 / (box_delta ** 3) * wavelength ** 2 * np.conjugate(complex_atomic_ff)
            np.add.at(self._density, (xindices, yindices, zindices), particle_contribution)
            if GPU_USED:
                self._density = xp.array(self._density)
        else:
            particle_contribution = 1 / (2 * xp.pi) * rel * 1 / (box_delta ** 3) * wavelength ** 2 * np.conjugate(complex_atomic_ff[types])
            np.add.at(self._density, (xindices, yindices, zindices), particle_contribution)
            if GPU_USED:
                self._density = xp.array(self._density)

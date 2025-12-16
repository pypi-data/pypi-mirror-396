import numpy as np
from typing import Union
from .. import xp, GPU_USED


class ShapeTemplate:
    name = 'TEMPLATE'

    def __str__(self):
        return self.name

    def __init__(self, *, refractive_index: complex = None, delta: float = None, beta: float = None,
                 box_size: float = None, npix: int = 64,
                 x_rotation: float = 0., y_rotation: float = 0., z_rotation: float = 0.):
        """
        Contains a 3d array, density, that corresponds to the complex relative refractive index: n-1 = -delta + i beta.

        Parameters
        ----------
        refractive_index : complex
        delta : float
        beta : float
        box_size : float
        npix : int
        x_rotation : float
        y_rotation : float
        z_rotation : float
        """
        default_refractive_index = 1 + 1e-9 + 1j * 0
        self.environment_refractive_index = 1 + 1j * 0
        if [x is not None for x in (refractive_index, delta, beta)].count(True) > 0:
            if refractive_index is not None:
                pass
            elif [x is not None for x in (delta, beta)].count(True) == 2:
                refractive_index = 1 - delta + 1j * beta
            else:
                raise AttributeError('Define either a refractive_index=..., or both a delta=... and beta=...!')
        else:
            refractive_index = default_refractive_index

        self.ref_index_array = xp.array([self.environment_refractive_index - 1, refractive_index - 1])

        self.box_size = box_size

        self.x_rotation = x_rotation
        self.y_rotation = y_rotation
        self.z_rotation = z_rotation
        self.orthogonal_rotations = all(rotation % np.pi == 0 for rotation in [self.x_rotation, self.y_rotation, self.z_rotation])

        self.resolution = npix
        self.radius_axis = xp.linspace(-1, 1, self.resolution)

        self.x_axis_slice, self.y_axis_slice = xp.meshgrid(self.radius_axis, self.radius_axis, indexing='ij')

        if ~self.orthogonal_rotations:
            self.rotmat_x = xp.array([[1., 0., 0.],
                                      [0., np.cos(self.x_rotation), -np.sin(self.x_rotation)],
                                      [0., np.sin(self.x_rotation), np.cos(self.x_rotation)]])

            self.rotmat_y = xp.array([[np.cos(self.y_rotation), 0., np.sin(self.y_rotation)],
                                      [0., 1., 0.],
                                      [-np.sin(self.y_rotation), 0., np.cos(self.y_rotation)]])

            self.rotmat_z = xp.array([[np.cos(self.z_rotation), -np.sin(self.z_rotation), 0.],
                                      [np.sin(self.z_rotation), np.cos(self.z_rotation), 0.],
                                      [0., 0., 1.]])
        else:
            self.rotmat_x, self.rotmat_y, self.rotmat_z = None, None, None

        self._density: xp.ndarray = None

    def apply_rotation(self, x_axis, y_axis, z_axis):
        if self.x_rotation == self.y_rotation == self.z_rotation == 0:
            return x_axis, y_axis, z_axis
        elif self.orthogonal_rotations:
            axes = (x_axis, y_axis, z_axis)
            # 'x':
            for _ in range(int(abs(self.x_rotation) / np.pi)):
                if self.x_rotation > 0:
                    axes = (axes[1], -axes[0], axes[2])
                else:
                    axes = (-axes[1], axes[0], axes[2])

            # 'y':
            for _ in range(int(abs(self.y_rotation) / np.pi)):
                if self.y_rotation > 0:
                    axes = (-axes[0], axes[2], -axes[1])
                else:
                    axes = (axes[0], -axes[2], axes[1])

            # 'z':
            for _ in range(int(abs(self.z_rotation) / np.pi)):
                if self.z_rotation > 0:
                    axes = (axes[2], -axes[1], axes[0])
                else:
                    axes = (-axes[2], axes[1], -axes[0])
            return axes
        else:
            coordinate_stack = xp.vstack([x_axis.ravel(), y_axis.ravel(), z_axis.ravel()]).T
            if self.x_rotation != 0:
                coordinate_stack = xp.einsum('ij,kj->ki', self.rotmat_x, coordinate_stack)
            if self.y_rotation != 0:
                coordinate_stack = xp.einsum('ij,kj->ki', self.rotmat_y, coordinate_stack)
            if self.z_rotation != 0:
                coordinate_stack = xp.einsum('ij,kj->ki', self.rotmat_z, coordinate_stack)
            return coordinate_stack[:, 0].reshape(x_axis.shape),\
                coordinate_stack[:, 1].reshape(y_axis.shape),\
                coordinate_stack[:, 2].reshape(z_axis.shape)

    def voxelize_simple(self) -> xp.ndarray:
        if not self.initialized():
            self._density = xp.empty((self.resolution, self.resolution, self.resolution))
            for nx, x in enumerate(self.radius_axis):
                for ny, y in enumerate(self.radius_axis):
                    for nz, z in enumerate(self.radius_axis):
                        XYZ = self.apply_rotation(x, y, z)
                        self._density[nx, ny, nz] = self.ref_index_array[int(self._get_density_point(XYZ))]
        return self._density

    def get_voxelize(self, x_axis: xp.ndarray = None, y_axis: xp.ndarray = None, z_axis: xp.ndarray = None) -> xp.ndarray:
        if not self.initialized():
            if type(self)._get_density_vectorized != ShapeTemplate3D._get_density_vectorized:
                if x_axis is None or y_axis is None or z_axis is None:
                    x_axis, y_axis, z_axis = self.apply_rotation(
                        *xp.meshgrid(self.radius_axis, self.radius_axis, self.radius_axis, indexing='ij'))
                return self.ref_index_array[self._get_density_vectorized(x_axis, y_axis, z_axis).astype(int)]
            else:
                return self.voxelize_simple()
        else:
            return self._density

    def voxelize(self):
        if not self.initialized():
            self._density = self.get_voxelize()

    def get_total_scattering_strength(self, k: float):
        delta = self.box_size/(self.resolution - 1)
        nref_volume_relative = self.get_voxelize()  # n - 1
        scatt_str = xp.abs(xp.sum(xp.exp(1j * delta * k * nref_volume_relative) - 1, axis=None) * delta * delta)
        if GPU_USED:
            return scatt_str.get()
        else:
            return scatt_str

    def _get_density_point(self, pos: Union[list[float, float, float], tuple[float, float, float], xp.ndarray]) -> int:
        pass

    def _get_density_vectorized(self, x_axis: xp.ndarray, y_axis: xp.ndarray, z_axis: xp.ndarray) -> xp.ndarray:
        pass

    def initialized(self) -> bool:
        return self._density is not None


class ShapeTemplate3D(ShapeTemplate):
    name = '3D_TEMPLATE'

    def get_voxelize_slice(self, slice_num: int) -> xp.ndarray:
        if not self.initialized():
            if type(self)._get_density_vectorized != ShapeTemplate3D._get_density_vectorized:
                z_axis_slice = xp.full((self.resolution, self.resolution), self.radius_axis[slice_num])
                x_axis, y_axis, z_axis = self.apply_rotation(self.x_axis_slice, self.y_axis_slice, z_axis_slice)
                return self.ref_index_array[self._get_density_vectorized(x_axis, y_axis, z_axis).astype(int)]
            else:
                raise Exception('Sliced voxelization is currently only supported for vectorized density definitions.')
        else:
            return self._density[..., slice_num]

    def get_real_grid(self):
        X, Y, Z = np.meshgrid(self.radius_axis, self.radius_axis, self.radius_axis, indexing='ij')
        if self.box_size is not None:
            X, Y, Z = X * self.box_size, Y * self.box_size, Z * self.box_size
        return X, Y, Z


class ShapeTemplate2D(ShapeTemplate):
    name = '2D_TEMPLATE'

    def get_real_grid(self):
        X, Y = np.meshgrid(self.radius_axis, self.radius_axis, indexing='ij')
        if self.box_size is not None:
            X, Y = X * self.box_size, Y * self.box_size
        return X, Y
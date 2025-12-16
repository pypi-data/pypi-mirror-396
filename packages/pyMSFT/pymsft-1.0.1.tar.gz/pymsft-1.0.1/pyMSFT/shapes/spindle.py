from .shapes import ShapeTemplate3D
from .. import xp

__all__ = ["Spindle"]


class Spindle(ShapeTemplate3D):
    name = 'Spindle'

    def __init__(self, aspect_ratio: float = 2, **kwargs):
        super().__init__(**kwargs)
        self.aspect_ratio = aspect_ratio
        if self.aspect_ratio < 1:
            raise Exception('aspect_ratio must be >= 1')

        self.width = 1 / self.aspect_ratio
        self.r_0 = self.width * (self.aspect_ratio**2 + 1) / 2

    def _get_density_vectorized(self, x_axis, y_axis, z_axis):
        meridian_curve = self.width - self.r_0 + xp.sqrt(self.r_0 * self.r_0 - z_axis * z_axis)
        return (x_axis * x_axis + y_axis * y_axis <= meridian_curve * meridian_curve) & (xp.abs(z_axis) < 1)

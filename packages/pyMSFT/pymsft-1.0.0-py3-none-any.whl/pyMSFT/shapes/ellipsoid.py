from .shapes import ShapeTemplate3D

__all__ = ['Ellipsoid', 'Sphere']


class Ellipsoid(ShapeTemplate3D):
    name = 'Ellipsoid'

    def __init__(self, a: float = 1, b: float = 2, c: float = 3, radius: float = None, **kwargs):
        super().__init__(**kwargs)
        max_range = max([a, b, c])
        if radius is None:
            self.radius_to_box_size = 1
        else:
            self.radius_to_box_size = ((2 * radius) / self.box_size)**2
        self.a = a / max_range
        self.b = b / max_range
        self.c = c / max_range

    def _get_density_point(self, pos):
        # as an example, this type of definition should be avoided in favor of _get_density_vectorized(...)
        if pos[0] * pos[0] / (self.a * self.a) \
                + pos[1] * pos[1] / (self.b * self.b) \
                + pos[2] * pos[2] / (self.c * self.c) <= self.radius_to_box_size:
            return 1
        else:
            return 0

    def _get_density_vectorized(self, x_axis, y_axis, z_axis):
        return (x_axis * x_axis / (self.a * self.a)
                + y_axis * y_axis / (self.b * self.b)
                + z_axis * z_axis / (self.c * self.c) <= self.radius_to_box_size)


class Sphere(Ellipsoid):
    name = 'Sphere'

    def __init__(self, **kwargs):
        super().__init__(a=1, b=1, c=1, **kwargs)

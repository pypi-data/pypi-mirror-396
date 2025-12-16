from .shapes import ShapeTemplate3D
from .. import xp, np, GPU_USED
from scipy.special import sph_harm
from typing import Union

__all__ = ['SphericalHarmonics']

class SphericalHarmonics(ShapeTemplate3D):
    name = 'SphericalHarmonics'

    def __init__(self, coefficients: Union[np.ndarray, list[list[int, int, float]], tuple[tuple[int, int, float]]] = None,
                 nphi: int = 32, ntheta: int = 32, **kwargs):
        super().__init__(**kwargs)

        if coefficients is None:
            coefficients = [[2, 2, 1]]

        if type(coefficients) == np.ndarray:
            self.coefficients = coefficients
        else:
            self.coefficients = np.array(coefficients)
        self.ncoefficients = len(self.coefficients)
        self.nphi = nphi
        self.ntheta = ntheta

        self.theta_axs = np.linspace(0, np.pi, self.ntheta)
        self.phi_axs = np.linspace(0, 2*np.pi, self.ntheta)
        self.dtheta_sh = self.theta_axs[1] - self.theta_axs[0]
        self.dphi_sh = self.phi_axs[1] - self.phi_axs[0]

        phis, thetas = np.meshgrid(self.phi_axs, self.theta_axs)
        phis, thetas = phis.ravel(), thetas.ravel()

        self.radii = np.zeros((self.ntheta * self.nphi))
        for icoeff in range(self.ncoefficients):
            coeff_n = int(self.coefficients[icoeff, 0])
            coeff_m = int(self.coefficients[icoeff, 1])
            if abs(coeff_m) > coeff_n:
                coeff_m = np.sign(coeff_m) * coeff_n
            coeff = self.coefficients[icoeff, 2]

            sph_leg_val = coeff * sph_harm(coeff_m, abs(coeff_n), phis, thetas)
            if coeff_m < 0:
                self.radii += np.imag(sph_leg_val)
            else:
                self.radii += np.real(sph_leg_val)

        maximum_radius = np.max(self.radii)
        norm = 1 / maximum_radius
        for i in range(self.ntheta * self.nphi):
            self.radii[i] *= norm
        if GPU_USED:
            self.radii = xp.asarray(self.radii)

    def _get_density_vectorized(self, x_axis, y_axis, z_axis):
        r = xp.sqrt(x_axis * x_axis + y_axis * y_axis + z_axis * z_axis)
        phi = xp.arctan2(y_axis, x_axis)
        theta = xp.arctan2(xp.sqrt(x_axis * x_axis + y_axis * y_axis), -z_axis)

        phi[phi < 0] += 2. * xp.pi
        float_phi = phi.ravel() / self.dphi_sh
        float_theta = theta.ravel() / self.dtheta_sh
        int_phi = float_phi.astype(int)
        int_theta = float_theta.astype(int)

        dec_phi = float_phi - int_phi
        dec_theta = float_theta - int_theta

        val = xp.take(self.radii, [xp.mod(int_phi, self.nphi) + self.nphi * xp.mod(int_theta, self.ntheta)])\
              * (1. - dec_phi) * (1. - dec_theta) \
              + xp.take(self.radii, [xp.mod((int_phi + 1), self.nphi) + self.nphi * xp.mod(int_theta, self.ntheta)])\
              * dec_phi * (1. - dec_theta) \
              + xp.take(self.radii, [xp.mod(int_phi, self.nphi) + self.nphi * xp.mod((int_theta + 1), self.ntheta)])\
              * (1. - dec_phi) * dec_theta \
              + xp.take(self.radii, [xp.mod((int_phi + 1), self.nphi) + self.nphi * xp.mod((int_theta + 1),
                                                                                           self.ntheta)])\
              * dec_phi * dec_theta

        return xp.reshape(r.ravel() <= abs(val), r.shape)

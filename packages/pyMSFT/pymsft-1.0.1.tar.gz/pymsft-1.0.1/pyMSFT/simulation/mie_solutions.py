import numpy as np
from scattnlay import scattnlay
from multiprocessing import Pool

__all__ = ['get_mie_q_detector', 'get_mie_spherical_detector', 'get_mie_flat_detector']

def _get_mie(Rsphere: float, wavelength: float, refIndex: complex, theta: np.ndarray, phi: np.ndarray, nworkers: int = None) -> np.ndarray:
    """
    Calculate the scattered fraction for a sphere using a Mie solution.
    Parameters
    ----------
    Rsphere : float
        Radius of the sphere.
    wavelength : float
        Wavelength of the incident light.
    refIndex : complex
        Complex refractive index of the sphere.
    r : np.ndarray
        Radial coordinates in spherical coordinates.
    theta : np.ndarray
        Polar angles in spherical coordinates.
    phi : np.ndarray
        Azimuthal angles in spherical coordinates.
    nworkers : int, optional
        Number of workers to use for parallel processing. If None or 1, no parallel processing is used.
    Returns
    -------
    np.ndarray
        Scattered fraction of light.
    """
    k_0 = 2 * np.pi / wavelength

    refractive_index_as_array = np.array([refIndex], dtype=np.complex128)
    size_parameter = np.array([2 * np.pi * Rsphere / wavelength], dtype=np.float64)
    unique_theta, unique_theta_indices = np.unique(theta, return_inverse=True)
    # print(f"Could reduce data by {(len(theta) - len(unique_theta)) / len(theta) * 100}%")

    # unique_theta = np.where(unique_theta == 0, 1e-10, unique_theta)  # ensure that theta does not contain 0
    # unique_theta = np.where(unique_theta == np.pi/2, np.pi/2 - 1e-10, unique_theta)  # ensure that theta does not contain pi/2

    # Calculate the scattering coefficients
    # Note: scattnlay provides a lot of other parameters. We only need the scattering matrix elements s1 and s2.
    if nworkers is None or nworkers == 1:
        _, _, _, _, _, _, _, _, s1, s2 = scattnlay(size_parameter, refractive_index_as_array, unique_theta)
    else:
        # Split the unique_theta array into nworkers chunks
        theta_chunks = np.array_split(unique_theta, nworkers)

        # Create a pool of workers
        with Pool(processes=nworkers) as pool:
            results = pool.starmap(scattnlay, [(size_parameter, refractive_index_as_array, chunk) for chunk in theta_chunks])

        # Combine the results
        s1 = np.concatenate([result[8] for result in results])
        s2 = np.concatenate([result[9] for result in results])


    # S1 is perpendicular to polarization, S2 is parallel to polarization
    s1 = s1[unique_theta_indices].reshape(theta.shape)
    s2 = s2[unique_theta_indices].reshape(theta.shape)

    return 1 / k_0**2 * (np.cos(phi) ** 2 * np.abs(s1) ** 2 + np.sin(phi) ** 2 * np.abs(s2) ** 2)


def get_mie_q_detector(Rsphere: float, wavelength: float, refIndex: complex, qx: np.ndarray,
                      qy: np.ndarray, nworkers: int = None) -> np.ndarray:
    """
    Parameters
    ----------
    Rsphere : float
        Radius of the sphere.
    wavelength : float
        Wavelength of the incident light.
    refIndex : complex
        Complex refractive index of the sphere.
    qx : np.ndarray
        qx-coordinates
    qy : np.ndarray
        qy-coordinates
    nworkers : int, optional
        Number of workers to use for parallel processing. If None or 1, no parallel processing is used.
    Returns
    -------
    np.ndarray
        Scattered fraction of light.
    """
    k_0 = 2 * np.pi / wavelength

    valid_q_mask = qx ** 2 + qy ** 2 < k_0 ** 2
    theta = np.arcsin(np.sqrt(qx[valid_q_mask] ** 2 + qy[valid_q_mask] ** 2) / k_0)
    phi = np.arctan2(qx[valid_q_mask], qy[valid_q_mask])

    scattering_fraction = np.full(qx.shape, np.nan)
    scattering_fraction[valid_q_mask] = _get_mie(Rsphere, wavelength, refIndex, theta, phi, nworkers) * 1 / np.cos(theta)
    return 1 / k_0**2 * scattering_fraction


def get_mie_spherical_detector(Rsphere: float, wavelength: float, refIndex: complex, r: float, theta: np.ndarray,
                               phi: np.ndarray, nworkers: int = None) -> np.ndarray:
    """
    Calculate the scattered fraction for a sphere using a Mie solution.
    Parameters
    ----------
    Rsphere : float
        Radius of the sphere.
    wavelength : float
        Wavelength of the incident light.
    refIndex : complex
        Complex refractive index of the sphere.
    r : np.ndarray
        Radial coordinates in spherical coordinates.
    theta : np.ndarray
        Polar angles in spherical coordinates.
    phi : np.ndarray
        Azimuthal angles in spherical coordinates.
    nworkers : int, optional
        Number of workers to use for parallel processing. If None or 1, no parallel processing is used.
    Returns
    -------
    np.ndarray
        Scattered fraction of light.
    """

    # Check if spherical coordinate arrays are valid
    if not (theta.shape == phi.shape):
        raise ValueError("theta, and phi must have the same shape.")
    if np.any(r <= 0):
        raise ValueError("All elements of r must be positive.")
    if np.any(theta < 0) or np.any(theta > np.pi):
        raise ValueError("All elements of theta must be in the range [0, pi].")

    return 1 / r ** 2 * _get_mie(Rsphere, wavelength, refIndex, theta, phi, nworkers)


def get_mie_flat_detector(Rsphere: float, wavelength: float, refIndex: complex, z_detector: float,
                         x: np.ndarray, y: np.ndarray, nworkers: int = None) -> np.ndarray:
    """
    Calculate the scattering coefficients for a sphere using the Mie theory.
    Parameters
    ----------
    Rsphere : float
        Radius of the sphere.
    wavelength : float
        Wavelength of the incident light.
    refIndex : complex
        Complex refractive index of the sphere.
    z_detector : float
        z-coordinate in Cartesian coordinates.
    x : np.ndarray
        x-coordinates in Cartesian coordinates.
    y : np.ndarray
        y-coordinates in Cartesian coordinates.
    nworkers : int, optional
        Number of workers to use for parallel processing. If None or 1, no parallel processing is used.
    Returns
    -------
    np.ndarray
        Scattered fraction of light.
    """

    if not (x.shape == y.shape):
        raise ValueError("x, y, and z must have the same shape.")

    r = np.sqrt(x ** 2 + y ** 2 + z_detector ** 2)
    theta = np.arccos(z_detector / r)
    phi = np.arctan2(x, y)

    return 1 / z_detector ** 2 * _get_mie(Rsphere, wavelength, refIndex, theta, phi, nworkers) * 1 / np.cos(theta) ** 3

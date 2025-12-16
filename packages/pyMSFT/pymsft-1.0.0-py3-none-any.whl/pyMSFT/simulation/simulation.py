import numpy as np
import pyfftw
from .. import xp, multiprocessing, GPU_USED
from ..shapes.shapes import ShapeTemplate3D, ShapeTemplate2D
from ..utilities import get_k_from_input, get_q_axis_and_angle
from typing import Union, Iterable
from tqdm import tqdm, trange
import functools


def apply_photon_statistics(image: np.ndarray, num_events: int, background_event_level: int = 0,
                                      *, seed=None) -> np.ndarray:
    """
    Apply Poisson statistics to an image.
    """

    generator = np.random.default_rng(seed)
    statisticed_image = generator.poisson((image/np.sum(image) * num_events).astype(np.float64))
    if background_event_level > 0:
        statisticed_image = statisticed_image + generator.poisson(background_event_level, size=statisticed_image.shape)

    return statisticed_image.astype(np.float64)


def get_linear_polarization_mask(K_X, k_0) -> np.ndarray:
    return 1 - (K_X / k_0) ** 2

class Simulation:
    name = ''
    shortname = ''

    def __str__(self):
        return self.shortname


class MultiSliceSimulation(Simulation):
    """
    Multislice MultiSliceSimulation class that contains the diffraction methods and ensures consistent definitions of the image
    and object planes.

    Attributes
    ----------
    Q_X : ndarray
        Projection of the scattering vector Q in x direction in 1/nm
    Q_Y : ndarray
        Projection of the scattering vector Q in y direction in 1/nm
    Q_Z : ndarray
        Projection of the scattering vector Q in z (propagation) direction in 1/nm
    Q_INVALID : ndarray
        Map of Q, where scattering > 90° occurs.
    Q : ndarray
        Length of the scattering vector Q in 1/nm
    Q_ANG : ndarray
        Scattering angle corresponding to scattering vector Q in [0, 2 pi]
    npix_fft : int
        Number of pixels for the resulting diffraction image in the image plane
    npix_real : int
        Number of pixels in the object plane
    box_size : float
        Size of the object plane box in nm
    k : float
        Defines photon energy of the imaging laser in 1/nm
    method: str, optional
        Defines the MSFT method from most to least accurate and slowest to fastest: ['pMSFT', 'MSFT', 'BORN', 'SAXS'].
    """

    def __init__(self, *, detector: dict = None, npix_fft: int = None, npix_real: int = None, box_size: float = None, box_delta: float = None,
                 k: float = None, wavelength: float = None, photon_energy: float = None, fixed_geometry_box: bool = False,
                 pool_size: int = 2, fftw_plan: str = 'FFTW_MEASURE', verbose: bool = False):
        """
        Initializes the Multislice MultiSliceSimulation class. All parameters are optional and can be set using `set_prop`
        function.

        Parameters
        ----------
        detector: dict, optional
            Defines the detector type, by default an Ewald sphere in k-space is assumed. This results in the simulated
            diffraction images being defined on Q_X, Q_Y pixel elements.
            Other options are the 'Spherical' detector or the 'Flat' detector, which implies phi and theta angles elements
            or x and y pixels respectively in real space.
            These detectors require a dictionary the distance to the detector in nm, e.g. {'type':'Spherical', 'distance': zdist}
            or {'type': 'Flat, 'distance': zdist}. The resulting diffraction images will then be defined on the axes of the
            detector and necessary transformation scalings will be applied.
        npix_fft : int, optional
            Number of pixels for the resulting diffraction image in the image plane
        npix_real : int, optional
            Number of pixels in the object plane
        box_size : float, optional
            Size of the object plane box in nm, exclusive input with box_delta
        box_delta : float, optional
            Distance of grid points in the image plane in nm, exclusive input with box_size
        k : float, optional
            Defines imaging laser using wavevector in 1/nm, exclusive with wavelength, photon_energy
        wavelength : float, optional
            Defines imaging laser using wavelength in nm, exclusive with k, photon_energy
        photon_energy : float, optional
            Defines imaging laser using photon_energy in eV, exclusive with k, wavelength
        fixed_geometry_box: bool, optional
            Toggles a check, whether npix_real and box_size or box_delta match the scattering geometry definition and prohibits dynamic changing of q axes according to scattering geometry
        pool_size : int, optional
            Defines the number of cores/workers to use during the calculation
        fftw_plan : str, optional
            Defines the FFTW plan to use for the FFT calculations. Default is 'FFTW_MEASURE', which is the most accurate but slowest option. Other options are 'FFTW_ESTIMATE', 'FFTW_PATIENT', and 'FFTW_EXHAUSTIVE'.
        verbose : bool, optional
            Toggle if verbose outputs are printed

        Raises
        ------
        AttributeError
            If the detector type is not 'Ewald', 'Spherical', or 'Flat' or if the required keys are not present in the detector dictionary.
        AttributeError
            If `box_size` and `box_delta` or 'k', 'wavelength', and 'photon_energy' were not defined exclusively
        """

        if detector is None:
            detector = {'type': 'Ewald', 'axes': None, 'distance': None}

        if detector['type'] == 'Spherical' or detector['type'] == 'Flat':
            if 'distance' not in detector:
                raise AttributeError("Real space detectors require 'distance' keys in the detector dictionary!")
        elif detector['type'] != 'Ewald':
            raise AttributeError("Detector type must be 'Ewald', 'Spherical', or 'Flat'!")

        if [x is not None for x in (box_size, box_delta)].count(True) > 1:
            raise AttributeError('Define either a box_size=..., or a box_delta=...!')
        elif box_size is None and box_delta is not None:
            box_size = (npix_real - 1) * box_delta

        k = get_k_from_input(k, wavelength, photon_energy)
        self.detector, self.npix_fft, self.npix_real, self.box_size, self.k_0, self.fixed_geometry_box, self.pool_size, self.fftw_plan, self.verbose\
            = detector, npix_fft, npix_real, box_size, k, fixed_geometry_box, pool_size, fftw_plan, verbose
        if [x is None for x in (npix_fft, npix_real, box_size, k)].count(True) > 1:
            self.K_X, self.K_Y, self.K_Z, self.Q_INVALID, self._Q_Z_shifted, self.Q, self.Q_ANG = None, None, None, None, None, None, None
        else:
            self._reset_q_axis_and_angle()

    def _reset_q_axis_and_angle(self):
        """
        Internal method that regenerates consistent definitions of the Q axes in the image plane
        """
        params = {'npix_fft': self.npix_fft, 'npix_real': self.npix_real, 'box_size': self.box_size, 'k': self.k_0}
        incorrect_params = [key for key, val in params.items() if val is None]
        if incorrect_params:
            raise Exception(f'MultiSliceSimulation not set up correctly, {incorrect_params}')
        self.K_X, self.K_Y, self.Q_Z, self.Q, self.Q_ANG = \
            get_q_axis_and_angle(npix_real=self.npix_real, npix_fft=self.npix_fft, box_size=self.box_size, k=self.k_0)
        self.Q_INVALID = self.K_X * self.K_X + self.K_Y * self.K_Y > self.k_0 * self.k_0
        self.K_Z = xp.sqrt(self.k_0**2 - self.K_X**2 - self.K_Y**2 + 0j)
        self._K_Z_shifted = xp.fft.fftshift(self.K_Z)
        self._Q_Z_shifted = xp.fft.fftshift(self.Q_Z)
        self._prepare_ffts()

    def _prepare_ffts(self):
        if GPU_USED:
            self._prepare_cupy_fft()
        else:
            self._prepare_pyfftw()

    def _prepare_cupy_fft(self):
        a = xp.random.random((self.npix_fft, self.npix_fft)).astype(xp.complex128)
        self._fftw_wisdom = xp.cupyx_get_fft_plan(a, axes=(0, 1), value_type='C2C')

    def _prepare_pyfftw(self):
        _fft_realspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
        _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

        _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1),
                                       direction='FFTW_FORWARD', flags=(self.fftw_plan,))

        self._fftw_wisdom = pyfftw.export_wisdom()

    def set_prop(self, **kwargs):
        """
        Method that changes the properties of the simulation class and maintains consistency with respect to image and
        object plane axes

        Parameters
        ----------
        **kwargs :
            Keyword arguments to set the properties of the simulation class. The following properties can be set:
            detector : dict
                Defines the detector type, by default an Ewald sphere in k-space is assumed. This results in the simulated diffraction images being defined on Q_X, Q_Y pixel elements.
                Other options are the 'Spherical' detector or the 'Flat' detector, which implies phi and theta angles elements or x and y pixels respectively in real space.
                These detectors require a dictionary the distance to the detector in nm, e.g. {'type':'Spherical', 'distance': zdist} or {'type': 'Flat, 'distance': zdist}.
                The resulting diffraction images will then be defined on the axes of the detector and necessary transformation scalings will be applied.
            npix_fft : int
                Number of pixels for the resulting diffraction image in the image plane
            npix_real : int
                Number of pixels in the object plane
            box_size : float
                Size of the object plane box in nm, exclusive input with box_delta
            box_delta : float
                Distance of grid points in the image plane in nm, exclusive input with box_size
            k : float
                Defines imaging laser using wavevector in 1/nm, exclusive with wavelength, photon_energy
            wavelength : float
                Defines imaging laser using wavelength in nm, exclusive with k, photon_energy
            photon_energy : float
                Defines imaging laser using photon_energy in eV, exclusive with k, wavelength
            pool_size : int
                Defines the number of cores/workers to use during the calculation
            verbose : bool, optional
                Toggle if verbose outputs are printed
        """
        if 'detector' in kwargs:
            if kwargs['detector']['type'] == 'Spherical' or kwargs['detector']['type'] == 'Flat':
                if 'distance' not in kwargs['detector']:
                    raise AttributeError("Real space detectors require 'distance' keys in the detector dictionary!")
            elif kwargs['detector']['type'] != 'Ewald':
                raise AttributeError("Detector type must be 'Ewald', 'Spherical', or 'Flat'!")
            self.detector = kwargs.pop('detector')

        prop_backup = (self.npix_fft, self.npix_real, self.box_size, self.k_0, self.pool_size, self.verbose)
        requires_new_q = False
        for key, val in kwargs.items():
            if key == 'photon_energy':
                self.k_0 = get_k_from_input(photon_energy=val)
            elif key == 'wavelength':
                self.k_0 = get_k_from_input(wavelength=val)
            elif key == 'box_delta':
                self.box_size = (self.npix_real + 1) * val
            elif hasattr(self, key):
                setattr(self, key, val)
            else:
                self.npix_fft, self.npix_real, self.box_size, self.k_0, self.pool_size, self.verbose = prop_backup
                raise Exception(f'Invalid property: {key}, reverted all changes.')

            if key != 'pool_size':
                requires_new_q = True

        if requires_new_q:
            self._reset_q_axis_and_angle()

    def get_diffraction_image(self,
                              shape_in: Union[Iterable[Union[ShapeTemplate3D, xp.ndarray]], Union[ShapeTemplate3D, xp.ndarray]],
                              *, output_axes: bool = False, normalize: bool = False, polarization_correction: bool = False):
        """
        Core method that returns the diffraction image for given inputs. Numerical diffraction schemes are defined in
        specific simulation subclasses.

        Parameters
        ----------
        shape_in : list of pyMSFT.ShapeTemplate3D or ndarray, or pyMSFT.ShapeTemplate3D or ndarray
            Input of pyMSFT.ShapeTemplates or ndarrays optionally also as an array_like.
        output_axes : bool, optional
            Toggle if Q axes are suppoesed to be output
        normalize : bool, optional
            Toggle if resulting diffraction images are supposed to be normalized

        Returns
        -------
        images : ndarray
            Resulting diffraction images in the image plane corresponding to the inputs shape_in.
            If complex=True this is the complex electric field in the image plane, otherwise it is the intensity.
            If normalize=True this output is normalized
        Q_X : ndarray, optional
            Projection of the scattering vector Q in x direction in 1/nm
        Q_Y : ndarray, optional
            Projection of the scattering vector Q in y direction in 1/nm
        Q_Z : ndarray, optional
            Projection of the scattering vector Q in z (propagation) direction in 1/nm
        Q : ndarray, optional
            Length of the scattering vector Q in 1/nm
        Q_ANG : ndarray, optional
            Scattering angle corresponding to scattering vector Q in [0, 2 pi]

        See Also
        --------
        pyMSFT.simulation.MultiSliceSimulation._get_diffraction_image :
            Internal simulation method that actually performs the numerical simulation scheme.
        """
        different_param = False
        if isinstance(shape_in, Iterable) and not isinstance(shape_in, xp.ndarray) and not isinstance(shape_in, np.ndarray):
            for shape_index, shape in enumerate(shape_in):
                different_param_in_iterable = False
                if isinstance(shape, ShapeTemplate3D):
                    if shape.box_size != self.box_size and shape.box_size is not None:
                        self.box_size = shape.box_size
                        different_param_in_iterable = True
                        different_param = True
                    if shape.resolution != self.npix_real and shape.resolution is not None:
                        self.npix_real = shape.resolution
                        different_param_in_iterable = True
                        different_param = True
                else:
                    if shape.shape[0] != self.npix_real:
                        self.npix_real = shape.shape[0]
                        different_param_in_iterable = True
                        different_param = True

                if different_param_in_iterable:
                    if self.fixed_geometry_box:
                        raise Exception("Fixed simulation geometry box definition does not match input geometry!")
                    if shape_index > 0:
                        raise AttributeError('Inconsistent shape parameters given!')

            if self.K_X is None and self.fixed_geometry_box:
                raise Exception("Fixed simulation geometry box not defined!")
            elif self.K_X is None or different_param:
                self._reset_q_axis_and_angle()

            if GPU_USED:
                images = [self._get_diffraction_image(shape, verbose=False) for shape in tqdm(shape_in, disable=not self.verbose,
                                                                                              desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]',
                                                                                              unit='sample')]

            else:
                with multiprocessing.Pool(self.pool_size) as p:
                    images = list(tqdm(p.imap(functools.partial(self._get_diffraction_image, verbose=False), shape_in),
                                       total=len(shape_in), disable=not self.verbose, desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]',
                                       unit='sample'))

        else:
            if isinstance(shape_in, ShapeTemplate3D):
                if shape_in.box_size != self.box_size and shape_in.box_size is not None:
                    self.box_size = shape_in.box_size
                    different_param = True
                if shape_in.resolution != self.npix_real and shape_in.resolution is not None:
                    self.npix_real = shape_in.resolution
                    different_param = True
            else:
                if shape_in.shape[0] != self.npix_real:
                    self.npix_real = shape_in.shape[0]
                    different_param = True
                if GPU_USED:
                    shape_in = xp.asarray(shape_in, dtype=xp.complex128)

            if self.fixed_geometry_box:
                if different_param:
                    raise Exception("Fixed simulation geometry box definition does not match input geometry!")
                if self.K_X is None:
                    raise Exception("Fixed simulation geometry box not defined!")
            elif self.K_X is None or different_param:
                self._reset_q_axis_and_angle()

            images = [self._get_diffraction_image(shape_in, verbose=self.verbose)]

        #Perform normalization
        if normalize:
            images = [xp.abs(image / xp.nanmax(xp.abs(image))) for image in images]
        else:
            images = [xp.abs(image) for image in images]

        box_delta = self.box_size / (self.npix_real - 1)
        fft_norm_correction = (box_delta**2 / (2 * np.pi))**2 # Normalization factor for the FFT2

        if polarization_correction:
            pol_mask = get_linear_polarization_mask(self.K_X, self.k_0)

        for indx, image in enumerate(images):
            # Perform invalid Q masking
            image[self.Q_INVALID] = xp.nan
            # Perform polarization correction
            if polarization_correction:
                image *= pol_mask

            #Perform detector scalings
            if self.detector['type'] == 'Ewald':
                image *= fft_norm_correction * self.k_0 / xp.real(self.K_Z)
                defined_axes = self.K_X, self.K_Y
            else:
                theta = xp.arcsin(xp.sqrt(self.K_X ** 2 + self.K_Y ** 2) / self.k_0)
                phi = xp.arctan2(self.K_X, self.K_Y)

                if self.detector['type'] == 'Spherical':
                    defined_axes = theta, phi
                    image *= fft_norm_correction * (self.k_0/self.detector['distance']) ** 2
                else: # 'Flat'
                    x = self.detector['distance'] * xp.tan(theta) * xp.cos(phi)
                    y = self.detector['distance'] * xp.tan(theta) * xp.sin(phi)
                    defined_axes = x, y
                    image *= fft_norm_correction * (self.k_0/self.detector['distance']) ** 2 * (xp.real(self.K_Z) / self.k_0)**3

            if GPU_USED:
                image = image.get()
                defined_axes = [x.get() for x in defined_axes]

            images[indx] = image

        if len(images) == 1:
            images = images[0]

        #Return images and axes
        if output_axes:
            return images, defined_axes
        else:
            return images


    def get_qaxes(self) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray):
        """
        Returns the Q axes of the simulation.

        Returns
        -------
        Q_X : ndarray, optional
            Projection of the scattering vector Q in x direction in 1/nm
        Q_Y : ndarray, optional
            Projection of the scattering vector Q in y direction in 1/nm
        Q_Z : ndarray, optional
            Projection of the scattering vector Q in z (propagation) direction in 1/nm
        Q : ndarray, optional
            Length of the scattering vector Q in 1/nm
        Q_ANG : ndarray, optional
            Scattering angle corresponding to scattering vector Q in [0, 2 pi]

        """

        if GPU_USED:
            return self.K_X.get(), self.K_Y.get(), self.K_Z.get(), self.Q.get(), self.Q_ANG.get()
        else:
            return self.K_X, self.K_Y, self.K_Z, self.Q, self.Q_ANG

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray], verbose: bool = False) -> np.ndarray:
        """
        Internal method that actually performs the calculation of the diffraction image. This function is overwritten by
        simulation subclasses.

        Parameters
        ----------
        shape : pyMSFT.ShapeTemplate3D or ndarray
            Definition of the object for which the diffraction is simulated. If an ndarray is used, it must be defined
            as a 3d array of refractive indices.
        complex_out : bool, optional
            Toggle if resulting diffraction image should be complex field instead of intenstity
        exit_field : bool, optional
            Toggle if resulting image should be the exit field instead of the diffraction image

        Returns
        -------
        images : ndarray
            Resulting diffraction image in the image plane

        See Also
        --------
        pyMSFT.simulation.pMSFT_Simulation._get_diffraction_image :
            Diffraction subclass containing propagation effects. Currently, the most accurate option for refractive
            indices that strongly differ from 1.
        pyMSFT.simulation.MSFT_Simulation._get_diffraction_image :
            Diffraction subclass containing basic material properies. Should only be used when the refractive index of
            the object is around 1.
        pyMSFT.simulation.BORN_Simulation._get_diffraction_image :
            Diffraction subclass neglecting all material properies. Should only be used when the refractive index of
            the object is 1.
        pyMSFT.simulation.SAXS_Simulation._get_diffraction_image :
            Diffraction subclass neglecting all material properies and assuming small angle diffraction. Significantly
            faster than the other methods but should only be used for very large k.
        """
        pass


class PMSFTSimulation(MultiSliceSimulation):
    """
    Multislice MultiSliceSimulation class that contains the propagation-MSFT diffraction method and ensures consistent
    definitions of the image and object planes. This diffraction method contains a complex model for the material
    properties allowing the description of propagation effects such as multiple scattering.
    """

    name = 'Propagation MultiSlice Fourier Transform'
    shortname = 'pMSFT' + ('(GPU)' if GPU_USED else '(CPU)')

    def _prepare_pyfftw(self):
        _fft_realspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
        _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

        _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1),
                                       direction='FFTW_FORWARD', flags=(self.fftw_plan,))
        _ifft_object = pyfftw.FFTW(_fft_fourspace, _fft_realspace, axes=(0, 1),
                                        direction='FFTW_BACKWARD', flags=(self.fftw_plan,))

        self._fftw_wisdom = pyfftw.export_wisdom()

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray],
                               complex_out: bool = False, exit_field: bool = False,
                               noise_level: float = None, verbose: bool = None) -> np.ndarray:
        if verbose is None:
            verbose = self.verbose

        if GPU_USED:
            _fft_realspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')

            ref_index_response = xp.ones((self.npix_fft, self.npix_fft), dtype='complex128')

        else:
            _fft_realspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            ref_index_response = pyfftw.ones_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            pyfftw.import_wisdom(self._fftw_wisdom)

            _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1), direction='FFTW_FORWARD',
                                      flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))
            _ifft_object = pyfftw.FFTW(_fft_fourspace, _fft_realspace, axes=(0, 1), direction='FFTW_BACKWARD',
                                       flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))

        padding = self.npix_fft // 2 - self.npix_real // 2

        _fft_realspace[:] = 1
        reference_input_field = xp.ones((self.npix_fft, self.npix_fft), dtype=complex)
        input_is_shape = isinstance(shape, ShapeTemplate3D)
        delta_z = self.box_size / (self.npix_real - 1)
        fourier_prop_slice = xp.exp(1j * delta_z * self._K_Z_shifted)
        for slice_index in trange(self.npix_real, disable=not verbose, desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]', unit='slice'):
            if input_is_shape:
                particle_slice_ref_index = shape.get_voxelize_slice(slice_index) + 1
            else:
                particle_slice_ref_index = shape[..., slice_index] + 1

            ref_index_response[padding:-padding, padding:-padding]\
                = xp.exp(1j * delta_z * self.k_0 * (particle_slice_ref_index - 1))
            xp.multiply(_fft_realspace, ref_index_response, out=_fft_realspace)
            if GPU_USED:
                _fft_fourspace = xp.cupyx_fft2(_fft_realspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _fft_object()
            xp.multiply(_fft_fourspace, fourier_prop_slice, out=_fft_fourspace)
            if GPU_USED:
                _fft_realspace = xp.cupyx_ifft2(_fft_fourspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _ifft_object()

        result = xp.fft.fft2(_fft_realspace) - xp.exp(1j * self.npix_real * delta_z * self._K_Z_shifted) * xp.fft.fft2(reference_input_field)

        return xp.fft.fftshift(xp.real(result * xp.conj(result)))

class HARESimulation(MultiSliceSimulation):
    """
    Multislice MultiSliceSimulation class that contains the propagation-MSFT diffraction method and ensures consistent
    definitions of the image and object planes. This diffraction method contains a complex model for the material
    properties allowing the description of propagation effects such as multiple scattering.
    """

    name = "Hare's  Paraxial Fourier Transform"
    shortname = 'HARE' + ('(GPU)' if GPU_USED else '(CPU)')

    def _prepare_pyfftw(self):
        _fft_realspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
        _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

        _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1),
                                       direction='FFTW_FORWARD', flags=(self.fftw_plan,))
        _ifft_object = pyfftw.FFTW(_fft_fourspace, _fft_realspace, axes=(0, 1),
                                        direction='FFTW_BACKWARD', flags=(self.fftw_plan,))

        self._fftw_wisdom = pyfftw.export_wisdom()

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray],
                               complex_out: bool = False, exit_field: bool = False,
                               noise_level: float = None, verbose: bool = None) -> np.ndarray:
        if verbose is None:
            verbose = self.verbose

        if GPU_USED:
            _fft_realspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')

            ref_index_response = xp.ones((self.npix_fft, self.npix_fft), dtype='complex128')

        else:
            _fft_realspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            ref_index_response = pyfftw.ones_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            pyfftw.import_wisdom(self._fftw_wisdom)

            _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1), direction='FFTW_FORWARD',
                                      flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))
            _ifft_object = pyfftw.FFTW(_fft_fourspace, _fft_realspace, axes=(0, 1), direction='FFTW_BACKWARD',
                                       flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))

        padding = self.npix_fft // 2 - self.npix_real // 2

        _fft_realspace[:] = 1
        reference_input_field = xp.ones((self.npix_fft, self.npix_fft), dtype=complex)
        input_is_shape = isinstance(shape, ShapeTemplate3D)
        delta_z = self.box_size / (self.npix_real - 1)
        paraxial_K_Z_shifted = xp.fft.fftshift(self.k_0 - (self.K_X**2 + self.K_Y**2)/ (2 * self.k_0))
        fourier_prop_slice = xp.exp(1j * delta_z * paraxial_K_Z_shifted)
        for slice_index in trange(self.npix_real, disable=not verbose, desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]', unit='slice'):
            if input_is_shape:
                particle_slice_ref_index = shape.get_voxelize_slice(slice_index) + 1
            else:
                particle_slice_ref_index = shape[..., slice_index] + 1

            ref_index_response[padding:-padding, padding:-padding]\
                = xp.exp(1j * delta_z * self.k_0 * (particle_slice_ref_index - 1))
            xp.multiply(_fft_realspace, ref_index_response, out=_fft_realspace)
            if GPU_USED:
                _fft_fourspace = xp.cupyx_fft2(_fft_realspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _fft_object()
            xp.multiply(_fft_fourspace, fourier_prop_slice, out=_fft_fourspace)
            if GPU_USED:
                _fft_realspace = xp.cupyx_ifft2(_fft_fourspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _ifft_object()

        result = xp.fft.fft2(_fft_realspace) - xp.exp(1j * self.npix_real * delta_z * paraxial_K_Z_shifted) * xp.fft.fft2(reference_input_field)

        return xp.fft.fftshift(xp.real(result * xp.conj(result)))


class MSFTSimulation(MultiSliceSimulation):
    """
    Multislice MultiSliceSimulation class that contains the MSFT diffraction method and ensures consistent definitions of the
    image and object planes. This diffraction method contains a simple model for the material properties.
    """

    name = 'MultiSlice Fourier Transform'
    shortname = 'MSFT' + (' (GPU)' if GPU_USED else ' (CPU)')

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray],
                               complex_out: bool = False, exit_field: bool = False,
                               noise_level: float = None, verbose: bool = None) -> np.ndarray:
        if verbose is None:
            verbose = self.verbose

        if GPU_USED:
            result = xp.zeros((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_realspace = xp.zeros((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')

        else:
            result = pyfftw.zeros_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_realspace = pyfftw.zeros_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            pyfftw.import_wisdom(self._fftw_wisdom)

            _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1), direction='FFTW_FORWARD',
                                      flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))

        padding = self.npix_fft // 2 - self.npix_real // 2

        ref_index_depth = xp.ones((self.npix_real, self.npix_real), dtype='complex128')

        input_is_shape = isinstance(shape, ShapeTemplate3D)

        delta_z = self.box_size / (self.npix_real - 1)

        for slice_index in trange(self.npix_real, disable=not verbose,
                                  desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]',
                                  unit='slice'):
            if input_is_shape:
                particle_slice_ref_index = shape.get_voxelize_slice(slice_index) + 1
            else:
                particle_slice_ref_index = shape[..., slice_index] + 1

            _fft_realspace[padding:-padding, padding:-padding] = \
                (xp.exp(1j * delta_z * self.k_0 * (particle_slice_ref_index - 1)) - 1) * ref_index_depth

            xp.multiply(ref_index_depth, xp.exp(1j * particle_slice_ref_index * self.k_0 * delta_z), out=ref_index_depth)

            if GPU_USED:
                _fft_fourspace = xp.cupyx_fft2(_fft_realspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _fft_object()

            result += _fft_fourspace * xp.exp(1j * self._K_Z_shifted * delta_z * (self.npix_real - slice_index))

        return xp.fft.fftshift(xp.real(result * xp.conj(result)))


class BORNSimulation(MultiSliceSimulation):
    """
    Multislice MultiSliceSimulation class that contains the diffraction method in Born's Approximation and ensures consistent
    definitions of the image and object planes. This diffraction method neglects all material properties.
    """

    name = 'Born\'s Approximation'
    shortname = 'Born' + (' (GPU)' if GPU_USED else ' (CPU)')

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray],
                               complex_out: bool = False, exit_field: bool = False,
                               noise_level: float = None, verbose: bool = None) -> np.ndarray:
        if verbose is None:
            verbose = self.verbose

        if GPU_USED:
            result = xp.zeros((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_realspace = xp.zeros((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')

        else:
            result = pyfftw.zeros_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_realspace = pyfftw.zeros_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            pyfftw.import_wisdom(self._fftw_wisdom)

            _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1), direction='FFTW_FORWARD',
                                      flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))

        padding = self.npix_fft // 2 - self.npix_real // 2
        delta_z = self.box_size / (self.npix_real - 1)
        fourier_prop_slice = xp.exp(1j * self._K_Z_shifted * delta_z)

        input_is_shape = isinstance(shape, ShapeTemplate3D)
        for slice_index in trange(self.npix_real, disable=not verbose,
                                  desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]',
                                  unit='slice'):
            if input_is_shape:
                particle_slice_ref_index = shape.get_voxelize_slice(slice_index) + 1
            else:
                particle_slice_ref_index = shape[..., slice_index] + 1

            _fft_realspace[padding:-padding, padding:-padding] = \
                (xp.exp(1j * delta_z * self.k_0 * (particle_slice_ref_index - 1)) - 1) * xp.exp(1j * self.k_0 * delta_z * slice_index)

            if GPU_USED:
                _fft_fourspace = xp.cupyx_fft2(_fft_realspace, axes=(0, 1), plan=self._fftw_wisdom)
            else:
                _fft_object()

            result += _fft_fourspace
            result *= fourier_prop_slice

        return xp.fft.fftshift(xp.real(result * xp.conj(result)))


class SAXSSimulation(MultiSliceSimulation):
    """
    Multislice MultiSliceSimulation class that contains the diffraction method in both Born's Approximation and the small angle
    approximation, while ensuring consistent definitions of the image and object planes. This diffraction method
    neglects all material properties and is only valid for very large photon energies of the imaging laser.
    """

    name = 'Small Angle X-ray Scattering'
    shortname = 'SAXS' + (' (GPU)' if GPU_USED else ' (CPU)')

    def _get_diffraction_image(self, shape: Union[ShapeTemplate3D, xp.ndarray],
                               complex_out: bool = False, exit_field: bool = False,
                               noise_level: float = None, verbose: bool = None) -> np.ndarray:
        if verbose is None:
            verbose = self.verbose

        if GPU_USED:
            _fft_realspace = xp.zeros((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = xp.empty((self.npix_fft, self.npix_fft), dtype='complex128')

        else:
            _fft_realspace = pyfftw.zeros_aligned((self.npix_fft, self.npix_fft), dtype='complex128')
            _fft_fourspace = pyfftw.empty_aligned((self.npix_fft, self.npix_fft), dtype='complex128')

            pyfftw.import_wisdom(self._fftw_wisdom)

            _fft_object = pyfftw.FFTW(_fft_realspace, _fft_fourspace, axes=(0, 1), direction='FFTW_FORWARD',
                                      flags=(self.fftw_plan, 'FFTW_WISDOM_ONLY'))

        delta_z = self.box_size / (self.npix_real - 1)
        if isinstance(shape, ShapeTemplate3D):  # 3d shape
            proj_dens = xp.zeros((shape.resolution, shape.resolution), dtype=complex)
            for slice_index in trange(self.npix_real, disable=not verbose,
                                      desc=self.shortname + f' [{self.npix_fft}x{self.npix_fft} @ {self.npix_real}]',
                                      unit='slice'):
                proj_dens += xp.exp(1j * delta_z * self.k_0 * shape.get_voxelize_slice(slice_index)) - 1
        elif len(xp.shape(shape)) == 3:  # 3d ndarray
            proj_dens = xp.sum(xp.exp(1j * delta_z * self.k_0 * shape) - 1, axis=2)

        padding_left = self.npix_fft // 2 - self.npix_real // 2
        padding_right = self.npix_fft // 2 - self.npix_real // 2

        _fft_realspace[padding_left:-padding_right, padding_left:-padding_right] = proj_dens
        if GPU_USED:
            _fft_fourspace = xp.cupyx_fft2(_fft_realspace, axes=(0, 1), plan=self._fftw_wisdom)
        else:
            _fft_object()
        _fft_fourspace *= xp.exp(1j * self.k_0 * delta_z * self.npix_real)
        return xp.fft.fftshift(xp.real(_fft_fourspace * xp.conj(_fft_fourspace)))

import re
import os
import time
import glob
import shutil
import itertools
import warnings
from typing import Dict, Optional
import urllib.request
from datetime import datetime
import importlib.metadata
import bz2



import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
# noinspection PyUnresolvedReferences
from line_racer.fortran_line_calculation_molliere2015 import line_calculation_molliere2015
# noinspection PyUnresolvedReferences
from line_racer.fortran_line_calculation_sampling_lines import sampling_lines
import zarr
import zarr.codecs
import zarr.storage


# Physical constants
amu = 1.660538921e-24  # g
h = 6.62606957e-27  # in erg s (1e-7 J s)
c_light = 2.99792458e10  # in cm/s
kB = 1.3806488e-16  # in erg/K
m_ele = 9.10938215e-28  # g
e = 4.80320425e-10  # Fr (cm^3/2 g^1/2 s^-1)
c2 = h * c_light / kB  # cm K

T_ref = 296.0  # Reference temperature in Kelvin
P_ref = 1.0  # Reference pressure in atm


class LineRacer:
    """
    Class to calculate line-by-line opacities for molecular species using either ExoMol, HITRAN or HITEMP databases.

    Parameters:

    resolution : float
        The resolution of the wavelength grid.
    cutoff : float
        The cutoff distance for line profile calculations.
    lambda_min : float
        The minimum wavelength in cm.
    lambda_max : float
        The maximum wavelength in cm.
    grid_type : str
        The type of grid to use ('log' or 'linear').
    hartmann : bool
        Whether to use Hartmann et al. 2002 treatment for the line wings.
    density_dist : float
        The distance for line density calculations.
    database : str
        The database to use ('exomol' or 'hitran').
    input_folder : str
        The folder containing the line list files.
    temperatures : list of float
        The list of temperatures in Kelvin.
    pressures : list of float
        The list of pressures in bar.
    sharp_burrows : bool
        Whether to use sharp Burrows et al. 2000 cutoff.
    mass : float
        The molecular mass in amu.
    force_molliere2015_method : bool
        Whether to force the use of the line profile calculation method from Mollière et al. 2015.
    species_isotope_dict : dict
        A dictionary mapping isotope identifiers to their abundances.
    line_list_name : str
        The name of the line list to use.
    broadening_species_dict : dict, optional
        A dictionary containing broadening parameters (gamma and n_temp).
    constant_broadening : list of float, optional
        A list containing constant broadening parameters [gamma, n_temp].
    broadening_type : str
        The type of broadening to use ('sharp_burrows', 'constant', 'exomol_table', 'hitran_table').
    """

    def __init__(self,
                 resolution: float = 1e6,
                 cutoff: float = 100.0,
                 lambda_min: float = 1.1e-5,
                 lambda_max: float = 2.5e-2,
                 grid_type: str = 'log', # todo: implement that also just a linear grid can be used -> for now need to interpolated if linear grid is desired. # noqa E501
                 hartmann: bool = True,
                 density_dist: float = 10.0,
                 database: str = None,
                 input_folder: str = None,
                 temperatures: list[float] = None,
                 pressures: list[float] = None,
                 mass: float = None,
                 force_molliere2015_method: bool = False,
                 species_isotope_dict: Optional[Dict[str, float]] = None,
                 line_list_name: str = None,
                 broadening_species_dict: Optional[Dict[str, float]] = None,
                 constant_broadening: list[float] = None,
                 broadening_type: str = None,
                 ):

        self.line_density = None
        self.grid_size = None
        self.resolution = resolution
        self.cutoff = cutoff
        self.lambda_min = lambda_min
        self.lambda_max = lambda_max
        self.hartmann = hartmann
        self.grid_type = grid_type
        self.density_dist = density_dist
        self.input_folder = input_folder
        self.temperatures = temperatures
        self.pressures = pressures
        self.line_list = line_list_name
        self.force_molliere2015_method = force_molliere2015_method
        self.N_rd_numbers = 1e8
        self.wavenumber_grid = None
        self.transition_files_list = None
        self.isotope_mass = mass
        self.species_isotope_dict = species_isotope_dict
        self.broadening_species_dict = broadening_species_dict
        self.intensity_correction_grid = None
        self.sigma_correction_grid = None
        self.gamma_sigma_ratio_correction_grid = None
        self.sub_grid_borders = None
        self.no_sub_grid = None
        self.broadening_information_hitran_dict = {}
        self.constant_broadening = constant_broadening
        self.include_all_isotopes_in_filename = False
        self.broadening_type = broadening_type
        self.no_intensity_correction = False
        self.verbose = False

        self.pressures = np.array(self.pressures) / 1.01325  # convert pressure from bar to atm
        self.temperatures = np.array(self.temperatures)

        if self.constant_broadening:
            self.constant_broadening = np.array(self.constant_broadening)  # (gamma, n_temp)
            self.constant_broadening[0] *= 1.01325  # convert from /bar to /atm

        if database == 'hitemp':
            self.database = 'hitran'
        else:
            self.database = database

        if self.database not in ['exomol', 'hitran']:
            raise KeyError("Database must be either 'exomol' or 'hitran'")

        if self.input_folder is None:
            raise KeyError("Input folder must be provided")

        if not self.species_isotope_dict:
            raise KeyError("Isotope dictionary must be provided, at least with the one isotope of interest")

        if self.broadening_type not in ['sharp_burrows', 'constant', 'exomol_table', 'hitran_table']:
            raise KeyError("Broadening type must be either 'sharp_burrows', 'default', "
                           "'exomol_table' or 'hitran_table'")

        if self.broadening_type == 'constant' and self.constant_broadening is None:
            raise KeyError("For 'constant' broadening type, constant_broadening parameter must be provided")

        if self.broadening_type == 'sharp_burrows' and self.database == 'hitran':
            raise KeyError("'sharp_burrows' broadening type can not be used with HITRAN database, since it is not "
                           "providing j quantum numbers")

        if ((self.broadening_type == 'exomol_table' or self.broadening_type == 'hitran_table') and
                self.broadening_species_dict is None):
            raise KeyError("For 'exomol_table' or 'hitran_table' broadening type, broadening_species_dict parameter "
                           "must be provided")

        if self.database == 'exomol' and self.isotope_mass is None:
            raise KeyError("For the ExoMol database, the molecular mass must be provided")

        print(f'Calculating the opacity for the following species: '
              f'{list(self.species_isotope_dict.keys())}')

        self.exomol_to_global = {
            # H20
            "1H2-16O": 1,
            "1H2-18O": 2,
            "1H2-17O": 3,
            "1H-2H-16O": 4,
            "1H-2H-18O": 5,
            "1H-2H-17O": 6,
            "2H2-16O": 129,

            # CO2
            "12C-16O2": 7,
            "13C-16O2": 8,
            "16O-12C-18O": 9,
            "16O-12C-17O": 10,
            "16O-13C-18O": 11,
            "16O-13C-17O": 12,
            "12C-18O2": 13,
            "17O-12C-18O": 14,
            "12C-17O2": 121,
            "13C-18O2": 15,
            "18O-13C-17O": 120,
            "13C-17O2": 122,

            # O3
            "16O3": 16,
            "16O-16O-18O": 17,
            "16O-18O-16O": 18,
            "16O-16O-17O": 19,
            "16O-17O-16O": 20,

            # N2O
            "14N2-16O": 21,
            "14N-15N-16O": 22,
            "15N-14N-16O": 23,
            "14N2-18O": 24,
            "14N2-17O": 25,

            # CO
            "12C-16O": 26,
            "13C-16O": 27,
            "12C-18O": 28,
            "12C-17O": 29,
            "13C-18O": 30,
            "13C-17O": 31,

            # CH4
            "12C-1H4": 32,
            "13C-1H4": 33,
            "12C-1H3-2H": 34,
            "13C-1H3-2H": 35,

            # O2
            "16O2": 36,
            "16O-18O": 37,
            "17O-16O": 38,

            # NO
            "14N-16O": 39,
            "15N-16O": 40,
            "14N-18O": 41,

            # SO2
            "32S-16O2": 42,
            "34S-16O2": 43,
            "33S-16O2": 137,
            "16O-32S-18O": 138,

            # NO2
            "14N-16O2": 44,
            "15N-16O2": 130,

            # NH3
            "14N-1H3": 45,
            "15N-1H3": 46,

            # HNO3
            "1H-14N-16O3": 47,
            "1H-15N-16O3": 117,

            # OH
            "16O-1H": 48,
            "18O-1H": 49,
            "16O-2H": 50,

            # HF
            "1H-19F": 51,
            "2H-19F": 110,

            # HCl
            "1H-35Cl": 52,
            "1H-37Cl": 53,
            "2H-35Cl": 107,
            "2H-37Cl": 108,

            # HBR
            "1H-79Br": 54,
            "1H-81Br": 55,
            "2H-79Br": 111,
            "2H-81Br": 112,

            # HI
            "1H-127I": 56,
            "2H-127I": 113,

            # ClO
            "35Cl-16O": 57,
            "37Cl-16O": 58,

            # OCS
            "16O-12C-32S": 59,
            "16O-12C-34S": 60,
            "16O-13C-32S": 61,
            "16O-12C-33S": 62,
            "18O-12C-32S": 63,
            "16O-13C-34S": 135,

            # H2CO
            "1H2-12C-16O": 64,
            "1H2-13C-16O": 65,
            "1H2-12C-18O": 66,

            # HOCl
            "1H-16O-35Cl": 67,
            "1H-16O-37Cl": 68,

            # N2
            "14N2": 69,
            "14N-15N": 118,

            # HCN
            "1H-12C-14N": 70,
            "1H-13C-14N": 71,
            "1H-12C-15N": 72,

            # CH3Cl
            "12C-1H3-35Cl": 73,
            "12C-1H3-37Cl": 74,

            # H2O2
            "1H2-16O2": 75,

            # C2H2
            "12C2-1H2": 76,
            "1H-12C-13C-1H": 77,
            "1H-12C2-2H": 105,

            # C2H6
            "12C2-1H6": 78,
            "12C-1H3-13C-1H3": 106,

            # PH3
            "31P-1H3": 79,

            # COF2
            "12C-16O-19F2": 80,
            "13C-16O-19F2": 119,

            # H2S
            "32S-19F6": 126,
            "1H2-32S": 81,
            "1H2-34S": 82,
            "1H2-33S": 83,

            # HCOOH
            "1H-12C-16O2-1H": 84,

            # HO2
            "1H-16O2": 85,

            # O
            "16O": 86,

            # ClONO2
            "35Cl-16O-14N-16O2": 127,
            "37Cl-16O-14N-16O2": 128,

            # NO+
            "14N-16O_p": 87,

            # HOBr
            "1H-16O-79Br": 88,
            "1H-16O-81Br": 89,

            # C2H4
            "12C2-1H4": 90,
            "12C-1H2-13C-1H2": 91,

            # CH3OH
            "12C-1H3-16O-1H": 92,

            # CH3Br
            "12C-1H3-79Br": 93,
            "12C-1H3-81Br": 94,

            # CH3CN
            "12C-1H3-12C-14N": 95,

            # CF4
            "12C-19F4": 96,

            # C4H2
            "12C4-1H2": 116,

            # HC3N
            "1H-12C3-14N": 109,

            # H2
            "1H2": 103,
            "1H-2H": 115,

            # CS
            "12C-32S": 97,
            "12C-34S": 98,
            "13C-32S": 99,
            "12C-33S": 100,

            # SO3
            "32S-16O3": 114,

            # C2N2
            "12C2-14N2": 123,

            # COCl2
            "12C-16O-35Cl2": 124,
            "12C-16O-35Cl-37Cl": 125,

            # SO
            "32S-16O": 146,
            "34S-16O": 147,
            "32S-18O": 148,

            # CH3F
            "12C-1H3-19F": 144,

            # GeH4
            "74Ge-1H4": 139,
            "72Ge-1H4": 140,
            "70Ge-1H4": 141,
            "73Ge-1H4": 142,
            "76Ge-1H4": 143,

            # CS2
            "12C-32S2": 131,
            "32S-12C-34S": 132,
            "32S-12C-33S": 133,
            "13C-32S2": 134,

            # CH3I
            "12C-1H3-127I": 145,

            # NF3
            "14N-19F3": 136,
        }

        global_iso_ids = [1, 2, 3, 4, 5, 6, 129, 7, 8, 9, 10, 11, 12, 13, 14, 121, 15, 120, 122, 16, 17, 18, 19, 20, 21,
                          22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 137,
                          138, 44, 130, 45, 46, 47, 117, 48, 49, 50, 51, 110, 52, 53, 107, 108, 54, 55, 111, 112, 56,
                          113, 57, 58, 59, 60, 61, 62, 63, 135, 64, 65, 66, 67, 68, 69, 118, 70, 71, 72, 73, 74, 75, 76,
                          77, 105, 78, 106, 79, 80, 119, 126, 81, 82, 83, 84, 85, 86, 127, 128, 87, 88, 89, 90, 91, 92,
                          93, 94, 95, 96, 116, 109, 103, 115, 97, 98, 99, 100, 114, 123, 124, 125, 146, 147, 148, 144,
                          139, 140, 141, 142, 143, 131, 132, 133, 134, 145, 136]

        local_iso_ids = [1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 11, 12, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2,
                         3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 1, 2, 1, 2, 1, 2, 1, 2, 3, 1, 2, 1, 2, 3,
                         4, 1, 2, 3, 4, 1, 2, 1, 2, 1, 2, 3, 4, 5, 6, 1, 2, 3, 1, 2, 1, 2, 1, 2, 3, 1, 2, 1, 1, 2, 3, 1,
                         2, 1, 1, 2, 1, 1, 2, 3, 1, 1, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 3, 4, 1,
                         1, 1, 2, 1, 2, 3, 1, 1, 2, 3, 4, 5, 1, 2, 3, 4, 1, 1]

        afgl_codes = [161, 181, 171, 162, 182, 172, 262, 626, 636, 628, 627, 638, 637, 828, 827, 727, 838, 837, 737,
                      666, 668, 686, 667, 676, 446, 456, 546, 448, 447, 26, 36, 28, 27, 38, 37, 211, 311, 212, 312, 66,
                      68, 67, 46, 56, 48, 626, 646, 636, 628, 646, 656, 4111, 5111, 146, 156, 61, 81, 62, 19, 29, 15,
                      17, 25, 27, 19, 11, 29, 21, 17, 27, 56, 76, 622, 624, 632, 623, 822, 634, 126, 136, 128, 165, 167,
                      44, 45, 124, 134, 125, 215, 217, 1661, 1221, 1231, 1222, 1221, 1231, 1111, 269, 369, 29, 121, 141,
                      131, 126, 166, 6, 5646, 7646, 46, 169, 161, 221, 231, 2161, 219, 211, 2124, 29, 2211, 1224, 11,
                      12, 22, 24, 32, 23, 26, 4224, 2655, 2657, 26, 46, 28, 219, 411, 211, 11, 311, 611, 222, 224, 223,
                      232, 217, 4999]

        mol_ids = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5,
                   5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 15,
                   15, 16, 16, 16, 16, 17, 17, 18, 18, 19, 19, 19, 19, 19, 19, 20, 20, 20, 21, 21, 22, 22, 23, 23, 23,
                   24, 24, 25, 26, 26, 26, 27, 27, 28, 29, 29, 30, 31, 31, 31, 32, 33, 34, 35, 35, 36, 37, 37, 38, 38,
                   39, 40, 40, 41, 42, 43, 44, 45, 45, 46, 46, 46, 46, 47, 48, 49, 49, 50, 50, 50, 51, 52, 52, 52, 52,
                   52, 53, 53, 53, 53, 54, 55]

        molid_afgl = [str(i) + str(j) for i, j in zip(mol_ids, afgl_codes)]
        molid_local_id = [str(i) + str(j) for i, j in zip(mol_ids, local_iso_ids)]
        self.molid_local_id_to_global_id = dict(zip(molid_local_id, global_iso_ids))
        self.global_to_molid_afgl = dict(zip(global_iso_ids, molid_afgl))
        self.global_to_molid = dict(zip(global_iso_ids, mol_ids))
        self.global_to_local_iso_id = dict(zip(global_iso_ids, local_iso_ids))

        if self.database == 'hitran':
            missing_keys = [key for key in self.species_isotope_dict if key not in self.exomol_to_global]
            if missing_keys:
                raise KeyError(f"The provided isotope(s) {missing_keys} are not known to be in HITRAN. If that is "
                               f"wrong, update the exomol_to_global dictionary and probably the global isotope IDs list"
                               f" in the _read_hitran_transition_files function and the mol_param.txt file.")

    @staticmethod
    def check_installation():
        """
        Run a test to check if the line racer installation is working properly.
        """
        print("Running line racer installation test...")

        try:
            from line_racer.fortran_line_calculation_molliere2015 import line_calculation_molliere2015
            from line_racer.fortran_line_calculation_sampling_lines import sampling_lines

        except ImportError as ie:
            print("Fortran modules could not be imported. Please check your installation.")
            raise ie

        print("line racer installation test passed successfully.")

        pass

    @staticmethod
    def prt_pressure_temperature_grid():
        """
        Pressure and temperature grid for the opacity calculations, following the default pRT format.

        Returns:

            pressures : numpy.ndarray
                The grid of pressures in bar.
            temperatures : numpy.ndarray
                The grid of temperatures in Kelvin.
        """
        pressures = np.logspace(-6, 3, 10)  # in bar
        temperatures = np.array([81.14113604736988, 109.60677358237457, 148.05862230132453, 200.0, 270.163273706,
                                 364.940972297, 492.968238926, 665.909566306, 899.521542126, 1215.08842295,
                                 1641.36133093, 2000., 2217.17775249, 2500., 2750., 2995.0, 3250., 3500., 3750., 4000.])

        return pressures, temperatures

    def _prt_line_by_line_grid(self):
        """
        Calculate the grid of wavelengths for the given resolution.

        Parameters:

        res : float
            The resolution of the grid.
        lambda_min : float
            The minimum wavelength.
        lambda_max : float
            The maximum wavelength.

        Returns:

        lambda : numpy.ndarray
            The grid of wavelengths.
        """

        lambd = [self.lambda_min]
        lambda_current = self.lambda_min
        while lambda_current < self.lambda_max:
            lambda_current = lambda_current * np.exp(1/self.resolution)
            lambd.append(lambda_current)

        self.grid_size = len(lambd)
        self.wavenumber_grid = 1 / np.array(lambd[::-1])

        pass

    def __do_rd_numbers(self):
        """
        Generate random numbers for the thermal and pressure broadening parameters.

        Input:

        N_rd_numbers : int
            The number of random numbers to generate.

        Returns:

        random_gauss_sample : numpy.ndarray
            The random numbers for the thermal broadening parameter.
        random_lorentz_sample : numpy.ndarray
            The random numbers for the pressure broadening parameter.
        max_gamma_rd : float
            The maximum value of the pressure broadening random numbers.
        max_sigma_rd : float
            The maximum value of the thermal broadening random numbers.
        """

        n_samples = int(self.N_rd_numbers)
        random_number = 2 * np.random.rand(n_samples) - 1
        random_gauss_sample = np.random.normal(np.zeros(n_samples), 1)
        random_lorentz_sample = np.tan(random_number * np.pi / 2)

        max_gamma_rd = np.max(abs(random_lorentz_sample))
        max_sigma_rd = np.max(abs(random_gauss_sample))

        del random_number

        return random_gauss_sample, random_lorentz_sample, max_gamma_rd, max_sigma_rd

    def __calculate_line_density(self, bin_indices, lines_per_bin):
        """
        Calculate the line density for the given bin indices and lines per bin.

        Parameters:

        bin_indices : numpy.ndarray
            The indices of the bins.
        lines_per_bin : numpy.ndarray
            The number of lines per bin.

        Returns:

        counts_in_env : numpy.ndarray
            The line density for each bin index.
        """

        n_bins = len(lines_per_bin)
        pref = np.concatenate((np.array([0]), np.cumsum(lines_per_bin, dtype=np.int64)))

        lefts = np.clip(bin_indices - self.density_dist, 0, n_bins - 1).astype(int)
        rights = np.clip(bin_indices + self.density_dist, 0, n_bins - 1).astype(int)

        counts_in_env = pref[rights + 1] - pref[lefts]

        del lefts, rights

        return counts_in_env

    def _read_exomol_states_file(self):
        """
        Read the ExoMol states file and extract the relevant parameters. Possibility to read in the .bz2 compressed file
        or the uncompressed .states file.

        Parameters:

        input_folder : str
            The folder containing the ExoMol .states file.

        Returns:

        state_energies : numpy.ndarray
            The energies of the states.
        state_degeneracies : numpy.ndarray
            The degeneracies of the states.
        state_j : numpy.ndarray
            The rotational quantum numbers of the states.
        """

        t_states = time.time()
        if self.verbose:
            print("Reading ExoMol states file...")

        # Read the ExoMol data file
        states_file_name = glob.glob(os.path.join(self.input_folder, '*.states'))

        if not states_file_name:  # if empty
            states_file_name = glob.glob(os.path.join(self.input_folder, '*.states.bz2'))

        if (len(glob.glob(self.input_folder + '/*.states')) != 1
                and len(glob.glob(self.input_folder + '/*.states.bz2')) != 1):
            raise FileNotFoundError(f"There should be exactly one .states or .states.bz2 file in the input folder")

        states_file_name = states_file_name[0]

        compression = "bz2" if states_file_name.endswith(".bz2") else None

        states_df = pd.read_fwf(
            states_file_name,
            compression=compression,
            header=None,
            colspecs=[(0, 12), (13, 25), (26, 32), (33, 40)],
            names=["id", "energy", "g", "J"]
        )

        state_energies = states_df["energy"].to_numpy()
        state_degeneracies = states_df["g"].to_numpy()
        state_j = states_df["J"].to_numpy()

        del states_df

        if self.verbose:
            print(f"Finished reading ExoMol states file in {time.time() - t_states:.2f} seconds.")

        return state_energies, state_degeneracies, state_j

    def _read_exomol_transition_file(self, transition_file_path, state_energies, state_degeneracies, state_j):
        """
        Read the ExoMol transition files and extract the relevant parameters.

        Parameters:

        transition_file_path : str
            The path to the ExoMol transition file.
        state_energies : numpy.ndarray
            The energies of the states.
        state_degeneracies : numpy.ndarray
            The degeneracies of the states.
        state_j : numpy.ndarray
            The rotational quantum numbers of the states.

        Returns:

        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers of the transitions.
        einstein_a : numpy.ndarray
            The Einstein A coefficients of the transitions.
        g_upper : numpy.ndarray
            The degeneracies of the upper states.
        j_upper : numpy.ndarray
            The rotational quantum numbers of the upper states.
        j_lower : numpy.ndarray
            The rotational quantum numbers of the lower states.
        energies_lower_state : numpy.ndarray
            The energies of the lower states.
        """

        t_trans = time.time()
        if self.verbose:
            print("Reading ExoMol transition file...")

        compression = "bz2" if transition_file_path.endswith(".bz2") else None

        if compression == "bz2":

            upper_id, lower_id, einstein_a = [], [], []

            with bz2.open(transition_file_path, "rt") as f:
                for line in f:
                    upper_id.append(int(line[0:12]))
                    lower_id.append(int(line[13:25]))
                    einstein_a.append(float(line[26:36]))

            upper_id = np.array(upper_id, dtype=np.int64)
            lower_id = np.array(lower_id, dtype=np.int64)
            einstein_a = np.array(einstein_a, dtype=np.float64)

        else:

            with open(transition_file_path, "rt") as f:
                lines = f.read().splitlines()

            upper_id = np.array([int(line[0:12]) for line in lines], dtype=np.int64)
            lower_id = np.array([int(line[13:25]) for line in lines], dtype=np.int64)
            einstein_a = np.array([float(line[26:36]) for line in lines], dtype=np.float64)

            del lines

        energies_upper_state = state_energies[upper_id - 1]
        energies_lower_state = state_energies[lower_id - 1]
        effective_wavenumbers = np.abs(energies_upper_state - energies_lower_state)

        j_upper = state_j[upper_id - 1]
        j_lower = state_j[lower_id - 1]
        g_upper = state_degeneracies[upper_id - 1]

        del upper_id, lower_id, energies_upper_state

        if self.verbose:
            print(f"Finished reading ExoMol transition file in {time.time() - t_trans:.2f} seconds.")

        return effective_wavenumbers, einstein_a, g_upper, j_upper, j_lower, energies_lower_state

    def _read_exomol_pressure_shift(self):
        """
        Read the ExoMol pressure shift file and extract the shift dependent on the diet.
        """
        # todo: needs to be implemented as soon as exomol published more pressure shift data!
        pass

    def _read_hitran_transition_files(self, transition_file_path):
        """
        Read the HITRAN transition files and extract the relevant parameters.
        Corrects the intensities for their terrestrial abundance and the isotope abundance given by the user
        (if provided).

        Parameters:

        transition_file_path : str
            The path to the HITRAN transition file.

        Returns:

        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers of the transitions.
        line_intensities : numpy.ndarray
            The line intensities of the transitions.
        einstein_a : numpy.ndarray
            The Einstein A coefficients of the transitions.
        energies_lower_state : numpy.ndarray
            The energies of the lower states.
        global_iso_ids : numpy.ndarray
            The global isotope IDs of the transitions.
        iso_masses : numpy.ndarray
            The isotope masses of the transitions.
        global_iso_ids : numpy.ndarray
            The global isotope IDs of the transitions.
        """

        t_hitran = time.time()
        if self.verbose:
            print("Reading HITRAN transition file...")

        global_ids = np.array([self.exomol_to_global[k] for k in self.species_isotope_dict.keys()])
        local_ids = np.array([self.global_to_local_iso_id[k] for k in global_ids])
        mol_id = self.global_to_molid[global_ids[0]]
        local_ids_to_user_abundances = {self.global_to_local_iso_id[self.exomol_to_global[name]]:
                                        abundance for name, abundance in self.species_isotope_dict.items()
                                        }

        mol_params = pd.read_csv('data/molparam.txt', sep=r'\s+')

        if transition_file_path.endswith('.out'):
            dat = pd.read_csv(transition_file_path, sep=',')

        elif transition_file_path.endswith('.par'):

            # todo: rewrite using the normal read in without pandas for speed
            colspecs = [
                (0, 2),  # I2: Isotopologue ID
                (2, 3),  # I1: Isotopologue number
                (3, 15),  # ν (wavenumber): F12.6
                (15, 25),  # S (line intensity): E10.3
                (25, 35),  # A (Einstein A): E10.3
                (35, 40),  # γ_air: F5.4
                (40, 45),  # γ_self: F5.3
                (45, 55),  # E″: F10.4
                (55, 59),  # n_air: F4.2
                (59, 67),  # δ_air: F8.6
                # (146, 153),  # g′: F7.1
                # (153, 160)  # g″: F7.1
            ]

            column_names = [
                "molec_id",  # Isotopologue ID (I2)
                "local_iso_id",  # Isotope number (I1)
                "nu",  # Wavenumber
                "sw",  # Line strength
                "a",  # Einstein A
                "gamma_air",  # Air-broadened Lorentz width
                "gamma_self",  # Self-broadened Lorentz width
                "elower",  # Lower state energy
                "n_air",  # Temperature exponent for γ_air
                "delta_air",  # Air pressure shift
                # "gp",  # Statistical weight of upper state (can also be Local upper)
                # "gpp",  # Statistical weight of lower state (can also be Local lower)
            ]
            dat = pd.read_fwf(transition_file_path, colspecs=colspecs, names=column_names)
        else:
            raise FileNotFoundError("No transition files found in the file path. Please check the path.")

        # Todo: Test that
        if mol_id == 2:
            dat['local_iso_id'] = dat['local_iso_id'].replace({'A': 11, 'B': 12}).astype(int)

        dat = dat[dat.local_iso_id.isin(local_ids)]

        mol_id_local_iso_id = str(mol_id) + dat['local_iso_id'].astype(str)
        global_iso_ids_lines = np.array(mol_id_local_iso_id.map(self.molid_local_id_to_global_id).values)

        # todo adapt that to the new molparam.txt file?
        filtered_mol_params = mol_params[mol_params.MolID == mol_id]
        iso_dict = dict(zip(filtered_mol_params['IsoID'], filtered_mol_params['MolarMass(g)']))

        isotope_masses = dat['local_iso_id'].map(iso_dict).values

        # correct for missing e_lower
        dat = dat[dat.elower != "##########"]

        # replace #### with nans, very time expensive!!
        for col in dat.columns:
            dat.loc[dat[col].astype(str).str.contains("#"), col] = 0.0

        # correct for the isotope abundance
        isotope_abundance = mol_params[mol_params.MolID == mol_id]['IsoAbundance'].values
        isotope_ids = mol_params[mol_params.MolID == mol_id]['IsoID'].values

        # Todo: check how the 0 index isotope id works here and in total
        original_isotope_dict = dict(zip(isotope_ids, isotope_abundance))

        # correct the intensity for the isotope abundance
        dat.sw /= dat.local_iso_id.map(original_isotope_dict)

        # correct the intensity for the isotope abundance given by the user
        dat.sw *= dat.local_iso_id.map(local_ids_to_user_abundances)

        effective_wavenumbers = np.array(dat['nu'].values, dtype=np.float64)
        line_intensities = np.array(dat['sw'].values, dtype=np.float64)
        einstein_a = np.array(dat['a'].values, dtype=np.float64)
        energies_lower_state = np.array(dat['elower'].values, dtype=np.float64)

        delta_ref = np.zeros_like(effective_wavenumbers, dtype=np.float64)

        if self.broadening_type == 'hitran_table':
            for species, mixing_ratio in self.broadening_species_dict.items():

                try:
                    gamma_species = np.array(dat[f'gamma_{species}'].values, dtype=np.float64)  # in /cm/atm

                    try:
                        n_temp_species = np.array(dat[f'n_{species}'].values, dtype=np.float64)
                    except KeyError:
                        n_temp_species = np.zeros_like(gamma_species, dtype=np.float64)
                        warnings.warn(f"Missing temperature exponent for species '{species}', "
                                      f"using default value of 0.")

                    self.broadening_information_hitran_dict[species] = (mixing_ratio, gamma_species, n_temp_species)

                except KeyError:
                    warnings.warn(f"Missing broadening data for species '{species}', skipping.")
                    continue

                try:
                    delta_ref += np.array(dat[f'delta_{species}'].values, dtype=np.float64)

                except KeyError:
                    warnings.warn(f"Missing pressure shift data for species '{species}', skipping.")
                    continue

        del dat, iso_dict, mol_id_local_iso_id,

        if effective_wavenumbers.size == 0:
            raise ValueError('No lines found for the given isotope selection in the HITRAN file.')

        if self.verbose:
            print(f"Finished reading HITRAN transition file in {time.time() - t_hitran:.2f} seconds.")

        return (effective_wavenumbers, line_intensities, energies_lower_state, delta_ref, einstein_a, isotope_masses,
                global_iso_ids_lines)

    def __subgrid_molliere2015_method(self):
        """
        Create the subgrid for the given parameters.

        Parameters:

        delta_lambda_steps : float
            The step size for the subgrid.

        Returns:

        no_sub_grid : int
            The number of sub grids.
        sub_grid_borders : list
            The borders of the sub grids.
        """

        delta_lambda_steps = 10000.0
        no_sub_grid = int(self.grid_size / delta_lambda_steps)

        if (no_sub_grid == 0) or (delta_lambda_steps == self.grid_size):
            no_sub_grid = 1
            sub_grid_borders = [1, self.grid_size]

        else:
            no_sub_grid = no_sub_grid + 1
            sub_grid_borders = [1]

            for i in np.arange(1, no_sub_grid):
                sub_grid_borders.append(delta_lambda_steps * i)

            sub_grid_borders.append(self.grid_size)

        self.sub_grid_borders = sub_grid_borders
        self.no_sub_grid = no_sub_grid

        pass

    def _calculate_qtable(self, temperature, path_to_partition_function_file, global_iso_ids_unique=None):
        """
        Calculate the Q-table for the given parameters.

        Parameters:

        temperature : float
            The temperature in K.
        path_to_partition_function_file : str
            The path to the partition function file.
        global_iso_ids_unique : numpy.ndarray
            The unique global isotope IDs.

        Returns:

        q_att : numpy.ndarray
            The partition function values for ExoMol.
        q_ref_over_t_dict : dict
            The partition function ratio dictionary for HITRAN.
        """

        if self.database == 'exomol':

            if len(glob.glob(f"{path_to_partition_function_file}*.pf")) != 1:
                raise FileNotFoundError("Not the right number of .pf files (it must be 1)")

            q_temp = np.loadtxt(glob.glob(f"{path_to_partition_function_file}*.pf")[0])
            # interpolate for the temperature
            f = interp1d(q_temp.T[0], q_temp.T[1], bounds_error=False, fill_value=(q_temp[0][1], q_temp[-1][1]))
            q_att = f(temperature)

            return q_att

        elif self.database == 'hitran':

            # Already normalizing the Q to the reference temperature, which is globally set to 296K.
            ratio_q_ref_q_t = np.zeros_like(global_iso_ids_unique, dtype=np.float64)

            for i in range(len(global_iso_ids_unique)):

                if len(glob.glob(f"{path_to_partition_function_file}*{global_iso_ids_unique[i]}.txt")) != 1:

                    pattern = f"{path_to_partition_function_file}*{global_iso_ids_unique[i]}.txt"

                    raise ValueError(f'Not the right number of .txt partition function files. Found '
                                     f'{len(glob.glob(pattern))}, 1 expected for isotope ID {global_iso_ids_unique[i]}')

                qt = np.loadtxt(glob.glob(f"{path_to_partition_function_file}*{global_iso_ids_unique[i]}.txt")[0])

                f = interp1d(qt.T[0], qt.T[1], bounds_error=False, fill_value=(qt[0][1], qt[-1][1]))
                q_ref = f(T_ref)
                ratio_q_ref_q_t[i] = q_ref / f(temperature)

            q_ref_over_t_dict = dict(zip(global_iso_ids_unique, ratio_q_ref_q_t))

            return q_ref_over_t_dict

    def _broadening_exomol_table(self, path_to_broadening_file, pressure, temperature, j_lower_transition,
                                 j_upper_transition):
        """
        Read the ExoMol broadening tables and calculate the pressure broadening parameter

        Parameters:

        path_to_broadening_file : str
            The path to the ExoMol broadening file.
        pressure : float
            The pressure in atm.
        temperature : float
            The temperature in K.
        j_lower_transition : numpy.ndarray
            The rotational quantum numbers of the lower states.
        j_upper_transition : numpy.ndarray
            The rotational quantum numbers of the upper states.

        Returns:

        gamma_medium_broadened : numpy.ndarray
            The pressure broadening parameter.
        """

        gamma_medium_broadened = np.zeros_like(j_lower_transition, dtype=np.float64)

        for species, mixing_ratio in self.broadening_species_dict.items():

            data_a0 = []
            data_m0 = []

            perturber = str(species)
            file = glob.glob(f"{path_to_broadening_file}*_{perturber}*.broad")

            a0 = False
            m0 = False

            with open(file[0], 'r') as f:

                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    if parts[0] == "a0" and len(parts) == 4:
                        typ, gamma_per, n_per, j_lower = parts
                        data_a0.append((int(j_lower), float(gamma_per), float(n_per)))

                        a0 = True

                    elif parts[0] == "m0" and len(parts) == 4:
                        typ, gamma_per, n_per, m = parts
                        data_m0.append((int(m), float(gamma_per), float(n_per)))

                        m0 = True

                    else:
                        continue

            if not (a0 or m0):
                # todo: implement a1 diet and others
                warnings.warn(f"Missing data for perturber {perturber}.")
                continue

            if a0 and m0:
                warnings.warn(f"Found unknown option of m0 and a0 diet in one file for perturber {perturber}.")

            if a0:
                if self.verbose:
                    print(f"Found a0 diet for perturber {perturber}.", flush=True)

                df_a0 = pd.DataFrame(data_a0, columns=["J_lower", "gamma", "n"])
                max_j = df_a0["J_lower"].max()
                row_maxj = df_a0[df_a0["J_lower"] == max_j]
                gamma_cap = row_maxj["gamma"].values[0]
                n_cap = row_maxj["n"].values[0]

                max_j_transition = np.max(j_lower_transition)

                gamma_perturber = np.full(max_j_transition + 1, gamma_cap)
                n_perturber = np.full(max_j_transition + 1, n_cap)

                for _, row_J in df_a0.iterrows():
                    j_low_file = int(row_J["J_lower"])
                    if j_low_file <= max_j_transition:
                        gamma_perturber[j_low_file] = row_J["gamma"]
                        n_perturber[j_low_file] = row_J["n"]

                gamma_medium = gamma_perturber[j_lower_transition] * 1.01325  # convert from /bar to /atm
                n_temp = n_perturber[j_lower_transition]
                gamma_medium_broadened += ((T_ref / temperature)**n_temp * gamma_medium *
                                           pressure / P_ref * mixing_ratio)

                del gamma_medium, n_temp, gamma_perturber, n_perturber

            if m0:
                if self.verbose:
                    print(f"Found m0 diet for perturber {perturber}.", flush=True)

                df_m0 = pd.DataFrame(data_m0, columns=["m", "gamma", "n"])

                delta_j = j_upper_transition - j_lower_transition
                m_transitions = np.zeros_like(j_lower_transition)

                m_transitions[delta_j == -1] = -j_lower_transition[delta_j == -1]
                m_transitions[delta_j == 0] = j_lower_transition[delta_j == 0]
                m_transitions[delta_j == +1] = j_lower_transition[delta_j == +1] + 1

                min_m_transition = np.min(m_transitions)
                max_m_transition = np.max(m_transitions)

                max_m = df_m0["m"].max()
                row_maxm = df_m0[df_m0["m"] == max_m]
                gamma_cap = row_maxm["gamma"].values[0]
                n_cap = row_maxm["n"].values[0]

                gamma_perturber = np.full(max_m_transition - min_m_transition + 1, gamma_cap)
                n_perturber = np.full(max_m_transition - min_m_transition + 1, n_cap)

                for _, row_m in df_m0.iterrows():
                    m = int(row_m["m"])
                    if min_m_transition <= m <= max_m_transition:
                        m_val = m - min_m_transition
                        gamma_perturber[m_val] = row_m["gamma"]
                        n_perturber[m_val] = row_m["n"]

                gamma_medium = gamma_perturber[m_transitions - min_m_transition] * 1.01325  # convert from /bar to /atm
                n_temp = n_perturber[m_transitions - min_m_transition]
                gamma_medium_broadened += ((T_ref / temperature)**n_temp * gamma_medium *
                                           pressure / P_ref * mixing_ratio)

                del gamma_medium, n_temp, gamma_perturber, n_perturber

        return gamma_medium_broadened

    def _calculate_broadening(self, pressure, temperature, j_upper=None, j_lower=None, effective_wavenumbers=None):
        """
        Calculate the pressure broadening parameter for the given parameters.

        Parameters:

        pressure : float
            The pressure in atm.
        temperature : float
            The temperature in K.
        j_upper : numpy.ndarray
            The rotational quantum numbers of the upper states.
        j_lower : numpy.ndarray
            The rotational quantum numbers of the lower states.
        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers of the transitions.

        Returns:

        gamma_broadened : numpy.ndarray
            The pressure broadening parameter.
        """

        if self.broadening_type == 'sharp_burrows':
            if self.verbose:
                print('Sharp Burrows broadening', flush=True)
            j_lower[j_lower >= 30] = 30
            gamma_sb = (0.1 - j_lower * 2e-3) / 2
            n_temp = 0 * np.ones_like(j_lower, dtype=np.float64)
            gamma_broadened = ((T_ref / temperature) ** n_temp * gamma_sb * pressure)

        elif self.broadening_type == 'constant':
            if self.verbose:
                print('Using default broadening values', flush=True)
            gamma_default, n_temp_default = self.constant_broadening
            gamma_broadened = (T_ref / temperature) ** n_temp_default * gamma_default * pressure

        elif self.broadening_type == 'exomol_table':
            if self.verbose:
                print('Using ExoMol broadening table', flush=True)
            gamma_broadened = self._broadening_exomol_table(self.input_folder, pressure, temperature, j_lower, j_upper)

        elif self.broadening_type == 'hitran_table':

            gamma_broadened = np.zeros_like(effective_wavenumbers, dtype=np.float64)

            if self.broadening_information_hitran_dict == {}:
                raise KeyError("No broadening information provided for HITRAN data, choose Sharp and Burrows 2007"
                               "broadening or a constant value for broadening.")

            for species in self.broadening_information_hitran_dict.keys():
                mixing_ratio, gamma_species, n_temp_species = self.broadening_information_hitran_dict[species]

                gamma_broadened += (gamma_species * (pressure / P_ref) *
                                    (T_ref / temperature) ** n_temp_species * mixing_ratio)

        else:
            raise KeyError("Broadening type not recognized. Choose from 'sharp_burrows', 'constant', "
                           "'exomol_table', or 'hitran_table'.")

        return gamma_broadened

    @staticmethod
    def __read_intensity_correction_cube(filename):
        """
        Reads the intensity correction cube from a file. Can be calculated with the script cutoff_correction_grid.py.
        The file should contain the following arrays:
        - sigma_grid: The sigma values.
        - gamma_sigma_ratio_grid: The gamma/sigma values.
        - cutoff_grid: The cutoff values.
        - correction_grid: The intensity correction values.
        The arrays should be stored in a .npz file.

        Parameters:

        filename : str
            The name of the file to read.

        Returns:

        cutoff_values : numpy.ndarray
            The cutoff values.
        sigma_grid : numpy.ndarray
            The sigma values.
        gamma_sigma_ratio_grid : numpy.ndarray
            The gamma/sigma values.
        correction_grid : numpy.ndarray
            The intensity correction values.
        """

        # read in the npz file
        data = np.load(filename)

        # extract the arrays
        sigma_grid = np.asfortranarray(data['sigma_grid'])
        gamma_sigma_ratio_grid = np.asfortranarray(data['gamma_sigma_ratio_grid'])
        intensity_correction_grid = np.asfortranarray(data["correction_grid"])
        cutoff_grid = np.asfortranarray(data["cutoff_grid"])

        del data

        return sigma_grid, gamma_sigma_ratio_grid, cutoff_grid, intensity_correction_grid

    def __interpolate_cutoff_correction_cube(self):
        """
        Interpolates the cutoff correction cube for a given set of cutoff values.

        Parameters:

        correction_cube : numpy.ndarray
            Dimensions: (N_cutoff, N_sigma, N_gamma_sigma_ratio_grid)
            The cutoff correction cube.

        Returns:

        C_corr_interp : numpy.ndarray
            The interpolated cutoff correction values.
        """

        if self.cutoff > 5000:
            self.no_intensity_correction = True
            warnings.warn(f'Cutoff value too large for the correction grid ({self.cutoff} 1/cm). '
                          f'Maximum is 5000 1/cm for the current correction cubes. \n You can create your own '
                          f'correction cube with the script intensity_correction_precalculation.py. Now proceeding '
                          f'without intensity correction!')
            pass

        else:

            if self.hartmann:
                path_to_intensity_correction_grid = 'data/correction_grid_Hartmann_cutoff.npz'
                sigma_grid, gamma_sigma_ratio_grid, cutoff_grid, correction_cube = (
                    self.__read_intensity_correction_cube(path_to_intensity_correction_grid))
                print('Using Hartmann and cutoff intensity correction grid')
            else:
                path_to_intensity_correction_grid = 'data/correction_grid_cutoff.npz'
                sigma_grid, gamma_sigma_ratio_grid, cutoff_grid, correction_cube = (
                    self.__read_intensity_correction_cube(path_to_intensity_correction_grid))
                print(f'Using cutoff intensity correction grid and interpolated to {self.cutoff}1/cm')

            # Interpolate the cutoff correction grid
            interp_func = interp1d(cutoff_grid, correction_cube, axis=0, kind='linear', bounds_error=True)
            self.intensity_correction_grid = interp_func(self.cutoff)
            self.sigma_correction_grid = sigma_grid
            self.gamma_sigma_ratio_correction_grid = gamma_sigma_ratio_grid

            del interp_func, cutoff_grid, correction_cube

            pass

    def _intensity_correction(self, lorentz_widths, doppler_widths):
        """
        Calculate the intensity correction for the given parameters.

        Parameters:

        path_to_grid : str
            The path to the intensity correction grid file.
        lorentz_widths : numpy.ndarray
            The Lorentz widths of the lines.
        doppler_widths : numpy.ndarray
            The Doppler widths of the lines.

        Returns:

        line_intensity_cutoff_correction : numpy.ndarray
            The intensity correction factors for each line.
        """

        if self.sigma_correction_grid is None:
            self.__interpolate_cutoff_correction_cube()
            warnings.warn('Interpolate the cutoff correction grid before the calculation for saving RAM!\n'
                          'However proceeding now...')

        n_sigma_correction_grid = len(self.sigma_correction_grid)
        n_gamma_sigma_ratio_correction_grid = len(self.gamma_sigma_ratio_correction_grid)

        n_lines = len(lorentz_widths)

        # interpolate for every line
        line_intensity_cutoff_correction = sampling_lines.intp_c_corr(
            n_lines, n_sigma_correction_grid,
            n_gamma_sigma_ratio_correction_grid,
            self.sigma_correction_grid,
            self.gamma_sigma_ratio_correction_grid,
            self.intensity_correction_grid,
            lorentz_widths/doppler_widths,
            doppler_widths)

        return line_intensity_cutoff_correction

    @staticmethod
    def __split_lines_by_intensity(effective_wavenumbers, line_intensities, bin_width=1.0, top_n_per_bin=200):
        """
        Split the lines into important and minor lines based on their intensities within specified bins.

        Parameters:

        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers of the transitions.
        line_intensities : numpy.ndarray
            The line intensities of the transitions.
        bin_width : float
            The width of each bin in 1/cm.
        top_n_per_bin : int
            The number of top lines to select per bin.

        Returns:

        important_lines_indices : numpy.ndarray
            The indices of the important lines.
        minor_lines_indices : numpy.ndarray
            The indices of the minor lines.
        lines_per_bin : numpy.ndarray
            The number of lines per bin.
        bin_indices : numpy.ndarray
            The indices of the bins.
        """

        # number of intervals in the range
        min_wavenumber = np.min(effective_wavenumbers)
        max_wavenumber = np.max(effective_wavenumbers)

        n_bins = int(np.floor((max_wavenumber - min_wavenumber) / bin_width)) + 1

        bin_indices = np.floor((effective_wavenumbers - min_wavenumber) / bin_width).astype(int)
        bin_indices = np.clip(bin_indices, 0, n_bins - 1)

        lines_per_bin = np.bincount(bin_indices, minlength=n_bins)

        important_lines_indices = []

        for bin_i in range(n_bins):

            indices_bin = np.where(bin_indices == bin_i)[0]

            if len(indices_bin) == 0:
                continue
            bin_intensities = line_intensities[indices_bin]

            if len(indices_bin) <= top_n_per_bin:
                strongest_indices_bin = indices_bin
            else:
                strongest_indices_bin = indices_bin[np.argsort(bin_intensities)[-top_n_per_bin:]]

            important_lines_indices.extend(strongest_indices_bin)
        important_lines_indices = np.array(important_lines_indices)

        minor_lines_indices = np.ones_like(line_intensities, dtype=bool)
        minor_lines_indices[important_lines_indices] = False

        del indices_bin, bin_intensities, strongest_indices_bin

        return important_lines_indices, minor_lines_indices, lines_per_bin, bin_indices

    @staticmethod
    def _calculate_doppler_width(temperature, effective_wavenumbers, isotope_mass):
        """
        Calculate the Doppler width for a given set of effective wavenumbers and isotope mass.

        Parameters:

        temperature : float
            The temperature in K.
        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers in 1/cm.
        isotope_mass : float
            The isotope mass in atomic mass units (amu).

        Returns:

        doppler_widths : numpy.ndarray
            The Doppler widths in 1/cm.
        """

        doppler_widths = effective_wavenumbers/(c_light * np.sqrt(2.0)) * np.sqrt(2.0 * kB *
                                                                                  temperature/(isotope_mass * amu))

        return doppler_widths

    @staticmethod
    def _calculate_lorentz_width(gamma_medium_broadened, einstein_a):
        """
        Calculate the Lorentz width for a given set of medium broadening and Einstein A coefficients.

        Parameters:

        gamma_medium_broadened : numpy.ndarray
            The medium broadening in 1/cm.
        einstein_a : numpy.ndarray
            The Einstein A coefficients in 1/s.

        Returns:

        lorentz_width : numpy.ndarray
            The Lorentz widths in 1/cm.
        """

        if np.shape(gamma_medium_broadened) != np.shape(einstein_a) and np.ndim(gamma_medium_broadened) != 0:
            raise ValueError("The shapes of gamma_medium_broadened and einstein_a do not match! They must be the same "
                             "or the broadening parameter must be a scalar.")

        lorentz_width = gamma_medium_broadened + einstein_a / (c_light * 4.0 * np.pi)

        return lorentz_width

    @staticmethod
    def _apply_pressure_shift(pressure, delta_ref, effective_wavenumbers):
        """
        Calculate and apply the pressure shift for a given set of effective wavenumbers and pressure.

        Parameters:

        pressure : float
            The pressure in atm.
        delta_ref : numpy.ndarray
            The reference pressure shift in 1/cm/atm.
        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers in 1/cm.

        Returns:

        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers corrected for pressure shift.
        """

        # todo remove when done comparing:)
        delta_ref = np.zeros_like(effective_wavenumbers)

        effective_wavenumbers += delta_ref * pressure / P_ref

        return effective_wavenumbers

    def _calculate_intensity(self, temperature, effective_wavenumbers, einstein_a, energies_lower_state, g_upper=None,
                             q_temp=None, global_iso_ids=None, line_intensities_t_ref=None):
        """
        Calculate the intensity for a given set of effective wavenumbers, Doppler widths, Lorentz widths,
        and line intensities.

        Parameters:

        temperature : float
            The temperature in K.
        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers in 1/cm.
        einstein_a : numpy.ndarray
            The Einstein A coefficients in 1/s.
        energies_lower_state : numpy.ndarray
            The lower state energies in 1/cm.
        g_upper : numpy.ndarray, optional
            The upper state degeneracies. Required for ExoMol database.
        q_temp : float, optional
            The partition function at the given temperature. Required for ExoMol database.
        global_iso_ids : numpy.ndarray, optional
            The global isotope IDs. Required for HITRAN database.
        line_intensities : numpy.ndarray, optional
            The line intensities at reference temperature. Required for HITRAN database.

        Returns:

        line_intensities : numpy.ndarray
            The line intensities at the given temperature.
        """

        if self.database == 'exomol':
            line_intensities = (einstein_a / (8 * np.pi * c_light) * g_upper *
                                np.exp(-c2 * energies_lower_state / temperature) / effective_wavenumbers ** 2
                                / q_temp * (1 - np.exp(-c2 * effective_wavenumbers / temperature)))

            return line_intensities

        elif self.database == 'hitran':

            global_ids_unique = np.unique(global_iso_ids)
            ratio_q_ref_q_t_dict = self._calculate_qtable(temperature, self.input_folder, global_ids_unique)
            ratio_q_ref_q_t = np.array([ratio_q_ref_q_t_dict[gid] for gid in global_iso_ids])

            line_intensities = (line_intensities_t_ref * ratio_q_ref_q_t *
                                (np.exp(-c2 * energies_lower_state / temperature) /
                                 np.exp(-c2 * energies_lower_state / T_ref)))
            line_intensities *= ((1 - np.exp(-c2 * effective_wavenumbers / temperature)) /
                                 (1 - np.exp(-c2 * effective_wavenumbers / T_ref)))

            return line_intensities

    def _calculate_pressure_temperature_point(self, pressure, temperature,
                                              effective_wavenumbers, einstein_a, g_up, j_upper, j_lower,
                                              energies_lower_state, iso_masses, line_intensities_t_ref, delta_ref,
                                              global_iso_ids, sampling_boost=1.0, coarse_grid_switch=True):

        """
        Calculate the opacity for a given pressure and temperature point. Splits between line calculations with the
        method from Molliere et al. 2015 and a sampling method described in Min 2017. The split is done based on the
        number of lines and their intensity.

        Parameters:

        pressure : float
            The pressure in atm.
        temperature : float
            The temperature in K.
        effective_wavenumbers : numpy.ndarray
            The effective wavenumbers in 1/cm.
        einstein_a : numpy.ndarray
            The Einstein A coefficients in 1/s.
        g_up : numpy.ndarray
            The upper state degeneracies.
        j_upper : numpy.ndarray
            The upper state rotational quantum numbers.
        j_lower : numpy.ndarray
            The lower state rotational quantum numbers.
        energies_lower_state : numpy.ndarray
            The lower state energies in 1/cm.
        iso_masses : numpy.ndarray
            The isotope masses in amu.
        line_intensities : numpy.ndarray
            The line intensities at reference temperature.
        global_iso_ids : numpy.ndarray
            The global isotope IDs.
        delta_ref : numpy.ndarray
            The reference pressure shift in 1/cm/atm.
        sampling_boost : float, optional
            The boost factor for the sampling.
        coarse_grid_switch : bool, optional
            Whether to use the coarse grid method.

        Returns:

        sigma : numpy.ndarray
            The opacity in cm^2/molecule.
        """

        t_start = time.time()

        if self.database == 'hitran':

            # Calculate the pressure broadened widths
            gamma_broadened = self._calculate_broadening(pressure, temperature, j_lower=j_lower, j_upper=j_upper,
                                                         effective_wavenumbers=effective_wavenumbers)

            # Calculate the Lorentz widths
            lorentz_widths = self._calculate_lorentz_width(gamma_broadened, einstein_a)

            # Calculate the Doppler widths
            doppler_widths = self._calculate_doppler_width(temperature, effective_wavenumbers, iso_masses)

            # Calculate the line intensities
            line_intensities = self._calculate_intensity(temperature, effective_wavenumbers, einstein_a,
                                                         energies_lower_state, global_iso_ids=global_iso_ids,
                                                         line_intensities_t_ref=line_intensities_t_ref)
            # Apply the pressure shift
            effective_wavenumbers = self._apply_pressure_shift(pressure, delta_ref, effective_wavenumbers)

            del gamma_broadened

        elif self.database == 'exomol':

            # Calculate the partition function
            q_temp = self._calculate_qtable(temperature, self.input_folder)

            # Calculate the pressure broadened widths
            gamma_broadened = self._calculate_broadening(pressure, temperature, j_upper=j_upper, j_lower=j_lower,
                                                         effective_wavenumbers=effective_wavenumbers)

            # Calculate the Doppler widths
            doppler_widths = self._calculate_doppler_width(temperature, effective_wavenumbers, self.isotope_mass)

            # Calculate the Lorentz widths
            lorentz_widths = self._calculate_lorentz_width(gamma_broadened, einstein_a)

            # Calculate the line intensities
            line_intensities = self._calculate_intensity(temperature, effective_wavenumbers, einstein_a,
                                                         energies_lower_state, g_upper=g_up, q_temp=q_temp)

            del gamma_broadened

        else:
            raise ValueError("Database not known. Use 'exomol' or 'hitran'.")

        print('Line parameter calculation time:', time.time() - t_start, 's', flush=True)

        sigma = np.zeros_like(self.wavenumber_grid)

        # Correct the intensities for cutoff and sub Lorentzian wing treatment
        line_intensity_corrections = self._intensity_correction(lorentz_widths, doppler_widths)

        line_intensities *= line_intensity_corrections
        del line_intensity_corrections

        # Decide which code to use
        range_effective_wavenumbers = effective_wavenumbers[-1] - effective_wavenumbers[0]

        whole_calculation_own = int(range_effective_wavenumbers * 200)

        cutoff_string = 'Amour'

        n_lines = len(effective_wavenumbers)

        if self.hartmann:
            cutoff_string = 'H'

        print(f'Starting the line profile calculation of {n_lines} lines', flush=True)

        # Calculate the opacity for the current transition file
        if n_lines < whole_calculation_own or self.force_molliere2015_method or n_lines == 1:
            phi_p = line_calculation_molliere2015.calc_sigma_coarse_interpol(effective_wavenumbers, lorentz_widths,
                                                                             doppler_widths, line_intensities,
                                                                             temperature, pressure, self.lambda_min,
                                                                             self.resolution, 10000,
                                                                             1 / self.wavenumber_grid[::-1], sigma,
                                                                             self.sub_grid_borders, cutoff_string,
                                                                             self.cutoff, self.verbose)

            sigma = sigma[::-1]

        else:

            if pressure * 1.01325 < 9e-7:
                warnings.warn("Pressure is lower than 1e-6 bar, the code was not tested for that case up to now. \n "
                              "Should work as well, but the sampling method of the lines can struggle for these "
                              "pressure. \n "
                              "To be safe, please boost the number of samples with sampling_boost of at least 10 for "
                              "every order of magnitude lower than 1e-6 bar.")

            important_lines_indices, minor_lines_indices, lines_per_bin, bin_indices = (
                self.__split_lines_by_intensity(effective_wavenumbers, line_intensities))

            effective_wavenumbers_important = np.asfortranarray(effective_wavenumbers[important_lines_indices])
            line_intensities_important = np.asfortranarray(line_intensities[important_lines_indices])
            lorentz_widths_important = np.asfortranarray(lorentz_widths[important_lines_indices])
            doppler_widths_important = np.asfortranarray(doppler_widths[important_lines_indices])

            # calculate the strong lines with own code
            town = time.time()

            if self.verbose:
                print('Calculating strong lines with Mollière et al. (2015) method', flush=True)

            phi_p = line_calculation_molliere2015.calc_sigma_coarse_interpol(effective_wavenumbers_important,
                                                                             lorentz_widths_important,
                                                                             doppler_widths_important,
                                                                             line_intensities_important,
                                                                             temperature, pressure, self.lambda_min,
                                                                             self.resolution, 10000.0,
                                                                             1 / self.wavenumber_grid[::-1],
                                                                             sigma, self.sub_grid_borders,
                                                                             cutoff_string, self.cutoff, self.verbose)
            print('Time strong lines:', time.time() - town, 's', flush=True)

            sigma = sigma[::-1]

            n_lines_minor = len(effective_wavenumbers[minor_lines_indices])
            n_packs = int(range_effective_wavenumbers)

            if n_packs == 0:
                n_packs = 1

            n_lines_per_pack = int(n_lines_minor / n_packs)
            n_lines_last_pack = n_lines_minor - n_lines_per_pack * n_packs

            if n_lines_per_pack == 0:
                warnings.warn("Number of lines to calculate with the sampling method is too low, please use "
                              "force_molliere2015_method = True. \n "
                              "That does not increase the calculation time for the present case but secures correct "
                              "calculations.")

            # Calculate the random numbers for the sampling
            del_therm_rd, del_press_rd, max_gam_rd, max_sig_rd = self.__do_rd_numbers()

            # Calculate the line density
            line_densities = self.__calculate_line_density(bin_indices, lines_per_bin)

            effective_wavenumbers_minor = np.asfortranarray(effective_wavenumbers[minor_lines_indices])
            line_intensities_minor = np.asfortranarray(line_intensities[minor_lines_indices])
            lorentz_widths_minor = np.asfortranarray(lorentz_widths[minor_lines_indices])
            doppler_widths_minor = np.asfortranarray(doppler_widths[minor_lines_indices])
            line_densities_minor = np.asfortranarray(line_densities[minor_lines_indices])

            del line_intensities, lorentz_widths, doppler_widths, line_densities

            tsam = time.time()

            if self.verbose:
                print('Calculating weak lines with sampling method', flush=True)

            (sigma_sampled, i_err) = sampling_lines.calc_all_linepacks(n_lines_minor,
                                                                       self.N_rd_numbers,
                                                                       self.grid_size, n_packs,
                                                                       n_lines_per_pack,
                                                                       n_lines_last_pack,
                                                                       self.resolution,
                                                                       self.wavenumber_grid,
                                                                       line_intensities_minor,
                                                                       lorentz_widths_minor,
                                                                       doppler_widths_minor,
                                                                       del_therm_rd, del_press_rd,
                                                                       max_gam_rd, max_sig_rd,
                                                                       effective_wavenumbers_minor,
                                                                       line_densities_minor,
                                                                       self.cutoff, sampling_boost, self.hartmann,
                                                                       coarse_grid_switch, self.verbose)

            if i_err == 1:
                raise RuntimeError("Wavenumber range of the last pack is too large for accurate results. \n "
                                   "Consider using force_molliere2015_method = True for the line profile calculations.")

            if i_err == 2:
                raise RuntimeError("Number of points for the linear grid is negative, probably the cutoff is too large "
                                   "for the sampling. \n Consider using the Mollière et al. (2015) method to calculate "
                                   "the lines by setting force_molliere2015_method = True.")

            if i_err == 3:
                raise RuntimeError("Number of points for the coarser linear grid is negative, probably the cutoff is "
                                   "too large. \n"
                                   "Consider using coarse_grid_switch = False, to disable the coarser grid, but that "
                                   "slows down the calculations a lot and is probably even worse. \n"
                                   "Consider using the Mollière et al. (2015) method to calculate the lines by setting "
                                   "force_molliere2015_method = True.")

            if i_err == 4:
                raise RuntimeError("Error in the search function for the interpolation from the linear grid to the "
                                   "logarithmic grid. Index j was not found.")

            print('Time for weak lines', time.time() - tsam, 's\n', flush=True)

            # add the strong lines to the sampled lines
            sigma += sigma_sampled

        print('Line profile calculation done', flush=True)

        return sigma

    def calculate_opacity(self, transition_files_list, use_mpi=True, n_cores=None, sampling_boost=1.0,
                          coarse_grid_switch=True, prt_format=False, doi=None, additional_information=None,
                          verbose=False):
        """
        Set up the calculation of the opacity for a given set of transition files. Read in the files and loop over the
        pressure temperature points in a separate function with multiprocessing to calculate the opacities. Save them
        in temporary files and combine them at the end to one file.

        Parameters:

        transition_files_list : list, optional
            A list of transition files to read in.
        use_mpi : bool, optional
            Whether to use MPI for parallelization.
        n_cores : int, optional
            The number of cores to use for parallelization.
        sampling_boost : float, optional
            The boost factor for the sampling.
        coarse_grid_switch : bool, optional
            Whether to use the coarse grid method.

        Returns:

        final_cross_section_file_name : str
            The name of the combined cross-section file.
        """
        self.verbose = verbose

        final_cross_section_file_name = self.run_transition_file_pressure_temperature_combination_parallel(
                                                                        transition_files_list,
                                                                        sampling_boost, coarse_grid_switch,
                                                                        use_mpi=use_mpi, n_cores=n_cores,
                                                                        prt_format=prt_format, doi=doi,
                                                                        additional_information=additional_information)

        return final_cross_section_file_name

    def __make_cross_section_files_for_line_list_files(self, transition_files_list):
        """
        Create temporary cross-section files for each line list file with a unique name

        Parameters:

        transition_files_list : list
            A list of transition files to create a cross-section file for.

        Returns:

        None
        """

        os.makedirs(".temporary_xsec", exist_ok=True)

        temporary_filenames = []

        for trans_file_name in transition_files_list:

            wavenumber_range = ''

            if self.database == 'exomol':

                wavenumber_range = trans_file_name.split('__')[-1].split('.trans')[0]

            else:
                basename = os.path.basename(trans_file_name)  # remove any path
                if basename.endswith(".par") or basename.endswith(".out"):
                    match = re.search(r'_([0-9]+-[0-9]+)_HITEMP', basename)
                    if match:
                        wavenumber_range = match.group(1)  # return only the wavenumber range for HITEMP files

                    else:
                        wavenumber_range = basename[:-4]  # remove .par or .out

            species = str(list(self.species_isotope_dict.keys())[0])
            species = self._collapse_isotope_name(species)
            filename = (f".temporary_xsec/temporary_xsec_{species}__{self.line_list}__"
                        f"{wavenumber_range}cm-1.zarr")

            temporary_filenames.append(filename)

            zarr_file = zarr.open(filename,
                                  mode='w',
                                  )

            try:
                # Zarr v3 style
                compressor = zarr.codecs.BloscCodec(cname='zstd', clevel=5,
                                                    shuffle=zarr.codecs.BloscShuffle.bitshuffle)
            except AttributeError:
                # Zarr v2 fallback
                compressor = zarr.Blosc(cname='zstd', clevel=5,
                                        shuffle=zarr.Blosc.BITSHUFFLE)

            zarr_file.create('xsec',
                             shape=(len(self.pressures), len(self.temperatures), len(self.wavenumber_grid)),
                             chunks=(1, 1, len(self.wavenumber_grid)),
                             compressors=compressor,
                             dtype='f8'
                             )

        return temporary_filenames

    @staticmethod
    def _save_cross_sections_temporary(filename, cross_section, pressure_index, temperature_index):
        """
        Save the cross-sections to a temporary zarr file.

        Parameters:

        filename : str
            The name of the temporary file to save the cross-section.
        cross_section : numpy.ndarray
            The cross-section array to be saved.
        pressure_index : int
            The index of the pressure in the cross-section array.
        temperature_index : int
            The index of the temperature in the cross-section array.

        Returns:

        None
        """

        f = zarr.open(filename, mode='r+')
        f['xsec'][pressure_index, temperature_index, :] = cross_section

        pass

    def _combine_wavenumber_regions_to_one_file(self, temporary_filenames=None):
        """
        Combine the temporary cross-section files into one file.

        Parameters:

        temporary_filenames : list, optional
            A list of temporary filenames to combine. If None, all files in the temporary_xsec folder will be used.

        Returns:

        opacity_filename : str
            The name of the combined cross-section file.
        """

        # Ignore zipfile UserWarnings about compression
        warnings.filterwarnings("ignore", category=UserWarning, module="zipfile")

        os.makedirs("cross-sections", exist_ok=True)

        if temporary_filenames is None:
            temporary_filenames = glob.glob(f".temporary_xsec/temporary_xsec_*cm-1*.zarr")

        if len(list(self.species_isotope_dict.keys())) == 1:
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name_file = str(isotope_name)
            opacity_filename = (f"cross-sections/cross-section_{species_name_file}__{self.line_list}__"
                                f"{self.wavenumber_grid[0]:.0f}-{self.wavenumber_grid[-1]:.0f}cm-1.zarr.zip")

        elif self.include_all_isotopes_in_filename:
            isotope_names = list(self.species_isotope_dict.keys())
            species_name_file = ''
            for iso in isotope_names:
                species_name_file += ('_' + str(iso))
            species_name_file = species_name_file[1:]  # remove leading underscore

            opacity_filename = (f"cross-sections/cross-section_{species_name_file}__{self.line_list}__"
                                f"{self.wavenumber_grid[0]:.0f}-{self.wavenumber_grid[-1]:.0f}cm-1.zarr.zip")

        else:
            print('Assuming natural abundance of isotopes, naming opacity file accordingly. If this is not desired, '
                  'please set include_all_isotopes_in_filename to True')
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name_file = str(isotope_name)
            opacity_filename = (f"cross-sections/cross-section_{species_name_file}-NatAbund__{self.line_list}__"
                                f"{self.wavenumber_grid[0]:.0f}-{self.wavenumber_grid[-1]:.0f}cm-1.zarr.zip")

        opacity_file = zarr.storage.ZipStore(opacity_filename, mode='w', compression=0)
        root = zarr.group(store=opacity_file)

        root.create('pressures', shape=(len(self.pressures),), dtype='f8')
        root.create('temperatures', shape=(len(self.temperatures),), dtype='f8')
        root.create('wavenumbers', shape=(len(self.wavenumber_grid),), dtype='f8')

        try:
            # Zarr v3 style
            compressor = zarr.codecs.BloscCodec(cname='zstd', clevel=5,
                                                shuffle=zarr.codecs.BloscShuffle.bitshuffle)
        except AttributeError:
            # Zarr v2 fallback
            compressor = zarr.Blosc(cname='zstd', clevel=5,
                                    shuffle=zarr.Blosc.BITSHUFFLE)
        root.create('cross-sections',
                    shape=(len(self.pressures), len(self.temperatures), len(self.wavenumber_grid)),
                    compressors=compressor,
                    dtype='f8')

        root.attrs["units"] = {"pressure": "bar", "temperature": "K", "wavenumber": "cm^-1",
                               "cross-sections": "cm^2/molecule"}

        root['pressures'][:] = self.pressures * 1.01325  # convert from atm to bar
        root['temperatures'][:] = self.temperatures
        root['wavenumbers'][:] = self.wavenumber_grid

        final_xsec = np.zeros((len(self.pressures), len(self.temperatures), len(self.wavenumber_grid)),
                              dtype=np.float64)

        for filename in temporary_filenames:
            temp_file = zarr.open(filename, mode='r')
            final_xsec += temp_file['xsec'][:]

        root['cross-sections'][:] = final_xsec

        opacity_file.close()

        shutil.rmtree(".temporary_xsec")

        return opacity_filename

    def __make_file_name_pressure_temperature_point(self, pressure, temperature) -> str:
        """
        Create a unique filename for the cross-section file at a given pressure and temperature point.

        Parameters:

        pressure : float
            The pressure in bar.
        temperature : float
            The temperature in K.

        Returns:

        filename : str
            The unique filename for the cross-section file.
        """

        if len(list(self.species_isotope_dict.keys())) == 1:
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name_file = str(isotope_name)
            filename = (f"temporary_xsec/temporary_xsec_{species_name_file}_{self.wavenumber_grid[0]:.0f}-"
                        f"{self.wavenumber_grid[-1]:.0f}cm-1_{pressure:.0e}bar_{temperature:.0f}K.zarr")

        elif self.include_all_isotopes_in_filename:
            isotope_names = list(self.species_isotope_dict.keys())
            species_name_file = ''
            for iso in isotope_names:
                species_name_file += ('_' + str(iso))
            species_name_file = species_name_file[1:]  # remove leading underscore

            filename = (f"temporary_xsec/temporary_xsec_{species_name_file}_{self.wavenumber_grid[0]:.0f}-"
                        f"{self.wavenumber_grid[-1]:.0f}cm-1_{pressure:.0e}bar_{temperature:.0f}K.zarr")

        else:
            print('Assuming natural abundance of isotopes, naming opacity file accordingly. If this is not desired, '
                  'please set include_all_isotopes_in_filename to True')
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name_file = str(isotope_name)
            filename = (f"temporary_xsec/temporary_xsec_{species_name_file}-NatAbund__{self.wavenumber_grid[0]:.0f}-"
                        f"{self.wavenumber_grid[-1]:.0f}cm-1_{pressure:.0e}bar_{temperature:.0f}K.zarr")

        return filename

    def make_individual_pressure_temperature_files(self, cross_sections_file_name):
        """
        Create individual petitRADTRANS-compatible cross-section files for each pressure-temperature point.

        Parameters:

        cross_sections_file_name : str
            The name of the cross-sections file that LINE-RACER created and where all cross-sections at all pressure-
            temperature points are stored.

        Returns:

        None
        """
        os.makedirs(".temporary_pRT_xsec", exist_ok=True)

        store = zarr.storage.ZipStore(cross_sections_file_name, mode='r')
        cross_sections = zarr.open_group(store=store, mode='r')

        pressures = cross_sections["pressures"][:]
        temperatures = cross_sections["temperatures"][:]
        wavenumbers = cross_sections["wavenumbers"][:]
        xsecs = cross_sections["cross-sections"][:, :, :]

        for id_p, pressure in enumerate(pressures):

            for id_t, temperature in enumerate(temperatures):

                cross_section = xsecs[id_p, id_t, :]

                species = str(list(self.species_isotope_dict.keys())[0])

                path = f".temporary_pRT_xsec/xsec_{species}_{pressure:.2e}bar_{temperature:.0f}K.zarr"

                # Create small Zarr file for this PT point
                pt_file = zarr.open(path, mode='w')

                pt_file.create('pressure',
                               shape=(1,),
                               dtype='f8',
                               )
                pt_file.create('temperature',
                               shape=(1,),
                               dtype='f8',
                               )
                pt_file.create('wavenumbers',
                               shape=(len(wavenumbers),),
                               dtype='f8',
                               )

                try:
                    # Zarr v3 style
                    compressor = zarr.codecs.BloscCodec(cname='zstd', clevel=5,
                                                        shuffle='bitshuffle')
                except AttributeError:
                    # Zarr v2 fallback
                    compressor = zarr.Blosc(cname='zstd', clevel=5,
                                            shuffle=zarr.Blosc.BITSHUFFLE)
                pt_file.create('cross-section',
                               shape=(len(wavenumbers),),
                               compressors=compressor,
                               dtype='f8'
                               )

                pt_file['pressure'][0] = pressure
                pt_file['temperature'][0] = temperature
                pt_file['wavenumbers'][:] = wavenumbers
                pt_file['cross-section'][:] = cross_section

        store.close()

        del cross_sections, pressures, temperatures, wavenumbers, xsecs

        pass

    @staticmethod
    def _collapse_isotope_name(name: str) -> str:
        """
        Collapse isotope names by removing isotope numbers and hyphens.

        Parameters:

        name : str
            The original isotope name.

        Returns:

        str
            The collapsed isotope name.
        """

        # Remove isotope numbers before element symbols
        name = re.sub(r'(\d+)([A-Z])', r'\2', name)

        # Remove hyphens
        name = name.replace('-', '')
        return name

    def convert_opacity_to_prt_format(self, final_cross_section_file_name, doi, rewrite=True,
                                      additional_information=None):
        """
        Convert the opacity file to petitRADTRANS format.

        Parameters:

        final_cross_section_file_name : str
            The name of the cross-sections file that LINE-RACER created and where all cross-sections at all pressure-
            temperature points are stored.
        doi : str
            The DOI to be included in the petitRADTRANS file.
        rewrite : bool, optional
            Whether to rewrite existing files.
        additional_information : str, optional
            Additional information to be included in the description.

        Returns:

        None
        """

        try:
            import petitRADTRANS
        except ImportError:
            raise ImportError("petitRADTRANS is not installed. Please install it to use this feature. You can do that "
                              "by installing line_racer with: pip install line_racer[full]")

        from petitRADTRANS.__file_conversion import format2petitradtrans

        natural_abundance = False

        if doi is None:
            warnings.warn("No DOI provided for petitRADTRANS format conversion. Please provide a DOI for proper "
                          "citation.")

        if len(list(self.species_isotope_dict.keys())) == 1:
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name = str(isotope_name)

        else:
            print('Assuming natural abundance of isotopes for writing to petitRADTRANS format. If this is not the case'
                  'please calculate the opacities of each isotope separately. Only relevant if used with pRT.')
            isotope_name = list(self.species_isotope_dict.keys())[0]
            species_name = (self._collapse_isotope_name(str(isotope_name)))
            natural_abundance = True

        self.make_individual_pressure_temperature_files(final_cross_section_file_name)

        prt_opacity_description = (f'Species: {list(self.species_isotope_dict.keys())[0]}, LR: '
                                   f'{importlib.metadata.version("line_racer")}, LineL: {self.line_list}, '
                                   f'Date of generation: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, '
                                   f'Broadening: {self.broadening_species_dict}, Type: {self.broadening_type}, '
                                   f'constant broadening: ({self.constant_broadening}), '
                                   f'Cutoff:{self.cutoff} 1/cm, Hartmann used: {self.hartmann}, '
                                   f'{additional_information}')

        def __line_racer_opacity_load_function(file,
                                               file_extension,
                                               molmass,
                                               wavelength_file,
                                               wavenumbers_petitradtrans_line_by_line,
                                               save_line_by_line,
                                               rebin,
                                               selection):

            zarr_file = zarr.open(file, mode='r')
            cross_sections = zarr_file['cross-section'][:]
            pressure = zarr_file['pressure'][0]
            temperature = zarr_file['temperature'][0]

            if save_line_by_line:

                if rebin:
                    target_wavenumbers = wavenumbers_petitradtrans_line_by_line[selection[0]:selection[1]]
                    cross_sections_line_by_line = np.interp(
                        target_wavenumbers,
                        self.wavenumber_grid,
                        cross_sections
                    )

                else:

                    cross_sections_line_by_line = np.interp(
                                                            wavenumbers_petitradtrans_line_by_line,
                                                            self.wavenumber_grid,
                                                            cross_sections
                                                            )

            else:
                cross_sections_line_by_line = None

            return cross_sections, cross_sections_line_by_line, self.wavenumber_grid, pressure, temperature

        format2petitradtrans(
            load_function=__line_racer_opacity_load_function,  # replace with your loading function's name
            opacities_directory='.temporary_pRT_xsec',  # replace with actual directory
            natural_abundance=natural_abundance,  # True or False
            source=self.line_list,  # replace with the source name, e.g. 'POKAZATEL'
            doi=doi,  # can be e.g. '' for personal usage
            species=species_name,  # species chemical formula, e.g. 'H2O'
            opacity_files_extension='*.zarr',  # extension of the opacity files
            save_correlated_k=True,  # if True, convert to c-k opacities
            save_line_by_line=True,  # if True, convert to lbl opacities
            # Information arguments
            charge='',  # for ions, charge of the species (e.g. '2+'), changes the output file name
            contributor=None,  # fill the 'contributor' attribute of the 'DOI' dataset
            description=prt_opacity_description,  # fill the 'description' attribute of the 'DOI' dataset
            rewrite=rewrite
        )

        # remove the temporary pressure temperature files
        shutil.rmtree('.temporary_pRT_xsec')
        print('Removed temporary folder .temporary_pRT_xsec with the individual p T point files.')

        pass

    @staticmethod
    def __check_for_data_directory():
        """
        Check if the data directory exists, if not download the necessary files.
        """

        files = {
            "correction_grid_cutoff.npz": "https://keeper.mpdl.mpg.de/f/a529f622ec2542309c43/?dl=1",
            "correction_grid_Hartmann_cutoff.npz": "https://keeper.mpdl.mpg.de/f/2fd9836ce57d4154be23/?dl=1",
            "molparam.txt": "https://keeper.mpdl.mpg.de/f/19ef3474fb894f42a6d3/?dl=1"
                }

        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        for filename, url in files.items():
            path = os.path.join(data_dir, filename)
            if not os.path.exists(path):
                warnings.warn(f"File {filename} not found. Downloading necessary file...")
                urllib.request.urlretrieve(url, path)
        pass

    def prepare_opacity_calculation(self, transition_files_list=None):
        """
        Prepare the opacity calculation by setting up the wavenumber grid, interpolating the intensity correction cube,
        and setting up the subgrid for the Mollière et al. 2015 method to calculate the line profiles.

        Parameters:

        transition_files_list : list, optional
            A list of transition files to read in. If None, the files will be searched in the input folder.

        Returns:

        transition_files_list : list
            A list of transition files to read in.
        """

        # check if the data directory is there, if not download it
        self.__check_for_data_directory()

        # Set up the grid
        self._prt_line_by_line_grid()

        # Set up the subgrid for the own code
        self.__subgrid_molliere2015_method()

        # interpolate the intensity correction cube to the right cutoff
        self.__interpolate_cutoff_correction_cube()

        # Calculate the opacity for a given pressure and temperature point
        if transition_files_list is None:

            if self.database == 'exomol':
                trans_files = glob.glob(os.path.join(self.input_folder, "*.trans"))

                if trans_files:
                    transition_files_list = glob.glob(os.path.join(self.input_folder, "*.trans"))
                else:
                    transition_files_list = glob.glob(os.path.join(self.input_folder, "*.trans.bz2"))

            elif self.database == 'hitran':
                transition_files_list = glob.glob(f'{self.input_folder}/*.out')

                if not transition_files_list:
                    transition_files_list = glob.glob(f'{self.input_folder}/*.par')

        if not transition_files_list:
            raise ValueError(f"No transition files found in the input folder. Input folder is {self.input_folder}. "
                             f"Either provide transition_files_list or check the input folder.")

        if not isinstance(transition_files_list, list):
            raise TypeError("transition_files_list must be of type list.")

        return transition_files_list

    @staticmethod
    def process_one_transition_file_pressure_temperature_combination(parameters):
        """
        Process one transition file for a given pressure and temperature combination. Safes the cross-section to a
        temporary file.

        Parameters:

        parameters : tuple
            A tuple containing the following parameters:

            f_id : int
                The file id.
            p_id : int
                The pressure id.
            t_id : int
                The temperature id.
            transition_file_name : str
                The name of the transition file.
            pressure : float
                The pressure in atm.
            temperature : float
                The temperature in K.
            self_ref : LineRacer object
                A reference to the LineRacer object.
            temporary_file_name : str
                The name of the temporary file to save the cross-section.
            sampling_boost : float
                The boost factor for the sampling.
            coarse_grid_switch : bool
                Whether to use the coarse grid method.

        Returns:

        None
        """

        (f_id, p_id, t_id, transition_file_name, pressure, temperature, self_ref, temporary_file_name,
         sampling_boost, coarse_grid_switch) = parameters

        if self_ref.database == 'exomol':
            state_energies, state_degeneracies, state_j = self_ref._read_exomol_states_file()

            effective_wavenumbers, einstein_a, g_up, j_upper, j_lower, energies_lower_state = (
                self_ref._read_exomol_transition_file(transition_file_name, state_energies, state_degeneracies,
                                                      state_j))

            iso_masses = global_iso_ids = line_intensities_t_ref = delta_ref = None

        elif self_ref.database == 'hitran':
            (effective_wavenumbers, line_intensities_t_ref, energies_lower_state, delta_ref, einstein_a, iso_masses,
             global_iso_ids) = self_ref._read_hitran_transition_files(transition_file_name)

            j_upper = j_lower = g_up = None

        else:
            raise ValueError("Database not known. Use 'exomol' or 'hitran'.")

        cross_section = self_ref._calculate_pressure_temperature_point(pressure, temperature,
                                                                       effective_wavenumbers, einstein_a, g_up,
                                                                       j_upper, j_lower, energies_lower_state,
                                                                       iso_masses, line_intensities_t_ref,
                                                                       delta_ref, global_iso_ids,
                                                                       sampling_boost, coarse_grid_switch)

        self_ref._save_cross_sections_temporary(temporary_file_name, cross_section, p_id, t_id)

    pass

    def run_transition_file_pressure_temperature_combination_parallel(self, transition_files_list,
                                                                      sampling_boost, coarse_grid_switch, use_mpi=True,
                                                                      n_cores=1, prt_format=False, doi=None,
                                                                      additional_information=None):
        """
        Run the opacity calculation for a given set of transition files in parallel using MPI or multiprocessing.

        Parameters:

        transition_files_list : list
            A list of transition files to read in.
        sampling_boost : float
            The boost factor for the sampling.
        coarse_grid_switch : bool
            Whether to use the coarse grid method.
        use_mpi : bool, optional
            Whether to use MPI for parallelization.
        n_cores : int, optional
            The number of cores to use for parallelization.
        prt_format : bool, optional
            Whether to convert the opacity file to petitRADTRANS format.
        doi : str, optional
            The DOI to be included in the petitRADTRANS file.
        additional_information : str, optional
            Additional information to be included in the description.

        Returns:

        opacity_filename : str
            The name of the combined cross-section file.
        """

        combinations = list(itertools.product(range(len(transition_files_list)),
                                              range(len(self.pressures)),
                                              range(len(self.temperatures))
                                              )
                            )

        time_start_total = time.time()

        if use_mpi:
            from mpi4py import MPI

            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            size = comm.Get_size()

            if rank == 0:

                # Create temporary cross-section files for each line list file
                temporary_filenames = self.__make_cross_section_files_for_line_list_files(transition_files_list)
            else:
                temporary_filenames = None

            comm.Barrier()

            temporary_filenames = comm.bcast(temporary_filenames, root=0)

            tasks = [(f_id, p_id, t_id,
                      transition_files_list[f_id],
                      self.pressures[p_id], self.temperatures[t_id], self,
                      temporary_filenames[f_id],
                      sampling_boost, coarse_grid_switch)
                     for f_id, p_id, t_id in combinations
                     ]

            for i, parameters in enumerate(tasks):
                if i % size == rank:
                    (f_id, p_id, t_id, transition_file_name, pressure, temperature, self_ref, temporary_file_name,
                     sampling_boost, coarse_grid_switch) = parameters
                    t_start = time.time()
                    print(f'Processing file {transition_file_name} (ID {f_id}) at {pressure * 1.01325}bar (ID {p_id})'
                          f' and {temperature}K (ID {t_id})...')
                    self.process_one_transition_file_pressure_temperature_combination(parameters)
                    print(f'Finished processing IDS {f_id, p_id, t_id} in {time.time() - t_start} s.')

            comm.Barrier()

            if rank == 0:

                opacity_filename = self._combine_wavenumber_regions_to_one_file(temporary_filenames=temporary_filenames)

                print('Total time for opacity calculation: ', time.time() - time_start_total, 's\n')

                if prt_format:
                    print('Converting to petitRADTRANS format...')

                    self.convert_opacity_to_prt_format(opacity_filename, doi, rewrite=True,
                                                       additional_information=additional_information)

                return opacity_filename

        elif n_cores == 187187:

            temporary_filenames = self.__make_cross_section_files_for_line_list_files(transition_files_list)

            if self.database == 'exomol':
                state_energies, state_degeneracies, state_j = self._read_exomol_states_file()

                effective_wavenumbers, einstein_a, g_up, j_upper, j_lower, energies_lower_state = (
                    self._read_exomol_transition_file(transition_files_list[0], state_energies, state_degeneracies,
                                                      state_j))

                iso_masses = global_iso_ids = line_intensities_t_ref = delta_ref = None

            elif self.database == 'hitran':
                (effective_wavenumbers, line_intensities_t_ref, energies_lower_state, delta_ref, einstein_a, iso_masses,
                 global_iso_ids) = self._read_hitran_transition_files(transition_files_list[0])

                j_upper = j_lower = g_up = None

            else:
                raise ValueError("Database not known. Use 'exomol' or 'hitran'.")

            cross_section = self._calculate_pressure_temperature_point(self.pressures[0], self.temperatures[0],
                                                                       effective_wavenumbers, einstein_a, g_up,
                                                                       j_upper, j_lower, energies_lower_state,
                                                                       iso_masses, line_intensities_t_ref,
                                                                       delta_ref, global_iso_ids,
                                                                       sampling_boost, coarse_grid_switch)

            self._save_cross_sections_temporary(temporary_filenames[0], cross_section, 0, 0)
            opacity_filename = self._combine_wavenumber_regions_to_one_file(temporary_filenames=temporary_filenames)

            return opacity_filename

        else:
            from multiprocessing import Pool

            # Create temporary cross-section files for each line list file
            temporary_filenames = self.__make_cross_section_files_for_line_list_files(transition_files_list)

            tasks = [(f_id, p_id, t_id,
                      transition_files_list[f_id],
                      self.pressures[p_id], self.temperatures[t_id], self,
                      temporary_filenames[f_id],
                      sampling_boost, coarse_grid_switch)
                     for f_id, p_id, t_id in combinations
                     ]

            with Pool(processes=n_cores) as pool:

                results = list(pool.map(self.process_one_transition_file_pressure_temperature_combination, tasks))

            opacity_filename = self._combine_wavenumber_regions_to_one_file(temporary_filenames=temporary_filenames)

            print('Total time for opacity calculation: ', time.time() - time_start_total, 's\n')

            if prt_format:
                print('Converting to petitRADTRANS format...')

                self.convert_opacity_to_prt_format(opacity_filename, doi, rewrite=True,
                                                   additional_information=additional_information)

            return opacity_filename

import numpy as np
import scipy.special as sp
import scipy.integrate as integrate


def analy_voigt(grid, gamma, sigma):
    """
    Calculate the Voigt profile using the Wofz function.

    Parameters:

    grid : array-like
        The grid of wavenumbers.
    gamma : float
        The line broadening parameter (gamma).
    sigma : float
        The Doppler width (sigma).

    Returns:

    sc_voigt : array-like
        The calculated Voigt profile.
    """

    sc_voigt = sp.voigt_profile(grid, gamma, sigma)

    return sc_voigt


def calculate_correction_grid(gamma_sigma_ratio_min, gamma_sigma_ratio_max, sigma_min, sigma_max, number_width_points,
                              cutoff_min, cutoff_max, number_cutoff_points, use_hartmann):
    """
    Calculate the Hartmann (Hartmann et al. 2002) and cutoff correction grid for the Voigt profile.

    Parameters:

    gamma_sigma_ratio_min : float
        Minimum value of gamma/sigma.
    gamma_sigma_ratio_max : float
        Maximum value of gamma/sigma.
    sigma_min : float
        Minimum value of sigma.
    sigma_max : float
        Maximum value of sigma.
    width_points : int
        Number of points in the gamma/sigma dimension.
    cutoff_min : float
        Minimum value of cutoff.
    cutoff_max : float
        Maximum value of cutoff.
    cutoff_points : int
        Number of points in the cutoff dimension.
    Hartmann : bool
        Whether to apply the Hartmann correction

    Returns:

    corr : numpy.ndarray
        The correction grid.
    sigma_arr : numpy.ndarray
        The array of sigma values.
    gamma_sigma_ratio_arr : numpy.ndarray
        The array of gamma/sigma values.
    cutoff_arr : numpy.ndarray
        The array of cutoff values.
    """

    g_s_ratio_max = np.log10(gamma_sigma_ratio_max)
    g_s_ratio_min = np.log10(gamma_sigma_ratio_min)
    s_max = np.log10(sigma_max)
    s_min = np.log10(sigma_min)
    c_max = np.log10(cutoff_max)
    c_min = np.log10(cutoff_min)

    # Create a grid for gamma/sigma and sigma values
    gamma_sigma_ratio_arr = np.logspace(g_s_ratio_min, g_s_ratio_max, number_width_points)[::-1]
    sigma_arr = np.logspace(s_min, s_max, number_width_points)

    # Create a grid for cutoff values
    cutoff_arr = np.logspace(c_min, c_max, number_cutoff_points)

    correction_arr = np.zeros((number_cutoff_points, number_width_points, number_width_points))

    # calculate the integral of the Voigt function for every combination of gamma/sigma and sigma values
    for k, cutoff in enumerate(cutoff_arr):
        if use_hartmann:
            add_hartmann = "and using Hartmann correction "
        else:
            add_hartmann = ""
        print(f"Calculating correction grid for cutoff {add_hartmann}{cutoff:.2f} cm^-1 ({k+1}/{len(cutoff_arr)})")

        for i, sigma in enumerate(sigma_arr):
            for j, g_s_ratio in enumerate(gamma_sigma_ratio_arr):

                gamma = g_s_ratio * sigma
                width = gamma + sigma
                n_points = 10000
                n_widths = 100

                nu_eff = cutoff

                left = nu_eff - n_widths * width
                left = max(left, 0)
                right = nu_eff + n_widths * width
                right = min(right, 2*cutoff)

                line_grid = np.linspace(left, right, n_points)
                hartmann_grid = np.ones_like(line_grid)

                delta_nu = line_grid - nu_eff

                # Apply Hartmann correction if specified
                if use_hartmann:

                    mask_60left = delta_nu < -60
                    mask_26left = (delta_nu >= -60) & (delta_nu < -26)
                    mask_26right = (delta_nu > 26) & (delta_nu <= 60)
                    mask_60right = delta_nu > 60

                    hartmann_grid[mask_60left] *= 0.0684 * np.exp(-abs(delta_nu[mask_60left]) / 393)
                    hartmann_grid[mask_26left] *= 8.72 * np.exp(-abs(delta_nu[mask_26left]) / 12)
                    hartmann_grid[mask_26right] *= 8.72 * np.exp(-abs(delta_nu[mask_26right]) / 12)
                    hartmann_grid[mask_60right] *= 0.0684 * np.exp(-abs(delta_nu[mask_60right]) / 393)

                voigt = analy_voigt(line_grid, gamma, sigma)
                voigt_integral = integrate.trapezoid(voigt * hartmann_grid, line_grid)
                correction_arr[k, i, j] = 1/voigt_integral

                # If the integral is greater than 0.9999, set the rest of the grid to 1.0
                if voigt_integral > 0.9999:
                    correction_arr[k, i, j + 1:] = 1.0
                    break

    gamma_sigma_ratio_arr = gamma_sigma_ratio_arr[::-1]
    correction_arr = correction_arr[:, :, ::-1]

    return correction_arr, sigma_arr, gamma_sigma_ratio_arr, cutoff_arr

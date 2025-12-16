=====================================================================
Physical and computational background of the line profile calculation
=====================================================================

In the following documentation, we will explain how the molecular and atomic lines look like and where they origin from. After that, we will explain how the line profiles are calculated in line racer.

Line shapes and broadening mechanisms
-------------------------------------

This section, is about the line profile and atomic and molecular state transitions.
The content is mostly taken from `Demtröder, 2016 <https://link.springer.com/book/10.1007/978-3-662-49094-5>`_, which however is written in German.
A more complete and detailed explanation in english can be found in the masters thesis chapter 2 of David, which can be found `here <https://keeper.mpdl.mpg.de/f/bf0488acf85e4d2a82b3/>`_.
For the whole description, we will use wavenumbers :math:`\nu` in units of :math:`\mathrm{cm}^{-1}`, which is common in spectroscopy.
Molecular and atomic spectral lines origin in the transitions between different energy levels of atoms or molecules.
The energy level can be associated with electronic states of atoms and molecules and vibrational or rotational states of molecule.
When an atom or molecule transitions from a higher energy level to a lower one, it emits a photon with an energy equal to the difference between the two levels.
Conversely, when it absorbs a photon with the right energy, it can transition from a lower energy level to a higher one.
Even though these transitions occur at specific energies (or wavenumbers/wavelengths), the observed spectral lines are not infinitely sharp.
Instead, they have a certain width and shape, which is described by the line profile or line shape function.
There are three mechanisms that contribute to the broadening of spectral lines: natural broadening, thermal broadening, and pressure (collisional) broadening.

Natural and collisional broadening
----------------------------------

Natural and collisional broadening are both described by a Lorentzian profile.
Natural broadening arises from the inherent uncertainty in the energy levels of atoms and molecules due to the finite lifetime of excited states, as described by the Heisenberg uncertainty principle.
From a semi-classical perspective this can be explained by a damped oscillator model, which has a spectral power density that follows a Lorentzian profile with a width determined by the lifetime of the state.
Collisional broadening, also known as pressure broadening, occurs when atoms or molecules collide with each other.
These collisions perturb the energy levels, therefore changing their lifetimes, leading to a broadening of the spectral lines also in the shape of a Lorentzian. The Lorentzian profile is given by:

.. math::

    \phi_\text{L}(\nu) = \frac{1}{\pi} \frac{\gamma}{\gamma^2 + (\nu - (\nu_0 + \delta_\text{p}P))^2}

where :math:`\nu` is the wavenumber, :math:`\nu_0` is the line center, :math:`delta_\text{p}` is the pressure shift coefficient, :math:`P` is the pressure and :math:`\gamma` is the broadening parameter of the line.
The broadening parameter :math:`\gamma` is given by:

.. math::
    \gamma = \gamma_\text{nat} + \gamma_\text{col} = \frac{1}{4\pi \tau} + P\sum_b \gamma_{b}p_b\left(\frac{T_\text{ref}}{T}\right)^{n_b}

where :math:`\gamma_\text{nat}` is the natural broadening parameter and :math:`\gamma_\text{col}` is the collisional broadening parameter, :math:`\tau = 1/A_{ij}` is the lifetime of the excited state with :math:`A_{ij}` being the Einstein coefficient, :math:`p_b` is the partial pressure of the broadening species :math:`b`, :math:`\gamma_b` is the collisional broadening coefficient for the broadening species :math:`b` at a reference temperature :math:`T_\text{ref}` and :math:`n_b` is the temperature exponent for the broadening species :math:`b`.
The different broadening parameters can be added, since the broadening mechanisms are independent of each other (the convolution of two Lorentzian with widths :math:`\gamma_a` and :math:`\gamma_b` is again a Lorentzian with width :math:`\gamma = \gamma_a + \gamma_b`).

Thermal broadening
------------------

Thermal broadening, also known as Doppler broadening, arises from the thermal motion of atoms and molecules. Due to their motion, the emitted or absorbed photons have a broader energy distribution which directly translates into a broader line profile. The thermal broadening is described by a Gaussian profile given by:

.. math::

    \phi_\text{D}(\nu) = \frac{1}{\sqrt{\pi}\gamma_D} \exp\left(-\left(\frac{\nu - \nu_0}{\gamma_D}\right)^2\right)

where :math:`\nu` is the wavenumber, :math:`\nu_0` is the line center and :math:`\gamma_D` is the Doppler width given by:

.. math::

    \gamma_D = \frac{\nu_0}{c} \sqrt{\frac{2k_\text{B}T}{m}}

where :math:`\nu_0` is the line center, :math:`k_\text{B}` is the Boltzmann constant, :math:`T` is the temperature, :math:`m` is the mass of the atom or molecule and :math:`c` is the speed of light.
Compared to the usual definition of the standard deviation :math:`\sigma_D` of a Gaussian distribution,
the introduced definition :math:`\gamma_D` relates as :math:`\gamma_D = \sqrt{2}\sigma_D`.

Voigt profile
-------------
Since the broadening mechanisms are independent of each other, the overall line profile is given by the convolution of the individual profiles.
The resulting profile is known as the Voigt profile, which can be seen in the following figure as the dashed line.

.. image:: images/voigtprofile_convolution.png
   :width: 500px

As a little side note, the Voigt profile is only an approximation of the real line profile, since other effects are neglected here.
However, the Voigt profile is widely used in astrophysics and atmospheric physics due to its simplicity and good accuracy for many applications, which is why it is also used in line racer.
Nevertheless, other line profiles exist, such as the `Hartmann-Tran Profile (HTP) <https://arxiv.org/abs/1409.7782>`_.



Cutoff and sub-Lorentzian treatment of the line wings
-----------------------------------------------------
Line racer provides two different options to account for the unphysicality of the far wings of the Voigt profile.
The first one is a simple cutoff of the wings, since it is unphysical for the wings to extend infinitely far.
However, it is an ongoing debate in the community about where to set the cutoff. There are studies like `Gharib-Nezhad et al. 2023 <https://doi.org/10.1093/rasti/rzad058>`_ which suggest that the cutoff should be set between 25 :math:`\mathrm{cm}^{-1}` and 100 :math:`\mathrm{cm}^{-1}` from the line center.
The general impact of a cutoff is illustrated on the following figure on the right side.

The second option is a sub-Lorentzian treatment of the wings, which reduces the absorption in the far wings compared to the Voigt profile.
This is done by multiplying the Lorentzian part of the Voigt profile with a factor that decreases with distance from the line center.
We implemented the `Hartmann et al. 2002 <https://www.sciencedirect.com/science/article/pii/S0022407301000589>`_ sub-Lorentzian treatment, which was originally measured for CH4 lines that were collisionally broadened by H2.
However, it is also used as an approximation for other molecules and broadening species in the absence of better data.
The general impact of the sub-Lorentzian treatment is illustrated on the following figure on the left side.

.. image:: images/hartmann_cutoff.png
   :width: 500px

In general, we suggest to use a cutoff not larger than 100 :math:`\mathrm{cm}^{-1}`, if no sub-Lorentzian treatment is used.
If a sub-Lorentzian treatment is used, a larger cutoff can be chosen, since the far wings are already reduced by the sub-Lorentzian treatment.
However, we suggest to still use a cutoff of 100 :math:`\mathrm{cm}^{-1}`.
Additionally, we recommend using the sub-Lorentzian treatment, since it is more physical than a simple cutoff.
If you have a different opinion about the cutoff or sub-Lorentzian treatment or if you recommend implementing a different sub-Lorentzian treatment, please feel free to contact us.
We are happy to discuss this topic.

Line calculation in line racer
------------------------------

Since the Voigt profile is a convolution, it is computationally expensive to calculate, especially, if the line lists contain billions of lines.
Therefore, the line profile calculation in line racer is split into two different methods depending on the size of the line list.
If the line list is small, which is here defined as less than 200 lines per 1 :math:`\mathrm{cm}^{-1}`, the `Mollière et al. 2015 <https://ui.adsabs.harvard.edu/abs/2015ApJ...813...47M/abstract>`_ method is used.
If the line list contains more lines, for every 1 :math:`\mathrm{cm}^{-1}` interval, the 200 strongest lines are calculated with the Mollière et al. 2015 method is used.
The remaining "weak" lines are calculated using a sampling technique of the line profile, which was proposed by `M. Min 2017 <https://ui.adsabs.harvard.edu/abs/2017A%26A...607A...9M/abstract>`_, and further improved by us.
It is also shown graphically in the following figure.

.. image:: images/line_profile_calculation_line_racer.png
   :width: 500px

Mollière et al. 2015 method
---------------------------

The first method is adapted from `Mollière et al. 2015 <https://ui.adsabs.harvard.edu/abs/2015ApJ...813...47M/abstract>`_ and uses the `Humlícek, 1982 <https://www.sciencedirect.com/science/article/pii/0022407382900784?via%3Dihub>`_ algorithm to calculate the line profiles.
However, since the Humlícek algorithm is computationally expensive, Mollière et al. 2015 introduced a speedup for the far wings of the lines.
It calculates the line cores on the full resolution of the grid and uses a coarser grid for the wings of the lines and then interpolates it back to the full grid.
The whole grid is divided into sub grids. More specifically, if a subgrid :math:`n \neq m` is located far away from sub grid :math:`m`, the line profile is only calculated on the coarse grid of :math:`m` and then interpolated back to the full grid.
This speedup is illustrated in the following figure, which is taken from Mollière et al. 2015.
The black crosses indicate the calculation of the line profile on the full resolution in sub grid :math:`m`, while the red crosses indicate the calculation on the coarse grid and then interpolated back to the full grid.
A further explanation can be found in the paper, including the criteria when to switch to the coarse grid calculation.

.. image:: images/wing_speedup_molliere2015.png
   :width: 500px

Sampling technique
------------------

The sampling technique is based on `M. Min 2017 <https://ui.adsabs.harvard.edu/abs/2017A%26A...607A...9M/abstract>`_.
It has the huge advantage, that the lines are not calculated on every grid point, but are rather sampled randomly according to the line profile and the desired precision.
This means, that lines that are very weak and only contributing to the background can be sampled with a low number of samples and therefore a lower precision but high speed.
On the other hand, strong lines can be sampled with a high number of samples and therefore a higher precision.
This leads to a huge speedup in the line profile calculation, especially for large line lists with many weak lines.
To sample the lines, a Gaussian and a Lorentzian sample are drawn and added. They represent the thermal and collisional/natural broadening, respectively and are scaled accordingly.
Adding two random numbers drawn from different distributions is equivalent to drawing a random number from the convolution of the two distributions, which is the Voigt profile in our case.
Therefore, to obtain the Voigt profile, the sum of the samples is added to the center location of the line :math:`\nu_0` and in the wavenumber bin, that contains the sampled value, a weight is added.
In the simplest case, one can just add 1 and normalize the profile afterward.
However, you could also directly use 1/N, with N being the number of samples, to obtain a normalized profile directly, assuming bin widths of 1.
An illustration of this procedure is shown in the following figure.
The green cross represents the line center, while the blue function is a Gaussian profile and the orange function is a Lorentzian profile.
The orange arrow indicates a drawn Lorentzian sample, while the blue arrow indicates a drawn Gaussian sample.
To better visualize the convolution, the dashed grey line shows that the Lorentzian sample is shifted to the drawn Gaussian sample.
In the bin that contains the sampled Voigt value, a weight is added, as indicated by the black box.
This would be a line sampled with one sample, assuming bin widths of 15 :math:`\mathrm{cm}^{-1}`.

.. image:: images/simple_sampling.png
   :width: 500px

However, taking only one sample per line is not sufficient to obtain a good approximation of the Voigt profile for more important lines.
Nevertheless, the background opacity can be constrained with that very well. To sample lines more accurate, more samples can be drawn.
With more and more samples, the profile converges to the real Voigt profile.
An illustration of that is shown in the following gif, where the number of samples is increasing from 1 to 1 000 000.

.. image:: images/Slow_sampling_animation.gif
   :width: 500px

This method is already quite strong, however it takes a lot of samples to sample the line accurately, especially on high resolution grids.
Therefore, `M. Min 2017 <https://ui.adsabs.harvard.edu/abs/2017A%26A...607A...9M/abstract>`_ proposed a speedup technique, which you can read up in his paper or in my thesis.
It basically makes more use of one sample by not just adding the weight in the bin that contains the sampled value, but spreads out a weight :math:`w` in an interval defined from the line center plus the Gaussian :math:`\Delta\nu_\mathrm{therm}` and then plus and minus the Lorentzian sample :math:`\Delta\nu_\mathrm{press}`.
By that, more information is obtained from one sample and therefore less samples are needed to obtain a good approximation of the Voigt profile.
The following gif shows the increasing number of samples for the improved sampling technique compared to the slow one shown before.

.. image:: images/Fast_sampling_animation.gif
   :width: 500px

To achieve even higher speeds, we further improved this method. For the speed up technique `M. Min 2017 <https://ui.adsabs.harvard.edu/abs/2017A%26A...607A...9M/abstract>`_ proposed, the profiles have to be normalized after the sampling.
We came up with a way of sampling them already normalized, which speeds up the calculation even more.
The significant difference to the previous method is that instead of adding :math:`w = \frac{\Delta\nu_\mathrm{press}^2}{\Delta\nu_\mathrm{press}^2 + \gamma^2}` to all bins in the sampled interval, we are adding the following:

.. math::

    w = \frac{\Delta\nu_\mathrm{press}^2}{\Delta\nu_\mathrm{press}^2 + \gamma^2} \frac{S}{N_\mathrm{samples}} \frac{R}{\nu_\mathrm{eff}}

where :math:`N_\mathrm{samples}` is the number of samples, :math:`\Delta\nu_\mathrm{press}` is the pressure broadening scaled Lorentzian sample, :math:`\gamma` is the Lorentzian width, :math:`S` is the line strength, :math:`\nu_\mathrm{eff}` and :math:`R` is the resolution of the grid.
The first part accounts for spreading the weight according to the Lorentzian sample, the second part normalizes the profile according to the number of samples and the line strength and the last part accounts for the grid bin width. For a logarithmic grid, it has the stated shape.
More details about the derivation, further explanations and detailed comparisons can be found in the master's thesis of David, which can be found `here <https://keeper.mpdl.mpg.de/f/bf0488acf85e4d2a82b3/>`_.

Moreover, to get the best possible performance, we also adapted a method from `de Regt et al. 2025 <https://ui.adsabs.harvard.edu/abs/2025arXiv251020870D/abstract>`_, which uses a grid resolution that adapts to the width of the lines.
By that, no information is lost, but also no unnecessary high resolution is used for broad lines.
This is used for the grid, on which the lines are sampled and is then interpolated back to the original grid.






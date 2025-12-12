==========================
Downloading line list data
==========================

There are currently three main databases of molecular line lists that are supported by line racer: `HITRAN <https://hitran.org/>`_, `HITEMP <https://hitran.org/hitemp/>`_ and `Exomol <https://www.exomol.com/>`_.
The following notes will explain how to download line lists from these databases for opacity calculations with line racer.
The first step is to create a folder in which you will store all the required data.
If you want to calculate H2O opacities e.g. your folder structure could look like: `line_list/H2O/`

.. Note:: In general the data can be downloaded by using `wget <https://www.gnu.org/software/wget/>`_ which e.g. can be downloaded using ``homebrew``, as explained in the `installation guide <installation.rst>`_. In the right subfolder you can then downloaded the files via ``wget https://www.your_link_here.com``.

ExoMol
~~~~~~

Go to the `ExoMol website <https://www.exomol.com/>`_ and navigate to the `Data <https://www.exomol.com/data/>`_ tab and then to `Molecules <https://www.exomol.com/data/molecules/>`_.
Here you can see an overview of all the available molecules within ExoMol.
Click on the molecule you are interested in to go to its data page.
On this page (for example `H2O <https://www.exomol.com/data/molecules/H2O/>`_) you will find a list of available isotopes for the molecule.

Additionally, there are broadening files (`.broad`). ExoMol uses quantum number dependent line broadening parameters, a more detailed explanation can be found in `Barton et al. (2017) <https://doi.org/10.1016/j.jqsrt.2017.01.028>`_ and in `Tennyson et al. (2024) <https://doi.org/10.1016/j.jqsrt.2024.109083>`_.
The broadening files are provided for (multiple) species, which is denoted by the suffix in the file name (for example `1H2-16O__H2.broad` for H2 broadening).
Sometimes, the broadening diet (more about that can be found in the upper mentioned literature) is also indicated in the file name (e.g. `1H2-16O__air_a0.broad` for the a0 diet).
Currently, line racer supports the a0 and m0 diet, but it is planed to include more.

Another feature planned to include in the future is the use of pressure shift parameters from ExoMol, which are also provided on this website (e.g. `1H2-16O__a0.shift`).
However, currently there are not many molecules with available pressure shift files.
If you want to use one (or multiple) of the broadening species, download the files and put them into your line list folder structure (e.g. `line_list/H2O/`).
If you do not use a broadening file, you can later choose different broadening routines within line racer (e.g. constant broadening or broadening using the approximaion from `Sharp and Burrows, 2007 <https://ui.adsabs.harvard.edu/abs/2007ApJS..168..140S/abstract>`_)


In the isotope list, click on the isotope you are interested in (for example `1H2-16O <https://www.exomol.com/data/molecules/H2O/1H2-16O/>`_) to go to its page.
Here you will find a list of available line lists for this isotope. Click on the line list you are interested in (for example `POKAZATEL <https://www.exomol.com/data/molecules/H2O/1H2-16O/POKAZATEL/>`_) to go to its page.
Best practice is to follow the ExoMol recommendation and use the line list that is marked in green.

On the line list page, you will first find the metadata, where one file is the `.def` file (e.g. `1H2-16O__POKAZATEL.def <https://www.exomol.com/data/molecules/H2O/1H2-16O/POKAZATEL/?export=def>`_).
This file includes all of the relevant information about the line list, like the number of lines, the temperature range, the isotope mass and the version number (in YYYYMMDD format).
Additionally, as the most important part, it contains the parameters ``Default value of Lorentzian half-width for all lines (in cm-1/bar)`` and ``Default value of temperature exponent for all lines``, which are needed for the line broadening calculations if no broadening species is chosen.

Below the ``spectrum overview`` you can find the download links for the line list files. The first file, is the `.states` file (e.g. `1H2-16O__POKAZATEL.states.bz2 <https://www.exomol.com/db/H2O/1H2-16O/POKAZATEL/1H2-16O__POKAZATEL.states.bz2>`_), which contains all the energy levels and their properties.
This is required to download in any case. Below that are the `.trans` files, which contain the actual transition data. Depending on the line list, there can be multiple `.trans` files, which are split in frequency ranges to make downloading easier.
Download the files of the wavenumber range of your interest (or just all of them) to your line list folder structure.

.. Note:: The `.states` and `.trans` files are usually `bz2` compressed. However, this is fine, and line racer is able to read these compressed files directly without the need to decompress them first (but also the decompressed).

Since there are often many `.trans` files, it is recommended to use a script to download them all at once.
An example ``bash`` script using ``wget`` to download all the `.trans` files for the POKAZATEL line list of H2O is provided below:

.. code-block:: bash

    #!/bin/bash

    # Adjust the base URL
    BASE_URL="https://www.exomol.com/db/H2O/1H2-16O/POKAZATEL/"

    # Adjust range as needed; e.g., for 0 to 41200 in steps of 100
    for ((i=0; i<=41200; i+=100)); do
        START=$(printf "%05d" $i)
        END=$(printf "%05d" $((i + 100)))
        FILENAME="1H2-16O__POKAZATEL__${START}-${END}.trans.bz2"
        URL="${BASE_URL}/${FILENAME}"

        echo "Downloading ${FILENAME}"
        wget --continue "${URL}" || break  # Stop if a file does not exist
    done

The line calculation is much faster for decompressed files, so if you have enough disk space available it is recommended to decompress the `.trans` files after downloading them. For many files, you can use the following script to decompress all `.bz2` files:

.. code-block:: bash
    #!/bin/bash
    #SBATCH --job-name=unzip_H2O
    #SBATCH --output=logs/line_racer/unzip_CH4.out
    #SBATCH --error=logs/line_racer/unzip_CH4.err
    #SBATCH --time=100:00:00
    #SBATCH --mem=80G
    #SBATCH --cpus-per-task=1

    cd line_list/H2O/

    echo "Starting decompression..."
    bunzip2 *.bz2
    echo "Done!"

Or simply run in your terminal:
.. code-block:: bash
    cd line_list/H2O/
    bunzip2 *.bz2

After the transition files, the last important data is the partition function, which can be found as the `.pf` file (e.g. `1H2-16O__POKAZATEL.pf <https://www.exomol.com/db/H2O/1H2-16O/POKAZATEL/1H2-16O__POKAZATEL.pf>`_).
This file contains the partition function values at different temperatures, which are needed for the opacity calculations and should be downloaded to the line list folder structure as well.


HITRAN
~~~~~~

Go to the `HITRAN website <https://hitran.org/>`_ and navigate to the `Line-by-Line Search <https://hitran.org/lbl/>`_ over the Data Access tab. Here you can select the molecule you are interested in from the molecule list (e.g. CO2).
Then you can select the isotopologue(s) you want to download data for. Do not worry too much about that, since you can later choose which isotopologues to use within line racer.
After that you can select the desired frequency range, however, it is recommended to download the full range, since the hitran line list files are not that big.
For the next step you need to be logged in to download the data. If you do not have an account yet, you can create one for free `here <https://hitran.org/register/>`_.
After login, you can download the data. The standard format is the `.par` format, which is also supported by line racer. It contains all the important information needed for the opacity calculations, including broadening parameters for `air` and `self` broadening.

However, if you need other broadening species, you can select ``Create New Output Format``. In the new window, select an ``Output Format Name`` and choose ``[comma]`` as a ``Field separator``, ``Windows (CR LF)`` as ``Line endings`` and select the ``Output header line``.
Then, on the bottom right, select the desired parameters in ``Available Parameters``, but it is recommended and most easy to just select all parameters. After doing that, please safe this output format.
If you choose to use the newly created output format then please make sure to select it on the ``4. Select or Create Output Format`` step on the left side under ``Available Output Formats``.

The line data can now be prepared by clicking on ``Start Data Search``.
It might take a while, but you will be directed to a new page, where you can download the `Output transition data`, as well as look into the ``List of sources`` to cite the data properly. Additionally, you can check your output format again, by looking into the `readme.txt` file.
Please add the transition data file to your line data file (e.g. `line_list/CO2/`).

Similar to ExoMol, you also need the partition function for HITRAN data. It can be found under the HITRAN Documentation tab under `Isotopologue Metadata <https://hitran.org/docs/iso-meta/>`_.
The partition function files are named after the HITRAN internal `global ID` as `q*globalid*.txt` (e.g. `q7.txt` for the 12C-16O2 isotopologue of CO2).
Please download all of the partition function files for the isotopologues you selected before and add them to your line list folder structure.


HITEMP
~~~~~~
The HITEMP database is an extension of the HITRAN database for high temperature applications. It can be found on the HITRAN website under Data Access choosing `HITEMP <https://hitran.org/hitemp/>`_.
The line list data can be downloaded by clicking on the ``Download`` feature of the HITEMP data table of the molecule you are interested in (e.g. for `CH4 <https://hitran.org/files/HITEMP/bzip2format/06_HITEMP2020.par.bz2>`_).
For some molecules, there are multiple files, please download all of the relevant files for you. HITEMP line lists automatically contain all the available isotopologues for the molecule and you can later choose which isotopologues to use within line racer.

.. important:: For HITEMP line lists, please decompress (or unzip) them before adding them to your line list folder structure (e.g. `line_list/CH4/`).

Similar to HITRAN, you also need the partition function for HITEMP data. It can be found under the HITRAN Documentation tab under `Isotopologue Metadata <https://hitran.org/docs/iso-meta/>`_.
The partition function files are named after the HITRAN internal ``globalID`` as `q*globalid*.txt` (e.g. `q32.txt` for the 12C-1H4 isotopologue of CH4).
Please download all of the partition function files for the isotopologues you want to use and add them to your line list folder structure.



After downloading all the required data, you are ready to use line racer for opacity calculations!

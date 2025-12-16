==================================
How to use line racer on a cluster
==================================

In this guide, we will walk you through the steps to set up and run line racer on a cluster. It is built to be able to multiprocess every pressure-temperature case in addition to the line list files.
Before starting the calculation, we have to make sure, that everything is set up correctly.

1. **Install line racer**: Make sure that line racer is installed on your cluster. You can follow the installation instructions provided in the `installation guide <installation.html>`_.
2. **Set up environment**: Load the necessary modules and activate your Python environment where line racer is installed. This may involve loading specific compiler or MPI modules depending on your cluster's configuration.
3. **Prepare input files**: Ensure that you have all the required input files, including line lists, available on the cluster. You may need to transfer these files from your local machine to the cluster using tools like `scp` or `rsync`. You can also download them directly on the cluster as shown in the `downloading line list tutorial <downloading_line_list_data.html>`_. For the following example, you can follow the instructions in the `line racer tutorial of ExoMol line lists <notebooks/line_racer_notebook_example.html>`_ to prepare the H2O POKAZATEL line list from ExoMol.

.. Note:: It is always helpful to check your calculation setup for a minimal example, like one pressure-temperature point for one file. This can help to identify potential issues before running larger calculations.

To start the calculation, we need a Python script that sets up and runs the line racer calculation and a job script to submit the calculation to the cluster's job scheduler.
We start with the Python script. Since this tutorial is meant be about the cluster calculation, we wont explain the line racer setup in detail here. For that, please check out the `line racer tutorial <notebooks/line_racer_notebook_example.html>`_.

.. code-block:: python

    import numpy as np
    import line_racer.line_racer as lr

    pressures, temperatures = lr.LineRacer.prt_pressure_temperature_grid()

    H2O_racer = lr.LineRacer(resolution=1e6,
                             cutoff=100.0,  # in 1/cm
                             lambda_min=1.1e-5,  # in cm
                             lambda_max=2.5e-2,  # in cm
                             grid_type='log',
                             hartmann=True,
                             database='exomol',
                             input_folder='line_list/H2O/',  # path to folder with input files
                             temperatures=temperatures,  # in K
                             pressures=pressures,  # in bar
                             mass=18.010565, # in amu
                             species_isotope_dict={'1H2-16O': 1.0},
                             line_list_name='POKAZATEL',
                             broadening_species_dict={'H2': 0.85, 'He': 0.15},
                             broadening_type='exomol_table',  # could also be 'sharp_burrows', 'hitran_table' or 'constant'

                             # constant_broadening=[0.07, 0.5],  # if you want to use the default ExoMol broadening parameters, set this and change broadening_type to 'constant'

                             # Change the following only if you know what you do!
                             force_molliere2015_method=False  # whether to force using Mollière et al. (2015) for line profile calculation, recommended only if warning appears or for small line lists
                             )

    # prepare_opacity_calculation searches for all transition files in the input folder and prepares them for the calculation
    transition_files_list = H2O_racer.prepare_opacity_calculation()

    final_cross_section_file_name = H2O_racer.calculate_opacity(transition_files_list, use_mpi=True, prt_format=False)


The most important thing is to set ``use_mpi=True`` in the ``calculate_opacity`` function to enable MPI parallelization.

To submit this script to the cluster, we need a job script. Below is an example SLURM job script:

.. code-block:: bash

    #!/bin/bash -l
    #SBATCH --job-name=H2O_opacity
    #SBATCH --output=logs/line_racer/racer_H2O_POKAZATEL_%j.out
    #SBATCH --error=logs/line_racer/racer_H2O_POKAZATEL_%j.err

    #SBATCH --mem=80G
    #SBATCH --time=100:00:00
    #SBATCH --nodes=4
    #SBATCH --ntasks-per-node=25
    #SBATCH --cpus-per-task=1

    module purge

    module load openmpi-gcc/5.0.3
    module load miniforge/25.3

    # activate your environment, here conda is used as an example
    conda activate conda_env_py311

    # Run your script with the file
    mpirun python calculate_H2O_pokazatel.py

This script assumes, that out python code is saved in a file called ``calculate_H2O_pokazatel.py``. We request 4 nodes with 25 tasks each, leading to a total of 100 MPI processes. Adjust the memory, time, nodes, and tasks according to your cluster's policies and your calculation needs.
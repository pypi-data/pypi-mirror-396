User Installation
=================

PlayMolecule® is a virtual environment for drug discovery where simulations, AI and data are
integrated to uncover new insights. For commercial use, a product licence is required.
`Contact us <https://www.acellera.com/contact-us>`_ to book a demo and obtain a product quote tailored to your needs.

First install MambaForge (conda will work too but MambaForge is much faster at solving dependencies).
If you decide to use conda replace all ``mamba`` references with ``conda``

.. code-block:: bash

    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
    bash Mambaforge-$(uname)-$(uname -m).sh

Create a new mamba/conda environmenht

.. code-block:: bash

    mamba create -n playmolecule
    mamba activate playmolecule
    mamba install python=3.10 ipython -c conda-forge

You can then pip install the PlayMolecule with

.. code-block:: bash

    pip install playmolecule

Then add the following to your ``.bashrc`` file with the path provided by your administrator

.. code-block:: bash

    export PM_APP_ROOT=/path/provided/by/administrator

Admin Installation
==================

Acellera will provide you with a license file for the applications and a Google service account JSON file.
The administrator has to perform a few extra steps to complete the PlayMolecule installation for the users.

1. Install the license file or license server
2. Install Apptainer (previously known as Singularity)
3. Install the applications over Google Cloud

License Installation
--------------------

If you are intending to run the applications on more than a single machine you will need to setup a license server. 
For more information on how to set up a license server (Floating license) please see 
https://software.acellera.com/acemd/licence.html#licence-server

Otherwise just place the license file on a location where all users can access it on the single machine.

Apptainer Installation
----------------------

PlayMolecule applications are packaged as Apptainer containers. 
Therefore all users need to have Apptainer installed on their machines.
Specifically we require the following packages to be installed:

- apptainer
- apptainer-setuid
- cryptsetup

The last package is required for decrypting the containers at runtime.
You can find the official installation instructions here: https://apptainer.org/docs/admin/main/installation.html#install-rpm-from-epel-or-fedora
To verify that the installation was successful you can run the following command:

.. code-block:: bash

    dpkg -l | grep 'apptainer\|cryptsetup' # For Debian/Ubuntu
    rpm -qa | grep 'apptainer\|cryptsetup' # For EPEL/Fedora

which should return the three above installed packages.


Application Installation
------------------------

To install the applications for the users you need to follow these steps:

1. Install Google Cloud CLI to authenticate with Google Cloud where the app images are stored. Installation instructions can be found here: https://cloud.google.com/sdk/docs/install
2. On the ``gcloud init`` step of the above instructions authenticate with any account you wish.

Install the following pip packages in addition to ``playmolecule`` which are needed for the admin installation.

.. code-block:: bash
    
    pip install playmolecule questionary google-cloud-storage==1.35.0 tqdm

Choose a path where PlayMolecule will be installed. If you are running the applications in a cluster like SLURM
choose a path which is accessible from all machines (i.e. on a shared file system).
Otherwise choose a path on your local machine which is accessible to all users on that machine.
Set up the path in your ``.bashrc`` file as follows:

.. code-block:: bash

    export PM_APP_ROOT=/path/provided/by/administrator

To create the PlayMolecule installation open an ipython console and type the following:

.. code-block:: python

    from playmolecule import update_apps

This will start an interactive installation of PlayMolecule to guide you through setting up everything. At some step
it will ask you for the service account JSON file which Acellera has provided you with for downloading the applications.

Later if you want to update the applications again to their latest versions you can run the following commands:

.. code-block:: python

    from playmolecule import update_apps
    update_apps()
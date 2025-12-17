Tutorial
========

This tutorial will help you understand how the PlayMolecule API can be used.
First open an IPython or Python console and run the following:

.. code-block:: python

    from playmolecule import describe_apps

    describe_apps()

This will print you a description of all available PlayMolecule applications.
To use an app, for example ProteinPrepare in this case you can do:

.. code-block:: python

    from playmolecule.apps import proteinprepare

    # See help for the function by running `proteinprepare?` in IPython
    ed = proteinprepare(outdir="test", pdbid="3ptb")

The following will create a folder called test with all the necessary files to execute this job.
All app functions will create a folder and return to you an `ExecutableDirectory <playmolecule.apps.html#playmolecule.apps.ExecutableDirectory>`_ object. 
This is a self-contained directory including all app input files which can be executed either locally or on a cluster.
If it's not executed locally make sure the directory can be accessed from all machines 
in the cluster (i.e. is located on a shared filesystem).

To execute the job locally you can do:

.. code-block:: python

    ed.run()

    # Or in shorter format you can directly execute the app like this:
    proteinprepare(outdir="test", pdbid="3ptb").run()

This will execute the executable directory locally.
Next let's see a more complex example involving SLURM and a specific version of the app (here v1).

.. code-block:: python

    from playmolecule.apps import proteinprepare

    ed = proteinprepare.v1(outdir="test", pdbid="3ptb")
    ed.slurm(partition="normalCPU", ncpu=1, ngpu=0)

This will execute the directory ``test`` on a SLURM cluster on partition ``normalCPU`` and will request 1 CPU and 0 GPUs for the job.

When running on SLURM (or when running locally once the job has completed) you can check the status of the job via:

.. code-block:: python

    print(ed.status)

which will be one of ``WAITING_INFO`` (has not started yet), ``RUNNING``, ``COMPLETED`` or ``ERROR``. 
See `JobStatus <playmolecule.apps.html#playmolecule.apps.JobStatus>`_ class.

All apps have a test suite included in them which you can check by running:

.. code-block:: python

    from playmolecule.apps import proteinprepare

    print(proteinprepare.tests)  # This will print all available tests
    proteinprepare.tests.simple.run()  # This will execute the test `simple` locally

Using artifacts and files
-------------------------

Artifacts or files are artifacts which are shipped together with an application and can be used by it.
This includes files necessary to run an app (like model files for Kdeep) or files used for the app tests.
They are mostly synonymous except that they provide different ways for accessing the files.

Here you see how to use artifacts in an app execution

.. code-block:: python

    # Show all Kdeep latest artifacts
    print(kdeep.artifacts)

    # Show Kdeep artifacts for app version v1
    print(kdeep.v1.artifacts)

    # Use a dataset in an execution
    kdeep(
        outdir="/tmp/test2", 
        scratchdir="/tmp/", 
        modelfile=kdeep.artifacts.AceBind2023_ET, 
        pdb="./tests/test_playmolecule/kdeep/10gs_protein.pdb", 
        sdf="./tests/test_playmolecule/kdeep/10gs_ligand.sdf", 
        correlation_field="EXP_AFF"
    ).run()

Not only apps can offer artifacts. PlayMolecule also offers some global artifacts which can be used from any app

.. code-block:: python

    from playmolecule import artifacts

    print(artifacts)
def submit_slurm(dirname, runsh, execution_resources, **kwargs):
    from jobqueues.slurmqueue import SlurmQueue

    sl = SlurmQueue()
    sl.runscript = runsh

    if execution_resources is not None:
        # Set app defaults
        for arg in execution_resources:
            setattr(sl, arg, execution_resources[arg])

    # Set user-specified arguments
    for arg in kwargs:
        setattr(sl, arg, kwargs[arg])

    sl.submit(dirname)
    return sl


def get_slurm_status(slurmq):
    from jobqueues.simqueue import QueueJobStatus
    from playmolecule.apps import JobStatus

    mapping = {
        QueueJobStatus.RUNNING: JobStatus.RUNNING,
        QueueJobStatus.FAILED: JobStatus.ERROR,
        QueueJobStatus.CANCELLED: JobStatus.ERROR,
        QueueJobStatus.OUT_OF_MEMORY: JobStatus.ERROR,
        QueueJobStatus.TIMEOUT: JobStatus.ERROR,
        QueueJobStatus.COMPLETED: JobStatus.COMPLETED,
        QueueJobStatus.PENDING: JobStatus.WAITING_INFO,
        None: JobStatus.WAITING_INFO,
    }
    info = slurmq.jobInfo()
    if info is None:
        return JobStatus.WAITING_INFO
    return mapping[info[list(info.keys())[0]]["state"]]


def slurm_mps(exec_dirs, **kwargs):
    """Submit a list of ExecutableDirectories to SLURM as a single MPS job.

    This means that all jobs submitted will be executed on the same GPU

    Parameters
    ----------
    exec_dirs : list[ExecutableDirectory]
        An iterable of ExecutableDirectory objects
    partition : str or list of str
        The queue (partition) or list of queues to run on. If list, the one offering earliest initiation will be used.
    jobname : str
        Job name (identifier)
    priority : str
        Job priority
    ncpu : int
        Number of CPUs to use for a single job
    ngpu : int
        Number of GPUs to use for a single job
    memory : int
        Amount of memory per job (MiB)
    gpumemory : int
        Only run on GPUs with at least this much memory. Needs special setup of SLURM. Check how to define gpu_mem on
        SLURM.
    walltime : int
        Job timeout (s)
    mailtype : str
        When to send emails. Separate options with commas like 'END,FAIL'.
    mailuser : str
        User email address.
    outputstream : str
        Output stream.
    errorstream : str
        Error stream.
    nodelist : list
        A list of nodes on which to run every job at the *same time*! Careful! The jobs will be duplicated!
    exclude : list
        A list of nodes on which *not* to run the jobs. Use this to select nodes on which to allow the jobs to run on.
    envvars : str
        Envvars to propagate from submission node to the running node (comma-separated)
    prerun : list
        Shell commands to execute on the running node before the job (e.g. loading modules)

    Examples
    --------
    >>> ed1 = kdeep(outdir="test1", pdb=apps.kdeep.files["tests/10gs_protein.pdb"], sdf=apps.kdeep.files["tests/10gs_ligand.sdf"], modelfile=kdeep.datasets.default)
    >>> ed2 = kdeep(outdir="test2", dataset=apps.kdeep.files["tests/dataset.zip"], modelfile=kdeep.datasets.default)
    >>> slurm_mps([ed1, ed2], partition="normalGPU", ncpu=1, ngpu=1)
    """
    from jobqueues.slurmqueue import SlurmQueue

    sl = SlurmQueue()

    if exec_dirs[0].execution_resources is not None:
        # Set app defaults
        for arg in exec_dirs[0].execution_resources:
            setattr(sl, arg, exec_dirs[0].execution_resources[arg])

    # Set user-specified arguments
    for arg in kwargs:
        setattr(sl, arg, kwargs[arg])

    sl.submit(
        dirs=[ed.dirname for ed in exec_dirs],
        runscripts=[ed.runsh for ed in exec_dirs],
        nvidia_mps=True,
    )
    return sl

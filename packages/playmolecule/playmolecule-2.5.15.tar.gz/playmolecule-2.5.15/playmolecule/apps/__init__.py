# (c) 2015-2023 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from glob import glob
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from playmolecule._appfiles import _File, _Artifacts, _get_app_files
from playmolecule._tests import _Tests
import shutil

# Do not remove unused imports. They are used in the jinja file probably
from pathlib import Path
import stat
import logging
import enum


logger = logging.getLogger(__name__)


class KWARGS(dict):
    pass


_function_dict = {}


env = Environment(
    loader=PackageLoader("playmolecule", "share"),
    autoescape=select_autoescape(["*"]),
)


@enum.unique
class JobStatus(enum.IntEnum):
    """Job status codes describing the current status of a job

    * WAITING_INFO : Waiting for status from the job. Job has not started yet computation.
    * RUNNING : Job is currently running
    * COMPLETED : Job has successfully completed
    * ERROR : Job has exited with an error
    """

    WAITING_INFO = 0
    RUNNING = 1
    COMPLETED = 2
    ERROR = 3

    def describe(self):
        codes = {0: "Waiting info", 1: "Running", 2: "Completed", 3: "Error"}
        return codes[self.value]

    def __str__(self):
        return self.describe()


JOB_TIMEOUT = 60  # Timeout after which if there is no newer date in .pm.alive we consider the job dead


class ExecutableDirectory:
    """Executable directory class.

    All app functions will create a folder and return to you an `ExecutableDirectory` object.
    This is a self-contained directory including all app input files which can be executed either locally or on a cluster.
    If it's not executed locally make sure the directory can be accessed from all machines
    in the cluster (i.e. is located on a shared filesystem).
    """

    def __init__(
        self, dirname, inputs_dir=None, _execution_resources=None, _input_json=None
    ) -> None:
        self.dirname = dirname
        self.runsh = os.path.basename(inputs_dir) + ".sh"
        self.inputs_dir = inputs_dir

        self.execution_resources = _execution_resources
        self.slurmq = None
        self._input_json = _input_json

    @property
    def status(self):
        """Returns current status of the ExecutableDirectory

        Examples
        --------
        >>> ed = proteinprepare(outdir="test", pdbid="3ptb")
        >>> ed.slurm(ncpu=1, ngpu=0)
        >>> print(ed.status)
        """
        from playmolecule import PM_APP_ROOT
        from playmolecule._executors._pmbackend import _pmbackend_status
        import datetime
        import json

        if PM_APP_ROOT.startswith("http"):
            if self._job_id is None:
                raise RuntimeError("Job ID is not set. Please run the job first.")
            return _pmbackend_status(self.dirname, self._job_id)

        # If the container reported completion or error
        # TODO: Remove the checks in dirname once all apps have been updated to write in the sentinel_dir
        if os.path.exists(os.path.join(self.inputs_dir, ".pm.done")) or os.path.exists(
            os.path.join(self.dirname, ".pm.done")
        ):
            return JobStatus.COMPLETED
        elif os.path.exists(os.path.join(self.inputs_dir, ".pm.err")) or os.path.exists(
            os.path.join(self.dirname, ".pm.err")
        ):
            return JobStatus.ERROR

        # If the container is reporting aliveness
        heartbeat = os.path.join(self.inputs_dir, ".pm.alive")
        if not os.path.exists(heartbeat):
            heartbeat = os.path.join(self.dirname, ".pm.alive")
        if os.path.exists(heartbeat):
            with open(heartbeat, "r") as f:
                timestamp_str = f.read().strip()
                timestamp = None

                if len(timestamp_str):
                    try:
                        timestamp = datetime.datetime.fromisoformat(timestamp_str)
                    except Exception:
                        logger.error(f"Malformed timestamp in {heartbeat}")

                if timestamp is not None:
                    diff = datetime.datetime.now() - timestamp
                    if diff > datetime.timedelta(seconds=JOB_TIMEOUT):
                        return JobStatus.ERROR
                    else:
                        return JobStatus.RUNNING

        # If it was submitted to SLURM handle the state here
        if self.slurmq is not None:
            from playmolecule._executors._slurm import get_slurm_status

            return get_slurm_status(self.slurmq)

        # Alternatively check if expected outputs exist
        outputs = os.path.join(self.inputs_dir, "expected_outputs.json")
        if os.path.exists(outputs):
            with open(outputs, "r") as f:
                outputs = json.load(f)

            for outf in outputs:
                if len(glob(os.path.join(self.dirname, outf))) == 0:
                    return JobStatus.RUNNING
            else:
                return JobStatus.COMPLETED

        logger.warning(
            f"Could not yet determine job status for directory {self.dirname}. The job might have not started running yet."
        )
        return JobStatus.WAITING_INFO

    def run(self, queue=None, verbose=True, **kwargs):
        """Execute the directory locally

        If no queue is specified it will run the job locally.

        Examples
        --------
        >>> ed = proteinprepare(outdir="test", pdbid="3ptb")
        >>> ed.run()

        Specifying a queue

        >>> ed.run(queue="slurm", partition="normalCPU", ncpu=3, ngpu=1)

        Alternative syntax for

        >>> ed.slurm(partition="normalCPU", ncpu=3, ngpu=1)
        """
        from playmolecule import PM_APP_ROOT
        from playmolecule._executors._pmbackend import _run_on_pmbackend

        self.slurmq = None  # New execution. Set to None

        if PM_APP_ROOT.startswith("http"):
            self._job_id = _run_on_pmbackend(self._input_json, **kwargs)
            return

        if queue is None:
            import subprocess

            logfile = os.path.join(self.dirname, self.runsh.replace(".sh", ".log"))

            with open(logfile, "w") as logfile:
                process = subprocess.Popen(
                    ["bash", self.runsh],
                    cwd=self.dirname,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                for line in process.stdout:
                    if verbose:
                        print(line, end="")  # Write to terminal
                    logfile.write(line)  # Write to file
                process.wait()
        else:
            if queue.lower() == "slurm":
                self.slurm(**kwargs)
            elif queue.lower() == "pmws":
                _run_on_pmbackend(self.inputs_dir, **kwargs)

    def slurm(self, **kwargs):
        """Submit simulations to SLURM cluster

        Parameters
        ----------
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
        >>> ed = proteinprepare(outdir="test", pdbid="3ptb")
        >>> ed.slurm(partition="normalCPU", ncpu=1, ngpu=0)
        """
        from playmolecule._executors._slurm import submit_slurm

        self.slurmq = submit_slurm(
            self.dirname, self.runsh, self.execution_resources, **kwargs
        )


_validators = {
    "str": str,
    "Path": (str, Path, _File),
    "bool": bool,
    "int": (int, float),
    "float": (int, float),
    "dict": dict,
}


def _inner_function(
    args: dict,
    function_name: str,
    function_resources: dict,
    func_manifest: dict,
    slpm_path: str,
    files: dict,
    run_sh: str,
):
    from playmolecule.apps import _write_inputs, ExecutableDirectory
    from playmolecule import PM_APP_ROOT
    from datetime import datetime
    import uuid
    import shutil
    import os

    assert (
        "outdir" in args or "execdir" in args
    ), "Functions must accept either 'outdir' or 'execdir'"

    if "outdir" in args:
        outdir = args["outdir"]
        args["outdir"] = "."
    elif "execdir" in args:
        if isinstance(args["execdir"], _File):
            args["execdir"] = args["execdir"].path
        outdir = args["execdir"]
        args["execdir"] = "."

    if PM_APP_ROOT.startswith("http"):
        from playmolecule._executors._pmbackend import _get_inputs

        input_dict = _get_inputs(args, func_manifest, files, slpm_path)
        ed = ExecutableDirectory(
            dirname=outdir,
            inputs_dir=outdir,
            _execution_resources=function_resources,
            _input_json=input_dict,
        )
        BLOCKING = os.getenv("PM_BLOCKING", "0") == "1"
        if not BLOCKING:
            return ed
        else:
            import time

            ed.run()
            time.sleep(2)
            while ed.status not in (JobStatus.COMPLETED, JobStatus.ERROR):
                time.sleep(3)
            return None

    if "scratchdir" in args:
        if args["scratchdir"] is None:
            args["scratchdir"] = os.path.join(outdir, "scratch")
        os.makedirs(args["scratchdir"], exist_ok=True)

    now = datetime.now()
    identifier = f"_{now.strftime(r'%d_%m_%Y_%H_%M')}_{uuid.uuid4().hex[:8]}"
    inputs_dir = os.path.join(outdir, f"run{identifier}")
    _write_inputs(
        outdir, inputs_dir, args, func_manifest, files, function_name, slpm_path
    )

    target_run_sh = None
    if run_sh is not None and len(run_sh):
        target_run_sh = os.path.join(outdir, f"run{identifier}.sh")
        shutil.copy(run_sh, target_run_sh)
        st = os.stat(target_run_sh)
        os.chmod(target_run_sh, st.st_mode | stat.S_IEXEC)

    return ExecutableDirectory(
        dirname=outdir, inputs_dir=inputs_dir, _execution_resources=function_resources
    )


def _write_inputs(
    write_dir, inputs_dir, arguments, manifest, app_files, function, slpm_path
):
    import json

    os.makedirs(inputs_dir, exist_ok=True)

    if "outputs" in manifest:
        with open(os.path.join(inputs_dir, "expected_outputs.json"), "w") as f:
            json.dump(manifest["outputs"], f)

    # Validate arg types and copy Path arguments to folder
    original_paths = {}
    for arg in manifest["params"]:
        name = arg["name"]
        argtype = arg["type"]
        nargs = None if "nargs" not in arg else arg["nargs"]

        vals = arguments[name]
        if nargs is None and isinstance(vals, (list, tuple)):
            raise RuntimeError(
                f"Argument '{name}' was passed value '{vals}' which is of type '{type(vals).__name__}'. Was expecting a single value of type '{argtype}'."
            )
        if not isinstance(vals, (list, tuple)):
            vals = [vals]

        # Validate type
        if argtype in _validators:
            validator = _validators[argtype]
            for val in vals:
                if val is not None and not isinstance(val, validator):
                    raise RuntimeError(
                        f"Argument '{name}' was passed value '{val}' which is of type '{type(val).__name__}'. Was expecting value of type '{argtype}'."
                    )
        else:
            logger.warning(
                f"Could not find validator for type: {arg['type']}. Please notify the PM developers."
            )

        # Copy Path-type arguments to folder
        if (
            argtype == "Path"
            and name in arguments
            and name not in ("outdir", "scratchdir", "execdir")
        ):
            newvals = []
            for val in vals:
                if val is None or (isinstance(val, str) and val == ""):
                    continue

                if isinstance(val, str) and val.startswith("app://files"):
                    val = app_files[val.replace("app://files/", "")]

                if isinstance(val, _File):
                    newvals.append(val.path)
                    continue  # Don't copy artifacts

                val = os.path.abspath(val)

                # Deduplicate file names
                outname = os.path.join(inputs_dir, os.path.basename(val))
                if os.path.exists(outname) and val != original_paths[outname]:
                    i = 0
                    while os.path.exists(outname):
                        parts = os.path.splitext(os.path.basename(val))
                        outname = os.path.join(inputs_dir, f"{parts[0]}_{i}{parts[1]}")
                        i += 1

                original_paths[outname] = val

                if "PM_SYMLINK" in os.environ:
                    os.symlink(val, outname)
                else:
                    if os.path.isdir(val):
                        shutil.copytree(val, outname)
                    else:
                        shutil.copy(val, outname)
                newvals.append(os.path.relpath(outname, write_dir))

            if len(newvals) == 0:
                arguments[name] = None
            elif len(newvals) == 1:
                arguments[name] = newvals[0]
            else:
                arguments[name] = newvals

        # Special case for the HTMD app which takes arbitrary function arguments
        if argtype == "KWARGS" and name in arguments:
            if vals[0] is not None:
                for key, item_vals in vals[0].items():  # Iterate over it like a dict
                    if not isinstance(item_vals, (list, tuple)):
                        item_vals = [item_vals]
                    newvals = []
                    for val in item_vals:
                        if val is None:
                            continue

                        if isinstance(val, _File):
                            newvals.append(val.path)
                            continue  # Don't copy artifacts

                        if not isinstance(val, str) or not os.path.exists(val):
                            newvals.append(val)
                            continue
                        val = os.path.abspath(val)

                        outname = os.path.join(inputs_dir, os.path.basename(val))
                        if os.path.exists(outname) and val != original_paths[outname]:
                            i = 0
                            while os.path.exists(outname):
                                parts = os.path.splitext(os.path.basename(val))
                                outname = os.path.join(
                                    inputs_dir, f"{parts[0]}_{i}{parts[1]}"
                                )
                                i += 1

                        original_paths[outname] = val

                        if "PM_SYMLINK" in os.environ:
                            os.symlink(val, outname)
                        else:
                            if os.path.isdir(val):
                                shutil.copytree(val, outname)
                            else:
                                shutil.copy(val, outname)
                        newvals.append(os.path.relpath(outname, write_dir))

                    if len(newvals) == 0:
                        arguments[name][key] = None
                    elif len(newvals) == 1:
                        arguments[name][key] = newvals[0]
                    else:
                        arguments[name][key] = newvals

    with open(os.path.join(inputs_dir, "inputs.json"), "w") as f:
        json.dump(
            {"function": function, "slpm_path": slpm_path, "arguments": arguments},
            f,
            indent=4,
        )

    with open(os.path.join(inputs_dir, "original_paths.json"), "w") as f:
        json.dump(original_paths, f, indent=4)

    with open(os.path.join(inputs_dir, ".manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)


def _docs_from_manifest(manifest, appname, appdir):
    from copy import deepcopy

    manifest = deepcopy(manifest)

    if "description" not in manifest:
        raise RuntimeError(
            "Missing the 'description' field in your app manifest with a description of the app."
        )

    docs = [manifest["description"], "", "Parameters", "----------"]
    for i, param in enumerate(manifest["params"]):
        pp = f"{param['name']} : {param['type']}"
        if "choices" in param and param["choices"] is not None:
            choices = '", "'.join(param["choices"])
            pp += f', choices=("{choices}")'
        docs.append(pp)
        docs.append(f"    {param['description']}")

    missing = []

    if "outputs" in manifest:
        docs.append("")
        docs.append("Outputs")
        docs.append("-------")
        for key, val in manifest["outputs"].items():
            docs.append(key)
            docs.append(f"    {val}")
    else:
        missing.append("outputs")

    if "resources" in manifest and manifest["resources"] is not None:
        docs.append("")
        docs.append("Note")
        docs.append("----")
        docs.append("Minimum job requirements::")
        docs.append("")
        for key, val in manifest["resources"].items():
            docs.append(f"    {key}: {val}")

    if "examples" in manifest:
        docs.append("")
        docs.append("Examples")
        docs.append("--------")
        for exp in manifest["examples"]:
            docs.append(f">>> {exp}")
    else:
        missing.append("examples")

    if "tests" in manifest:
        for test_name in manifest["tests"]:
            desc = manifest["tests"][test_name]["description"]
            args = manifest["tests"][test_name]["arguments"]
            args_str = ""
            for key, vals in args.items():
                if not isinstance(vals, (list, tuple)):
                    vals = [vals]
                for i in range(len(vals)):
                    val = vals[i]
                    if isinstance(val, str):
                        if val.startswith("tests/"):
                            val = f"{appname}.files['{val}']"
                        elif val.startswith("datasets/"):
                            val = val.replace("datasets/", "")
                            val = f"{appname}.datasets.{val}"
                        elif val.startswith("artifacts/"):
                            val = val.replace("artifacts/", "")
                            val = f"{appname}.artifacts.{val}"
                        else:
                            val = f"'{val}'"
                    vals[i] = val
                if len(vals) > 1:
                    args_str += f"{key}=[{', '.join(map(str, vals))}], "
                else:
                    args_str += f"{key}={vals[0]}, "

            docs.append("")
            docs.append(desc)
            docs.append(f">>> {appname}(outdir='./out', {args_str[:-2]}).run()")

        if "examples" in missing:  # if there are tests don't complain about examples
            missing.remove("examples")

    if appdir is not None:
        tutorials = glob(os.path.join(appdir, "tutorials", "*"))
        if len(tutorials):
            docs.append("")
            docs.append("Notes")
            docs.append("-----")
            docs.append("Tutorials are available for this app:")
            docs.append("")
            for fname in tutorials:
                docs.append(f"    - {fname}")

    if len(missing):
        logger.warning(f"{appname} manifest is missing fields: {', '.join(missing)}")
    return docs


def _args_from_manifest(func_args):
    # Fix for old apps
    fix_old_types = {"string": "str", "file": "Path"}

    # Arguments which don't have a "value" field should be mandatory
    for arg in func_args:
        if "mandatory" not in arg:
            arg["mandatory"] = "value" not in arg

    args = []
    # Ensure mandaroty args come first if someone messes up the manifest
    mand_params = [x for x in func_args if x["mandatory"]]
    opt_params = [x for x in func_args if not x["mandatory"]]

    params = mand_params + opt_params
    for i, param in enumerate(params):
        atype = param["type"]
        if atype in fix_old_types:
            atype = fix_old_types[atype]
        if atype == "str_to_bool":
            atype = "bool"

        atype_final = atype
        if "nargs" in param and param["nargs"] is not None:
            atype_final = f"list[{atype}]"

        argstr = f"{param['name']} : {atype_final}"

        if not param["mandatory"]:
            default = param["value"]

            if atype in ("str", "Path") and param["value"] is not None:
                if isinstance(default, (list, tuple)):
                    for k in range(len(default)):
                        if default[k].startswith("app://files"):
                            # Handle app://files URIs
                            default[k] = (
                                f"files['{default.replace('app://files/', '')}']"
                            )
                elif default.startswith("app://files"):
                    # Handle app://files URIs
                    default = f"files['{default.replace('app://files/', '')}']"
                else:
                    default = f"\"{param['value']}\""

            # Fix for old apps
            if atype not in ("str", "Path") and param["value"] == "":
                default = None

            argstr += f" = {default}"

        if i != len(params) - 1:
            argstr += ","
        args.append(argstr)
    return args


def __ensure_module_path(module_path):
    """
    Ensures that all parts of the dotted module path exist in sys.modules
    and returns the final module object.
    """
    import sys
    import types

    parts = module_path.split(".")
    full_path = ""
    parent = None

    for part in parts:
        full_path = f"{full_path}.{part}" if full_path else part
        if full_path not in sys.modules:
            mod = types.ModuleType(full_path)
            sys.modules[full_path] = mod
            if parent:
                setattr(parent, part, mod)
        parent = sys.modules[full_path]

    return sys.modules[full_path]


def _manifest_to_func(appname, app_versions):
    from copy import deepcopy

    template = env.get_template("func.py.jinja")

    for version in app_versions:
        manifest = app_versions[version]["manifest"]
        new_mode = True
        if (
            "functions" not in manifest
        ):  # TODO: Deprecate eventually. Just for backwards compatibility
            new_mode = False
            manifest = deepcopy(manifest)
            try:
                manifest["functions"] = [
                    {
                        "function": (
                            manifest["container_config"]["appfunction"]
                            if "container_config" in manifest
                            else "main"
                        ),
                        "env": "base",
                        "resources": manifest.get("resources", None),
                        "examples": manifest.get("examples", []),
                        "params": manifest["params"],
                        "tests": manifest.get("tests", {}),
                        "outputs": manifest.get("outputs", {}),
                        "description": manifest["description"],
                    }
                ]
            except Exception:
                import traceback

                logger.error(
                    f"Failed to parse manifest for app {appname} version {version} due to error:\n{traceback.format_exc()}"
                )
                continue

        module_path = f"playmolecule.apps.{appname}.{version}"
        module = __ensure_module_path(module_path)

        setattr(module, "__manifest__", deepcopy(manifest))

        app_artifacts = None
        source_dir = app_versions[version].get("appdir")
        if source_dir is not None:
            source_dir = os.path.join(source_dir, "files")
        app_files = _get_app_files(source_dir, manifest)
        setattr(module, "files", app_files)

        artifact_dict = manifest.get("artifacts", manifest.get("datasets", {}))
        if len(artifact_dict):
            app_artifacts = _Artifacts(artifact_dict, app_files)
            setattr(module, "artifacts", app_artifacts)
            setattr(module, "datasets", app_artifacts)

        func_names = []
        for idx, func_mani in enumerate(manifest["functions"]):
            try:
                func_name = func_mani["function"].split(".")[-1]
                if func_name == "main":
                    func_name = appname

                run_sh = app_versions[version].get("run.sh")
                code = template.render(
                    function=func_mani["function"],
                    function_idx=idx,
                    function_name=func_name,
                    function_args=_args_from_manifest(func_mani["params"]),
                    function_docs=_docs_from_manifest(
                        func_mani, appname, app_versions[version]["appdir"]
                    ),
                    function_resources=func_mani.get("resources", None),
                    module_path=module_path,
                    slpm_path=f"{appname}.{version}.{func_name}",
                    run_sh=run_sh if run_sh else "",
                )
                local_ns = {"files": app_files}
                exec(code, globals().copy(), local_ns)
                _func = local_ns[func_name]

                tests = _Tests(func_mani["tests"], _func, app_files, app_artifacts)
                # Add some metadata to the function object
                _func.tests = tests
                _func._name = func_name
                _func.__manifest__ = deepcopy(func_mani)
                func_names.append(func_name)
                setattr(module, func_name, _func)
                _function_dict[f"{module_path}.{func_name}"] = _func
            except Exception:
                import traceback

                logger.error(
                    f"Failed to parse manifest for app {appname} version {version} with error: {traceback.format_exc()}"
                )
    return func_names


def _link_latest_version(appname, latest, func_names):
    import sys

    # Link the latest version of the app to the top level module
    parent_module = sys.modules[f"playmolecule.apps.{appname}"]
    latest_module = sys.modules[f"playmolecule.apps.{appname}.{latest}"]
    for symbol in func_names + [
        "artifacts",
        "datasets",
        "files",
        "tests",
        "__manifest__",
    ]:
        if symbol not in parent_module.__dict__ and symbol in latest_module.__dict__:
            setattr(
                sys.modules[f"playmolecule.apps.{appname}"],
                symbol,
                getattr(
                    sys.modules.get(f"playmolecule.apps.{appname}.{latest}"), symbol
                ),
            )


def _check_folder_validity(root_dir, app_d):
    import re

    folder_path = os.path.relpath(app_d, root_dir)

    # Check if the folder consists only of lowercase letters, numbers, underscores or path separators
    if not re.match(r"^[a-z0-9_/\\]+$", folder_path):
        logger.warning(
            f'Path {app_d} has invalid characters in the part: "{folder_path}". Only lowercase letters, numbers and underscores are allowed. Please fix the path. Skipping...'
        )
        return False
    return True


def _set_root(root_dir):
    import json
    from natsort import natsorted
    import playmolecule

    if root_dir.startswith("http"):
        from playmolecule._executors._pmbackend import _set_root_pmbackend

        _set_root_pmbackend()
        return

    logger.info(f"PlayMolecule home: {root_dir}")

    _setup_folders(root_dir)

    for app_d in natsorted(glob(os.path.join(root_dir, "apps", "*", ""))):
        appname = os.path.basename(os.path.abspath(app_d))
        if not _check_folder_validity(root_dir, app_d):
            continue

        versions = glob(os.path.join(app_d, "*"))
        versions.sort(key=lambda s: natsorted(os.path.basename(s)))

        app_versions = {}
        for vv in versions:
            vname = os.path.basename(vv)
            if not _check_folder_validity(root_dir, vv):
                continue

            jf = glob(os.path.join(vv, "*.json"))
            if len(jf) > 1:
                print(f"ERROR: Multiple json files found in {vv}")
            if len(jf) == 1 and os.stat(jf[0]).st_size != 0:
                try:
                    with open(jf[0]) as f:
                        app_versions[vname] = {
                            "manifest": json.load(f),
                            "appdir": vv,
                            "run.sh": os.path.join(vv, "run.sh"),
                        }
                except Exception as e:
                    logger.error(
                        f"Failed at parsing manifest JSON file {jf[0]} with error: {e}"
                    )
        if len(app_versions):
            func_names = _manifest_to_func(appname, app_versions)
            _link_latest_version(appname, os.path.basename(versions[-1]), func_names)

    dsdir = os.path.join(root_dir, "datasets")
    dsjson = os.path.join(dsdir, "datasets.json")
    if os.path.exists(dsdir) and os.path.exists(dsjson):
        with open(dsjson) as f:
            manifest = json.load(f)
        files = _get_app_files(dsdir)
        playmolecule.datasets = _Artifacts(manifest["datasets"], files)


def _setup_folders(root_dir):
    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(os.path.join(root_dir, "apps"), exist_ok=True)
    os.makedirs(os.path.join(root_dir, "datasets"), exist_ok=True)

    apptainer_runner = os.path.join(root_dir, "apptainer_run.sh")
    if not os.path.exists(apptainer_runner):
        try:
            import questionary

            license_type = questionary.select(
                "Do you use a floating license server (IP/Port) or a license file?:",
                choices=["Floating License Server", "License File"],
                default="Floating License Server",
                use_shortcuts=True,
            ).unsafe_ask()
            if license_type == "Floating License Server":
                license_ip = questionary.text(
                    message="Type the IP/URL of the license server:"
                ).unsafe_ask()
                license_port = questionary.text(
                    message="Type the port of the license server:", default="27000"
                ).unsafe_ask()
                license_file = f"{license_port}@{license_ip}"
            else:
                license_file = questionary.path(
                    message="Path to license file:",
                ).unsafe_ask()
                new_lic_file = os.path.join(root_dir, "license.dat")
                if os.path.abspath(new_lic_file) != os.path.abspath(license_file):
                    shutil.copy(license_file, new_lic_file)
                license_file = new_lic_file
        except KeyboardInterrupt:
            raise RuntimeError("PlayMolecule setup cancelled...")

        template = env.get_template("apptainer_run.sh")
        fstring = template.render(
            license_file_or_server=license_file,
            root_dir=root_dir,
        )
        with open(apptainer_runner, "w") as f:
            f.write(fstring)

        st = os.stat(apptainer_runner)
        os.chmod(
            apptainer_runner, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

        with open(os.path.join(root_dir, "license_path.txt"), "w") as f:
            f.write(license_file)

    if len(glob(os.path.join(root_dir, "apps", "*", ""))) == 0:
        from playmolecule._update import update_apps

        update_apps()

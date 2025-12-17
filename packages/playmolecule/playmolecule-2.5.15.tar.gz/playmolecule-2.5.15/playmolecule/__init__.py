# (c) 2015-2023 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
import logging.config
from playmolecule.apps import _set_root, JobStatus, ExecutableDirectory
from playmolecule._executors._slurm import slurm_mps
from playmolecule._executors._pmbackend import login, logout
from playmolecule._update import update_apps
from importlib.metadata import version as __version
from importlib.metadata import PackageNotFoundError
from playmolecule._protocols import __find_protocols

# from importlib.resources import files

try:
    __version__ = __version("playmolecule")
except PackageNotFoundError:
    pass

dirname = os.path.dirname(__file__)

try:
    logging.config.fileConfig(
        os.path.join(dirname, "logging.ini"), disable_existing_loggers=False
    )
except Exception:
    print("playmolecule: Logging setup failed")


logger = logging.getLogger(__name__)
PM_APP_ROOT = os.environ.get("PM_APP_ROOT", None)
PM_SKIP_SETUP = os.environ.get("PM_SKIP_SETUP", False)
if not PM_SKIP_SETUP and PM_APP_ROOT is None:
    raise RuntimeError(
        "Could not find environment variable PM_APP_ROOT. Please set the variable to set the path to the app root."
    )

if PM_APP_ROOT is not None and not PM_SKIP_SETUP:
    # Necessary for PMWS URL but also good for paths
    while PM_APP_ROOT[-1] == "/":
        PM_APP_ROOT = PM_APP_ROOT[:-1]
    _set_root(PM_APP_ROOT)


def describe_apps(as_dict=False):
    from playmolecule.apps import _function_dict

    app_dict = {}
    sorted_keys = sorted(_function_dict.keys())
    for func_path in sorted_keys:
        func = _function_dict[func_path]
        if "name" in func.__manifest__:
            name = func.__manifest__["name"]
        else:
            name = func_path.split(".")[-1]
        app_dict[func_path] = {"description": func.__doc__.strip().split("\n")[0]}
        if not as_dict:
            print(name, func_path)
            desc = func.__doc__.strip().split("\n")[0]
            print(f"    {desc}")

    if as_dict:
        return app_dict


protocols = None
# Add the acellera-protocols folder as a submodule
if not PM_SKIP_SETUP:
    protocols = __find_protocols(PM_APP_ROOT)

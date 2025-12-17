# (c) 2015-2023 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
from playmolecule.apps import JobStatus
import requests
import logging
import json
import os

logger = logging.getLogger(__name__)

# --- Global State ---
# This persists as long as the python script is running.
# We initialize it immediately so it's ready to use.
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_internal_session = requests.Session()

# Configure connection pooling + retries.
# This makes status polling resilient to transient disconnects (e.g. backend/proxy
# closing an idle keep-alive connection).
_retry_strategy = Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET", "POST"}),
    respect_retry_after_header=True,
)
_adapter = HTTPAdapter(
    max_retries=_retry_strategy,
    pool_connections=10,
    pool_maxsize=10,
    pool_block=False,
)
_internal_session.mount("http://", _adapter)
_internal_session.mount("https://", _adapter)

# Default timeout: (connect, read). Avoids hanging forever on backend issues.
_DEFAULT_TIMEOUT = (5, 30)

_base_url = os.environ["PM_APP_ROOT"]
_headers = {}


def login(username, password):
    """
    Authenticates and stores cookies in the global module session.
    """
    if not _base_url.startswith("http"):
        raise RuntimeError(f"Invalid backend URL: {_base_url}")

    # Get the unauthenticated CSRF token
    response = _internal_session.get(
        f"{_base_url}/auth/csrf", headers=_headers, timeout=_DEFAULT_TIMEOUT
    )
    response.raise_for_status()
    csrf_token = response.json()["csrf_token"]

    headers = _headers.copy()
    headers["X-CSRF-Token"] = csrf_token

    # This updates _internal_session.cookies automatically
    response = _internal_session.post(
        f"{_base_url}/auth/login",
        data={"username": username, "password": password},
        headers={"X-CSRF-Token": csrf_token},
        timeout=_DEFAULT_TIMEOUT,
    )
    response.raise_for_status()

    print(f"Logged in as {username}")


def logout():
    """
    Clears the cookies from the global session.
    """
    _internal_session.cookies.clear()
    print("Logged out.")


def _get_apps():
    print("Querying", f"{_base_url}/apps/manifests")
    rsp = requests.get(f"{_base_url}/apps/manifests", timeout=_DEFAULT_TIMEOUT)
    if rsp.status_code != 200:
        raise RuntimeError(f"Failed to get apps from {_base_url}: {rsp.text}")

    apps = {}
    for app_module, manifest in rsp.json().items():
        app_name = app_module.split(".")[0]
        if app_name not in apps:
            apps[app_name] = {}

        version = manifest.get("version")
        if version is None:
            version = manifest["container_config"]["version"]
        apps[app_name][f"v{version}"] = {
            "manifest": manifest,
            "appdir": None,
            "run.sh": None,
        }

    return apps


def _set_root_pmbackend():
    from playmolecule.apps import _manifest_to_func, _link_latest_version
    from natsort import natsorted

    app_manifests = _get_apps()

    for appname in app_manifests:
        func_names = _manifest_to_func(appname, app_manifests[appname])
        _link_latest_version(
            appname, natsorted(app_manifests[appname].keys())[-1], func_names
        )


def _pmbackend_status(dirname, job_id):
    import safezipfile
    import io

    # Query job metadata

    try:
        res = _internal_session.get(
            f"{_base_url}/jobs?prefix={job_id}",
            timeout=_DEFAULT_TIMEOUT,
            headers={"Connection": "close"},
        )
    except requests.exceptions.RequestException as e:
        # Typical root cause: proxy/backend closes an idle keep-alive connection
        # and the client tries to reuse it (RemoteDisconnected).
        logger.warning(f"PM backend status poll failed for job '{job_id}': {e}")
        return JobStatus.WAITING_INFO
    res.raise_for_status()
    jobs = res.json()
    if not isinstance(jobs, list) or len(jobs) != 1:
        return JobStatus.WAITING_INFO

    metadata = jobs[0]
    status = {0: "WAITING_INFO", 1: "RUNNING", 2: "COMPLETED", 3: "ERROR"}[
        int(metadata["status"])
    ]
    # On error, return combined error text (no files)
    if status == "ERROR":
        res = _internal_session.get(
            f"{_base_url}/files?prefix={job_id}/", timeout=_DEFAULT_TIMEOUT
        )
        files = res.json()
        errf = None
        outf = None
        for f in files.values():
            if f["name"].startswith("slurm."):
                if f["name"].endswith(".err"):
                    errf = f["uri"]
                elif f["name"].endswith(".out"):
                    outf = f["uri"]

        errres = _internal_session.get(
            f"{_base_url}/file/{job_id}{errf}", timeout=_DEFAULT_TIMEOUT
        )
        outres = _internal_session.get(
            f"{_base_url}/file/{job_id}{outf}", timeout=_DEFAULT_TIMEOUT
        )
        combined_error = f"{outres.content}{errres.content}"
        return JobStatus.ERROR

    # While running/waiting: no files
    if status in ("WAITING_INFO", "RUNNING"):
        return JobStatus.RUNNING

    # Completed. Download files
    res = _internal_session.get(
        f"{_base_url}/file/{job_id}/",
        timeout=(5, 360),  # Longer read timeout for file downloads
    )
    with safezipfile.ZipFile(io.BytesIO(res.content)) as zf:
        zf.extractall(dirname, max_files=1e9, max_file_size=1e11, max_total_size=1e12)

    return JobStatus.COMPLETED


def _get_inputs(arguments, manifest, app_files, slpm_path):
    from playmolecule.apps import _validators
    from playmolecule._appfiles import _File

    files = []
    file_handles = []  # Keep track of file handles to close later

    if "outdir" in arguments:
        del arguments["outdir"]
    if "scratchdir" in arguments:
        del arguments["scratchdir"]
    if "execdir" in arguments:
        del arguments["execdir"]

    # Validate arg types and copy Path arguments to folder
    original_paths = {}
    for arg in manifest["params"]:
        name = arg["name"]
        argtype = arg["type"]
        nargs = None if "nargs" not in arg else arg["nargs"]

        if name in ("outdir", "scratchdir", "execdir"):
            continue

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

        # Open files for Path-type arguments
        if argtype == "Path" and name in arguments:
            newvals = []
            for val in vals:
                if val is None or (isinstance(val, str) and val == ""):
                    continue

                if isinstance(val, str) and val.startswith("app://files"):
                    newvals.append(val)
                    continue

                if isinstance(val, _File):
                    newvals.append(val.path)
                    continue  # Don't copy artifacts

                val = os.path.abspath(val)
                filename = os.path.basename(val)
                if os.path.isdir(val):
                    raise RuntimeError(
                        f"Directory arguments are not supported for PM backend: {val}"
                    )
                fh = open(val, "rb")
                file_handles.append(fh)  # Track for cleanup
                files.append((name, (filename, fh, "application/octet-stream")))
                newvals.append(filename)

            if len(newvals) == 0:
                arguments[name] = None
            elif len(newvals) == 1:
                arguments[name] = newvals[0]
            else:
                arguments[name] = newvals

    return {
        "arguments": arguments,
        "slpm_path": slpm_path,
        "files": files,
        "file_handles": file_handles,
    }


def _run_on_pmbackend(input_dict, job_id=None, prefix="default-project/", _logger=True):
    if "access_token" not in _internal_session.cookies:
        raise RuntimeError("Access token not found. Please login to the PM backend.")

    if job_id is not None:
        input_dict["arguments"]["_job_id"] = job_id

    file_handles = input_dict.get("file_handles", [])

    try:
        res = _internal_session.post(
            f"{_base_url}/apps/{input_dict['slpm_path']}/run?prefix={prefix}",
            data={"input": json.dumps(input_dict["arguments"])},
            files=input_dict["files"],
            headers={"X-CSRF-Token": _internal_session.cookies.get("csrf_token")},
            timeout=(10, 120),
        )

        if res.status_code != 200:
            raise RuntimeError(f"Failed to run job on {_base_url}: {res.text}")
        return res.json()["job_id"]
    finally:
        # Always close file handles, even if an error occurs
        for fh in file_handles:
            try:
                fh.close()
            except Exception as e:
                logger.warning(f"Failed to close file handle: {e}")


def _get_app_files_pmbackend(manifest):
    from playmolecule._appfiles import _File

    files = manifest.get("files", {})
    for name, description in files.items():
        while name.endswith("/"):
            name = name[:-1]
        path = f"app://files/{name}"
        files[name] = _File(name, path, description)

    return files

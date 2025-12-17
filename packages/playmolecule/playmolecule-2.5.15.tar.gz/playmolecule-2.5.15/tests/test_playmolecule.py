from glob import glob
import json
import os
import tempfile
import pytest
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))


def prepare(datadir):
    outdir = str(datadir.join("out"))
    scratchdir = str(datadir.join("scratch"))
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(scratchdir, exist_ok=True)
    return outdir, scratchdir


@pytest.fixture
def test_app_root():
    """Set up the test app root"""
    old_root = os.environ.get("PM_APP_ROOT")
    os.environ["PM_APP_ROOT"] = os.path.join(curr_dir, "test_playmolecule")
    yield os.path.join(curr_dir, "test_playmolecule")
    if old_root:
        os.environ["PM_APP_ROOT"] = old_root
    else:
        os.environ.pop("PM_APP_ROOT", None)


def _test_old_playmolecule_manifests():
    os.environ["PM_APP_ROOT"] = os.path.join(curr_dir, "test_playmolecule")

    from playmolecule import apps, datasets, protocols
    import tempfile

    assert hasattr(apps, "proteinprepare")
    assert hasattr(apps.proteinprepare, "files")
    assert hasattr(apps.proteinprepare, "proteinprepare")
    assert hasattr(apps.proteinprepare.v1, "proteinprepare")
    assert hasattr(apps.proteinprepare.v1, "files")
    assert hasattr(apps.proteinprepare.v1.proteinprepare, "tests")
    assert hasattr(apps.proteinprepare.v1.proteinprepare.tests, "simple")
    assert sorted(list(apps.proteinprepare.v1.files.keys())) == sorted(
        [
            "datasets",
            "datasets/3ptb.pdb",
            "tests",
            "tests/web_content.pickle",
            "tests/reprepare.pickle",
            "tests/3ptb.pdb",
            "tests/587HG92V.pdb",
            "tutorials",
            "tutorials/learn_this_app.ipynb",
        ]
    )
    assert hasattr(apps.proteinprepare.v1.datasets, "file_3ptb")
    assert hasattr(datasets, "file_3ptb")
    assert hasattr(protocols, "crypticscout")
    assert hasattr(protocols.crypticscout, "v1")
    assert hasattr(protocols.crypticscout.v1, "crypticscout")
    assert hasattr(protocols.crypticscout.v1.crypticscout, "crypticscout")
    assert callable(protocols.crypticscout.v1.crypticscout.crypticscout)

    expected_files = [
        "run_*.sh",
        "run_*/",
        "run_*/expected_outputs.json",
        "run_*/.pm.done",
        "run_*/.manifest.json",
        os.path.join("run_*", "inputs.json"),
        os.path.join("run_*", "original_paths.json"),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinprepare.proteinprepare(tmpdir, pdbfile=datasets.file_3ptb).run()
        for ef in expected_files:
            assert len(glob(os.path.join(tmpdir, ef))), "could not find " + ef

    expected_files += [os.path.join("run_*", "3ptb.pdb")]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinprepare.proteinprepare(
            tmpdir,
            pdbfile=os.path.join(curr_dir, "test_playmolecule", "datasets", "3ptb.pdb"),
        ).run()
        for ef in expected_files:
            assert len(glob(os.path.join(tmpdir, ef))), "could not find " + ef


def _test_new_playmolecule_manifests():
    os.environ["PM_APP_ROOT"] = os.path.join(curr_dir, "test_playmolecule")

    from playmolecule import apps, datasets
    import tempfile

    assert hasattr(apps, "proteinpreparenew")
    assert hasattr(apps.proteinpreparenew, "proteinpreparenew")
    assert hasattr(apps.proteinpreparenew, "files")
    assert hasattr(apps.proteinpreparenew.v1, "proteinpreparenew")
    assert hasattr(apps.proteinpreparenew.v1, "files")
    assert hasattr(apps.proteinpreparenew.v1.proteinpreparenew, "tests")
    assert hasattr(apps.proteinpreparenew.v1.proteinpreparenew.tests, "simple")
    assert hasattr(apps.proteinpreparenew.v2, "proteinpreparenew")
    assert hasattr(apps.proteinpreparenew.v2, "files")
    assert hasattr(apps.proteinpreparenew.v2.proteinpreparenew, "tests")
    assert hasattr(apps.proteinpreparenew.v2.proteinpreparenew.tests, "simple")
    assert sorted(list(apps.proteinpreparenew.v1.files.keys())) == sorted(
        [
            "datasets",
            "datasets/3ptb.pdb",
            "tests",
            "tests/web_content.pickle",
            "tests/reprepare.pickle",
            "tests/3ptb.pdb",
            "tests/587HG92V.pdb",
            "tutorials",
            "tutorials/learn_this_app.ipynb",
        ]
    )
    assert hasattr(apps.proteinpreparenew.v1.datasets, "file_3ptb")
    assert hasattr(datasets, "file_3ptb")

    expected_files = [
        "run_*.sh",
        "run_*/",
        "run_*/.pm.done",
        "run_*/.manifest.json",
        "run_*/expected_outputs.json",
        os.path.join("run_*", "inputs.json"),
        os.path.join("run_*", "original_paths.json"),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinpreparenew.proteinpreparenew(
            tmpdir, pdbfile=datasets.file_3ptb
        ).run()
        for ef in expected_files:
            assert len(glob(os.path.join(tmpdir, ef))), "could not find " + ef

        with open(glob(os.path.join(tmpdir, "run_*", "inputs.json"))[0], "r") as f:
            inputs = json.load(f)
            assert "function" in inputs
            assert (
                inputs["function"] == "proteinprepare.apps.proteinpreparenew.app.main"
            )

    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinpreparenew.v1.bar(tmpdir, pdbid="3ptb").run()
        for ef in expected_files:
            assert len(glob(os.path.join(tmpdir, ef))), "could not find " + ef

        with open(glob(os.path.join(tmpdir, "run_*", "inputs.json"))[0], "r") as f:
            inputs = json.load(f)
            assert "function" in inputs
            assert inputs["function"] == "proteinprepare.apps.proteinpreparenew.app.bar"

    expected_files += [os.path.join("run_*", "3ptb.pdb")]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinpreparenew.proteinpreparenew(
            tmpdir,
            pdbfile=os.path.join(curr_dir, "test_playmolecule", "datasets", "3ptb.pdb"),
        ).run()
        for ef in expected_files:
            assert len(glob(os.path.join(tmpdir, ef))), "could not find " + ef

    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinpreparenew.proteinpreparenew(
            tmpdir, pdbfile="app://files/datasets/3ptb.pdb"
        ).run()
        assert (
            len(glob(os.path.join(tmpdir, "run_*", "3ptb.pdb"))) == 0
        ), "3ptb file should not be copied since it's a dataset"

        with open(glob(os.path.join(tmpdir, "run_*", "inputs.json"))[0], "r") as f:
            inputs = json.load(f)
            assert "function" in inputs
            assert (
                inputs["function"] == "proteinprepare.apps.proteinpreparenew.app.main"
            )
            assert (
                inputs["arguments"]["pdbfile"]
                == apps.proteinpreparenew.files["datasets/3ptb.pdb"].path
            )


# ============================================================================
# Test _appfiles module
# ============================================================================


def _test_file_class():
    """Test the _File class"""
    from playmolecule._appfiles import _File

    # Test basic file creation
    file = _File("test", "/path/to/file", "Test description")
    assert file.name == "test"
    assert file.path == "/path/to/file"
    assert file.description == "Test description"

    # Test string representation
    assert "[test]" in str(file)
    assert "/path/to/file" in str(file)
    assert "Test description" in str(file)

    # Test file without description
    file_no_desc = _File("test2", "/path/to/file2")
    assert file_no_desc.description is None
    assert "test2" in str(file_no_desc)


def _test_artifacts_class(test_app_root):
    """Test the _Artifacts class"""
    from playmolecule._appfiles import _Artifacts, _File

    files_dict = {
        "datasets/test.pdb": _File("test.pdb", "/path/to/test.pdb"),
        "artifacts/data.txt": _File("data.txt", "/path/to/data.txt"),
    }

    artifacts_list = [
        {"name": "file_test", "path": "test.pdb", "description": "Test file"},
        {"name": "file_data", "path": "data.txt", "description": "Data file"},
    ]

    artifacts = _Artifacts(artifacts_list, files_dict)

    # Test that attributes were created correctly
    assert hasattr(artifacts, "file_test")
    assert hasattr(artifacts, "file_data")

    # Test string representation
    str_repr = str(artifacts)
    assert "file_test" in str_repr
    assert "file_data" in str_repr


def _test_artifacts_validation(test_app_root):
    """Test _Artifacts validation"""
    from playmolecule._appfiles import _Artifacts, _File

    files_dict = {"datasets/test.pdb": _File("test.pdb", "/path/to/test.pdb")}

    # Test that names with dots are rejected
    artifacts_list = [
        {"name": "file.with.dots", "path": "test.pdb", "description": "Test"}
    ]
    artifacts = _Artifacts(artifacts_list, files_dict)
    assert not hasattr(artifacts, "file.with.dots")

    # Test that names starting with numbers are rejected
    artifacts_list = [{"name": "123file", "path": "test.pdb", "description": "Test"}]
    artifacts = _Artifacts(artifacts_list, files_dict)
    assert not hasattr(artifacts, "123file")


def _test_get_app_files(test_app_root):
    """Test _get_app_files function"""
    from playmolecule._appfiles import _get_app_files

    source_dir = os.path.join(test_app_root, "apps", "proteinprepare", "v1", "files")
    files = _get_app_files(source_dir)

    # Check that files were found
    assert isinstance(files, dict)
    assert len(files) > 0

    # Check that keys are relative paths
    for key in files.keys():
        assert not os.path.isabs(key)


# ============================================================================
# Test _protocols module
# ============================================================================


def _test_find_protocols(test_app_root):
    """Test __find_protocols function"""
    from playmolecule._protocols import __find_protocols

    protocols = __find_protocols(test_app_root)
    assert protocols is not None

    # Check that the protocols module was created
    assert hasattr(protocols, "crypticscout")
    assert hasattr(protocols.crypticscout, "v1")


def _test_find_protocols_nonexistent():
    """Test __find_protocols with non-existent directory"""
    from playmolecule._protocols import __find_protocols

    protocols = __find_protocols("/nonexistent/path")
    assert protocols is None


# ============================================================================
# Test _tests module
# ============================================================================


def _test_tests_class(test_app_root):
    """Test _Tests class"""
    os.environ["PM_APP_ROOT"] = test_app_root
    from playmolecule import apps
    from playmolecule._tests import _Tests

    # Get a function with tests
    func = apps.proteinprepare.v1.proteinprepare
    assert hasattr(func, "tests")
    assert hasattr(func.tests, "simple")

    # Test string representation
    tests_str = str(func.tests)
    assert "simple" in tests_str


def _test_test_class_attributes(test_app_root):
    """Test _Test class attributes"""
    os.environ["PM_APP_ROOT"] = test_app_root
    from playmolecule import apps

    func = apps.proteinprepare.v1.proteinprepare
    test = func.tests.simple

    assert hasattr(test, "func")
    assert hasattr(test, "name")
    assert hasattr(test, "config")
    assert callable(test.run)

    # Test string representation
    test_str = str(test)
    assert "Arguments" in test_str
    assert "Expected outputs" in test_str


def _test_convert_test_files(test_app_root):
    """Test _convert_test_files function"""
    from playmolecule._tests import _convert_test_files
    from playmolecule._appfiles import _File

    files = {
        "tests/test.pdb": _File("test.pdb", "/path/to/test.pdb"),
    }

    # Test with test file
    result = _convert_test_files("tests/test.pdb", files)
    assert isinstance(result, _File)
    assert result.path == "/path/to/test.pdb"

    # Test with regular string
    result = _convert_test_files("regular_string", files)
    assert result == "regular_string"


# ============================================================================
# Test apps module - JobStatus
# ============================================================================


def _test_job_status_enum():
    """Test JobStatus enum"""
    from playmolecule import JobStatus

    # Test enum values
    assert JobStatus.WAITING_INFO == 0
    assert JobStatus.RUNNING == 1
    assert JobStatus.COMPLETED == 2
    assert JobStatus.ERROR == 3

    # Test describe method
    assert JobStatus.WAITING_INFO.describe() == "Waiting info"
    assert JobStatus.RUNNING.describe() == "Running"
    assert JobStatus.COMPLETED.describe() == "Completed"
    assert JobStatus.ERROR.describe() == "Error"

    # Test string representation
    assert str(JobStatus.COMPLETED) == "Completed"


# ============================================================================
# Test apps module - ExecutableDirectory
# ============================================================================


def _test_executable_directory_init(test_app_root):
    """Test ExecutableDirectory initialization"""
    from playmolecule import apps
    from playmolecule.apps import ExecutableDirectory

    os.environ["PM_APP_ROOT"] = test_app_root
    from playmolecule import datasets

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an executable directory
        ed = apps.proteinprepare.proteinprepare(tmpdir, pdbfile=datasets.file_3ptb)

        assert ed.dirname == tmpdir
        assert ed.runsh is not None
        assert ed.runsh.endswith(".sh")
        assert ed.inputs_dir is not None


def _test_executable_directory_status_completed(test_app_root):
    """Test ExecutableDirectory status with completed job"""
    from playmolecule import apps, JobStatus

    os.environ["PM_APP_ROOT"] = test_app_root
    from playmolecule import datasets

    with tempfile.TemporaryDirectory() as tmpdir:
        ed = apps.proteinprepare.proteinprepare(tmpdir, pdbfile=datasets.file_3ptb)
        ed.run()

        # Check status after completion
        assert ed.status == JobStatus.COMPLETED


def _test_executable_directory_status_error():
    """Test ExecutableDirectory status detection for errors"""
    from playmolecule.apps import ExecutableDirectory, JobStatus

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a fake run script
        runsh = os.path.join(tmpdir, "run_test.sh")
        with open(runsh, "w") as f:
            f.write("#!/bin/bash\n")

        inputs_dir = os.path.join(tmpdir, "run_test")
        os.makedirs(inputs_dir, exist_ok=True)

        # Create error marker
        with open(os.path.join(inputs_dir, ".pm.err"), "w") as f:
            f.write("")

        ed = ExecutableDirectory(tmpdir, inputs_dir=inputs_dir)
        assert ed.status == JobStatus.ERROR


# ============================================================================
# Test apps module - function creation and validation
# ============================================================================


def _test_validators():
    """Test type validators"""
    from playmolecule.apps import _validators
    from pathlib import Path
    from playmolecule._appfiles import _File

    # Test str validator
    assert isinstance("test", _validators["str"])

    # Test Path validator
    assert isinstance("/path/to/file", _validators["Path"])
    assert isinstance(Path("/path"), _validators["Path"])
    assert isinstance(_File("test", "/path"), _validators["Path"])

    # Test bool validator
    assert isinstance(True, _validators["bool"])

    # Test int validator
    assert isinstance(1, _validators["int"])
    assert isinstance(1.0, _validators["int"])

    # Test float validator
    assert isinstance(1.0, _validators["float"])

    # Test dict validator
    assert isinstance({}, _validators["dict"])


def _test_write_inputs(test_app_root):
    """Test _write_inputs function"""
    from playmolecule.apps import _write_inputs
    from playmolecule._appfiles import _get_app_files

    os.environ["PM_APP_ROOT"] = test_app_root

    with tempfile.TemporaryDirectory() as tmpdir:
        inputdir = os.path.join(tmpdir, "run_test")

        # Simple manifest for testing
        manifest = {
            "params": [
                {"name": "outdir", "type": "str"},
                {"name": "value", "type": "int"},
            ],
            "outputs": {"output.txt": "Test output"},
        }

        arguments = {"outdir": ".", "value": 42}
        app_files = {}

        _write_inputs(
            tmpdir,
            inputdir,
            arguments,
            manifest,
            app_files,
            "test.func",
            "test.v1.func",
        )

        # Check that files were created
        assert os.path.exists(os.path.join(inputdir, "inputs.json"))
        assert os.path.exists(os.path.join(inputdir, "expected_outputs.json"))
        assert os.path.exists(os.path.join(inputdir, "original_paths.json"))
        assert os.path.exists(os.path.join(inputdir, ".manifest.json"))

        # Check inputs.json content
        with open(os.path.join(inputdir, "inputs.json"), "r") as f:
            inputs = json.load(f)
            assert inputs["function"] == "test.func"
            assert inputs["arguments"]["value"] == 42


def _test_args_from_manifest():
    """Test _args_from_manifest function"""
    from playmolecule.apps import _args_from_manifest

    # Test mandatory parameters
    func_args = [
        {"name": "param1", "type": "str", "mandatory": True},
        {"name": "param2", "type": "int", "value": 10, "mandatory": False},
    ]

    args = _args_from_manifest(func_args)
    assert len(args) == 2
    assert "param1 : str," in args[0]
    assert "param2 : int = 10" in args[1]


def _test_docs_from_manifest():
    """Test _docs_from_manifest function"""
    from playmolecule.apps import _docs_from_manifest

    manifest = {
        "description": "Test app description",
        "params": [
            {"name": "input", "type": "Path", "description": "Input file"},
            {"name": "output", "type": "str", "description": "Output file"},
        ],
        "outputs": {"result.txt": "Result file"},
        "resources": {"ncpu": 1, "ngpu": 0},
    }

    docs = _docs_from_manifest(manifest, "testapp", None)

    assert len(docs) > 0
    assert "Test app description" in docs
    assert "Parameters" in docs
    assert "Outputs" in docs
    assert "Note" in docs


def _test_check_folder_validity():
    """Test _check_folder_validity function"""
    from playmolecule.apps import _check_folder_validity

    root = "/home/test"

    # Valid folder names
    assert _check_folder_validity(root, "/home/test/app_name")
    assert _check_folder_validity(root, "/home/test/app123")
    assert _check_folder_validity(root, "/home/test/my_app")

    # Invalid folder names
    assert not _check_folder_validity(root, "/home/test/App-Name")
    assert not _check_folder_validity(root, "/home/test/app.name")
    assert not _check_folder_validity(root, "/home/test/app name")


# ============================================================================
# Test _devutils module
# ============================================================================


def _test_ensurelist():
    """Test ensurelist function"""
    from playmolecule._devutils import ensurelist

    # Test with list
    assert ensurelist([1, 2, 3]) == [1, 2, 3]

    # Test with tuple
    assert ensurelist((1, 2, 3)) == (1, 2, 3)

    # Test with scalar
    assert ensurelist(1) == [1]

    # Test with string
    assert ensurelist("test") == ["test"]

    # Test with range
    assert ensurelist(range(3)) == [0, 1, 2]


def _test_ensurelist_with_tomod():
    """Test ensurelist with separate check and modification values"""
    from playmolecule._devutils import ensurelist

    # Test with tocheck as list, tomod as different value
    result = ensurelist([1, 2], "value")
    assert result == "value"

    # Test with tocheck as scalar, tomod as different value
    result = ensurelist(1, "value")
    assert result == ["value"]


def _test_report_alive():
    """Test report_alive function runs in thread"""
    from playmolecule._devutils import report_alive
    import threading
    import time

    with tempfile.TemporaryDirectory() as tmpdir:
        inputs_dir = os.path.join(tmpdir, "test_sentinel")

        # Start the thread
        thread = threading.Thread(target=report_alive, args=(inputs_dir,), daemon=True)
        thread.start()

        # Give it a moment to write the file
        time.sleep(0.5)

        # Check that the alive file was created
        assert os.path.exists(os.path.join(inputs_dir, ".pm.alive"))

        # Read the file and verify it contains a timestamp
        with open(os.path.join(inputs_dir, ".pm.alive"), "r") as f:
            content = f.read()
            assert len(content) > 0


def _test_dump_manifest(test_app_root):
    """Test dump_manifest function"""
    from playmolecule._devutils import dump_manifest

    os.environ["PM_APP_ROOT"] = test_app_root
    # Need to import apps after setting the environment variable
    from playmolecule import apps

    with tempfile.TemporaryDirectory() as tmpdir:
        outfile = os.path.join(tmpdir, "manifest.json")

        # This should work with the test apps
        dump_manifest("playmolecule.apps.proteinprepare.v1", outfile)

        assert os.path.exists(outfile)

        with open(outfile, "r") as f:
            manifest = json.load(f)
            assert "functions" in manifest


# ============================================================================
# Test main module integration
# ============================================================================


def _test_describe_apps(test_app_root, capsys):
    """Test describe_apps function"""
    os.environ["PM_APP_ROOT"] = test_app_root

    # Need to reload the module to pick up the new PM_APP_ROOT
    if "playmolecule" in sys.modules:
        del sys.modules["playmolecule"]
    if "playmolecule.apps" in sys.modules:
        del sys.modules["playmolecule.apps"]

    from playmolecule import describe_apps

    describe_apps()
    captured = capsys.readouterr()

    # Check that output was produced
    assert len(captured.out) > 0


def _test_version():
    """Test version import"""
    from playmolecule import __version__

    # Version should be set (either from package or not set)
    assert __version__ is not None or __version__ == "__version"


def _test_pm_skip_setup():
    """Test PM_SKIP_SETUP environment variable"""
    old_skip = os.environ.get("PM_SKIP_SETUP")
    old_root = os.environ.get("PM_APP_ROOT")

    try:
        os.environ["PM_SKIP_SETUP"] = "1"
        if "PM_APP_ROOT" in os.environ:
            del os.environ["PM_APP_ROOT"]

        # Need to reload the module
        if "playmolecule" in sys.modules:
            del sys.modules["playmolecule"]

        # This should not raise an error even without PM_APP_ROOT
        import playmolecule

        assert playmolecule.PM_SKIP_SETUP

    finally:
        if old_skip:
            os.environ["PM_SKIP_SETUP"] = old_skip
        else:
            os.environ.pop("PM_SKIP_SETUP", None)

        if old_root:
            os.environ["PM_APP_ROOT"] = old_root


# ============================================================================
# Test KWARGS class
# ============================================================================


def _test_kwargs_class():
    """Test KWARGS class"""
    from playmolecule.apps import KWARGS

    kwargs = KWARGS({"a": 1, "b": 2})
    assert isinstance(kwargs, dict)
    assert kwargs["a"] == 1
    assert kwargs["b"] == 2


# ============================================================================
# Test error handling
# ============================================================================


def _test_write_inputs_type_validation():
    """Test type validation in _write_inputs"""
    from playmolecule.apps import _write_inputs

    with tempfile.TemporaryDirectory() as tmpdir:
        inputdir = os.path.join(tmpdir, "run_test")

        manifest = {
            "params": [
                {"name": "value", "type": "int"},
            ],
        }

        # Pass wrong type
        arguments = {"value": "not_an_int"}
        app_files = {}

        with pytest.raises(RuntimeError, match="Was expecting value of type"):
            _write_inputs(
                tmpdir,
                inputdir,
                arguments,
                manifest,
                app_files,
                "test.func",
                "test.v1.func",
            )


def _test_write_inputs_nargs_validation():
    """Test nargs validation in _write_inputs"""
    from playmolecule.apps import _write_inputs

    with tempfile.TemporaryDirectory() as tmpdir:
        inputdir = os.path.join(tmpdir, "run_test")

        manifest = {
            "params": [
                {"name": "value", "type": "int", "nargs": None},
            ],
        }

        # Pass list when single value expected
        arguments = {"value": [1, 2, 3]}
        app_files = {}

        with pytest.raises(RuntimeError, match="Was expecting a single value"):
            _write_inputs(
                tmpdir,
                inputdir,
                arguments,
                manifest,
                app_files,
                "test.func",
                "test.v1.func",
            )


def _test_sleep_exception():
    """Test SleepException"""
    from playmolecule._devutils import SleepException

    with pytest.raises(SleepException):
        raise SleepException("Test exception")


# ============================================================================
# Test path handling
# ============================================================================


def _test_path_copying_in_write_inputs(test_app_root):
    """Test that Path-type arguments are copied correctly"""
    from playmolecule.apps import _write_inputs

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = os.path.join(tmpdir, "input.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        inputdir = os.path.join(tmpdir, "run_test")

        manifest = {
            "params": [
                {"name": "inputfile", "type": "Path"},
            ],
        }

        arguments = {"inputfile": test_file}
        app_files = {}

        _write_inputs(
            tmpdir,
            inputdir,
            arguments,
            manifest,
            app_files,
            "test.func",
            "test.v1.func",
        )

        # Check that the file was copied
        copied_file = os.path.join(inputdir, "input.txt")
        assert os.path.exists(copied_file)

        # Check original_paths.json
        with open(os.path.join(inputdir, "original_paths.json"), "r") as f:
            orig_paths = json.load(f)
            assert test_file in orig_paths.values()


def _test_app_files_uri_handling():
    """Test handling of app://files URIs"""
    from playmolecule.apps import _write_inputs
    from playmolecule._appfiles import _File

    with tempfile.TemporaryDirectory() as tmpdir:
        inputdir = os.path.join(tmpdir, "run_test")

        manifest = {
            "params": [
                {"name": "datafile", "type": "Path"},
            ],
        }

        app_files = {
            "datasets/test.pdb": _File("test.pdb", "/actual/path/test.pdb"),
        }

        arguments = {"datafile": "app://files/datasets/test.pdb"}

        _write_inputs(
            tmpdir,
            inputdir,
            arguments,
            manifest,
            app_files,
            "test.func",
            "test.v1.func",
        )

        # Check that the URI was resolved
        with open(os.path.join(inputdir, "inputs.json"), "r") as f:
            inputs = json.load(f)
            # The app://files URI should be resolved to the actual path
            assert inputs["arguments"]["datafile"] == "/actual/path/test.pdb"

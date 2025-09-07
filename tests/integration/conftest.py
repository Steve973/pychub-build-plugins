from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import venv
import zipfile
from pathlib import Path

import pytest
from pychub.model.chubconfig_model import ChubConfig

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


def bash_setup_script(backend: str, root_dir: Path, activate: Path):
    return f"""
#!/usr/bin/env bash
set -euo pipefail

# Activate the temporary test venv
source "{activate}"

pip install --upgrade pip poetry build
if [ "pdm" == "{backend}" ]; then
  pip install "pdm==2.25.4" pdm-backend
elif [ "hatch" == "{backend}" ]; then
  pip install {backend} hatchling
fi
poetry install --directory "{root_dir}"
if [ "pdm" == "{backend}" ]; then
  poetry run {backend} build --no-isolation -v
elif [ "hatch" == "{backend}" ]; then
  poetry run python -m build --no-isolation -w
else
  poetry run {backend} build
fi
"""


@pytest.fixture(scope="function")
def test_env(request):
    """
    Create a clean venv, install monorepo root, and build the given backend test project
    in a copied tempdir. request.param should be one of: "poetry", "hatch", "pdm".
    """
    root_dir = Path(__file__).resolve().parents[2]
    backend = request.param
    src_proj_dir = root_dir / "tests" / "integration" / backend / "test_proj"
    print(f"[pychub-build-plugins] Running test with param: {backend}, root: {root_dir}, proj: {src_proj_dir}")

    temp_dir = Path(tempfile.mkdtemp(prefix=f"integration-{backend}-"))
    venv_dir = temp_dir / "venv"
    venv.create(venv_dir, with_pip=True)

    # copy the test project into the tempdir
    build_proj_dir = temp_dir / "test_proj"
    shutil.copytree(src_proj_dir, build_proj_dir)

    setup_script = bash_setup_script(backend, root_dir, venv_dir / "bin" / "activate")

    # run all steps in a single shell process
    subprocess.run(setup_script, shell=True, check=True, cwd=build_proj_dir, executable="/bin/bash")

    dist_dir = build_proj_dir / "dist"
    wheels = list(dist_dir.glob("*.whl"))
    assert wheels, f"No wheel built for {backend}"

    chub_build_dir = dist_dir / "chub-build"
    chubs = list(chub_build_dir.glob("*.chub"))
    assert chubs, f"No .chub file found for {backend}"

    yield {
        "temp_dir": temp_dir,
        "venv_dir": venv_dir,
        "python_bin": venv_dir / "bin" / "python",
        "root_dir": root_dir,
        "build_proj_dir": build_proj_dir,
        "wheel_path": wheels[0],
        "chub_path": chubs[0]
    }

    shutil.rmtree(temp_dir)


def get_chub_contents(chub_path: Path) -> tuple[list[str] | [], ChubConfig | None]:
    """Return (names, ChubConfig instance) from the built .chub archive."""

    with zipfile.ZipFile(chub_path, "r") as zf:
        names = zf.namelist()
        text = None
        for name in names:
            if name.endswith(".chubconfig"):
                with zf.open(name) as f:
                    text = f.read().decode("utf-8")
                break
        if text is None:
            return names, None
        cfg = ChubConfig.from_yaml(text)
        return names, cfg


def verify_chub_matches_config(chub_file: Path):
    assert chub_file.exists(), f"Chub file not found: {chub_file}"
    assert zipfile.is_zipfile(chub_file), "Not a valid zip file"

    names, chubconfig = get_chub_contents(chub_file)

    # Validate wheel
    for wheel in chubconfig.wheels:
        expected_wheel = Path(wheel).name
        assert f"libs/{expected_wheel}" in names, f"Expected wheel {wheel} not found in zip file"

    # Validate scripts
    for post_script_entry in chubconfig.scripts.post or []:
        post_script_name = Path(post_script_entry).name
        assert any(
            post_script_name in name for name in names),\
            f"Expected script {post_script_name} not found in zip file"
    for pre_script_entry in chubconfig.scripts.pre or []:
        pre_script_name = Path(pre_script_entry).name
        assert any(
            pre_script_name in name for name in names),\
            f"Expected script {pre_script_name} not found in zip file"

    # Validate includes
    for incl_exp in chubconfig.includes:
        incl_src, incl_dest = incl_exp.split("::") if "::" in incl_exp else (incl_exp, Path(incl_exp).name)
        chub_incl_dest = incl_dest
        if incl_dest.endswith("/"):
            chub_incl_dest = f"{incl_dest}{Path(incl_src).name}"
        assert any(
            chub_incl_dest in name for name in names),\
            f"Expected include {incl_exp} (as {chub_incl_dest}) not found in zip file"

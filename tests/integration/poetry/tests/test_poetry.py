from pathlib import Path

import pytest

from tests.integration.conftest import verify_chub_matches_config


@pytest.mark.parametrize("test_env", ["poetry"], indirect=True)
def test_poetry_chub_build(test_env):
    chub = test_env["chub_path"]
    assert Path(chub).is_file(), "No .chub file found"
    verify_chub_matches_config(chub)

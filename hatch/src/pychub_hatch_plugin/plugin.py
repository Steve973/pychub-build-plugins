from pathlib import Path
import os
from contextlib import contextmanager
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

@contextmanager
def pushd(p: Path):
    old = os.getcwd(); os.chdir(p)
    try: yield
    finally: os.chdir(old)

class PychubBuildHook(BuildHookInterface):
    PLUGIN_NAME = "pychub"

    def finalize(self, version: str, build_data: dict, artifact_path: str) -> None:
        if not artifact_path.endswith(".whl"):
            return
        root = Path(self.root).resolve()
        with pushd(root):
            from pychub.package.bt_options_processor import process_chubproject
            process_chubproject(root / "pyproject.toml")

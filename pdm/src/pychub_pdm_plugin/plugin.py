import os
from pathlib import Path
from pychub.package.bt_options_processor import process_chubproject
try:
    # Python 3.11+
    from contextlib import chdir
except Exception:
    # Fallback for <3.11
    from contextlib import contextmanager
    @contextmanager
    def chdir(path: Path):
        old = os.getcwd()
        os.chdir(path)
        try:
            yield
        finally:
            os.chdir(old)


class PychubBuildHook:
    def pdm_build_hook_enabled(self, context):
        return context.target == "wheel"

    def pdm_build_finalize(self, context, artifact):
        artifact = Path(artifact).resolve()
        project_root = artifact.parents[2].resolve()
        for p in artifact.parents:
            if p.name == "dist":
                root = p.parent
                if (root / "pyproject.toml").exists():
                    project_root = root
        config_path = project_root / "pyproject.toml"
        print(f"[pychub-pdm-plugin] finalize on {artifact} with config path: {config_path}")
        with chdir(project_root):
            process_chubproject(config_path)
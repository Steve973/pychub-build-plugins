# pkg/hooks.py
from hatchling.plugin import hookimpl
from .plugin import PychubBuildHook

@hookimpl
def hatch_register_build_hook():
    return PychubBuildHook

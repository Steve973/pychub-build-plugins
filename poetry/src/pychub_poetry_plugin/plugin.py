from pathlib import Path

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND, TERMINATE
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin
from pychub.package.bt_options_processor import process_chubproject


class PychubPoetryPlugin(ApplicationPlugin):

    def __init__(self):
        # This flag tracks whether we're building
        self._is_build_command = False

    def on_command(self, event: Event, _str: str, _evd: EventDispatcher):
        if isinstance(event, ConsoleCommandEvent):
            command = event.command
            if command.name == "build":
                print("[pychub-poetry-plugin] Detected build command: enabling pychub build")
                self._is_build_command = True
            else:
                self._is_build_command = False

    def on_terminate(self, _evt: Event, _str: str, _evd: EventDispatcher):
        if self._is_build_command:
            config_path = Path.cwd() / "pyproject.toml"
            print(f"[pychub-poetry-plugin] Running pychub with {config_path}")
            process_chubproject(config_path)

    def activate(self, application: Application):
        application.event_dispatcher.add_listener(COMMAND, self.on_command)
        application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

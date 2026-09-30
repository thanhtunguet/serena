import shutil
from typing import TYPE_CHECKING

from serena.jetbrains import launch_coordinator
from serena.jetbrains.jetbrains_backend import JetBrainsLanguageBackend
from serena.language_backend import BuiltinLanguageBackend

if TYPE_CHECKING:
    from serena.agent import SerenaAgent
    from serena.repl.facade import ApiScope, Facade


class OraiosJVMLanguageBackend(JetBrainsLanguageBackend):
    """
    The Oraios Language Backend (OLB) for JVM-based languages (Java, Kotlin, Groovy).
    This is a drop-in replacement for the JetBrains backend.
    """

    def __init__(self):
        super().__init__(key=BuiltinLanguageBackend.OLB_JVM.value)

    def _create_ide_facade(self, agent: "SerenaAgent", api_scope: "ApiScope") -> "Facade":
        facade = super()._create_ide_facade(agent, api_scope)
        facade.set_name("ide")
        facade.set_description(facade.description.replace("JetBrains", "Oraios"))
        return facade

    def is_jetbrains(self):
        # TODO: For the time being, this backend shall be treated the same as the JetBrains backend.
        #  Ultimately, we'll want to remove this method altogether.
        return True

    @staticmethod
    def _check_olb_installed():
        """Checks whether the Oraios Language Backend (olb) CLI tool is available, raising an exception if not."""
        if shutil.which("olb") is None:
            raise Exception(
                "The Oraios Language Backend CLI (olb) was not found on the PATH. "
                "Install it via `uv tool install olb-cli` and then install the JVM language backend via `olb install jvm`."
            )

    def _init_project_ide_launch(self, agent: "SerenaAgent") -> None:
        self._check_olb_installed()
        project = agent.get_active_project_or_raise()
        launch_command = ["olb", "start", "jvm"]
        launch_coordinator.launch_and_wait_for_plugin_server(project, launch_command)

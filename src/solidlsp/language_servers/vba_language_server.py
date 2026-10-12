"""SolidLSP adapter for the standalone VBA language server."""

import os
import shutil
from pathlib import Path

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig, LanguageServerId
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class VbaLanguageServer(SolidLanguageServer):
    """Launches SSlinky/VBA-LanguageServer over stdio."""

    def __init__(self, config: LanguageServerConfig, repository_root_path: str, solidlsp_settings: SolidLSPSettings):
        custom_settings = solidlsp_settings.get_ls_specific_settings(LanguageServerId.VBA)
        configured_path = os.environ.get("VBA_LS_PATH") or custom_settings.get("vba_ls_path")
        server_path = Path(os.path.expanduser(configured_path or "~/.local/src/VBA-LanguageServer/dist/server/out/server.js"))
        if not server_path.is_file():
            raise FileNotFoundError(
                f"VBA language server bundle not found at {server_path}; build VBA-LanguageServer or set ls_specific_settings.vba.vba_ls_path"
            )

        node_executable = custom_settings.get("node_path") or shutil.which("node")
        if not node_executable:
            raise FileNotFoundError("Node.js was not found; install Node.js or set ls_specific_settings.vba.node_path")

        process_launch_info = ProcessLaunchInfo(cmd=[node_executable, str(server_path), "--stdio"], cwd=repository_root_path)
        super().__init__(
            config,
            repository_root_path,
            process_launch_info=process_launch_info,
            language_id="vba",
            solidlsp_settings=solidlsp_settings,
        )

    def _create_base_initialize_params(self) -> dict:
        return {
            "capabilities": {
                "textDocument": {
                    "synchronization": {"dynamicRegistration": True},
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "definition": {"dynamicRegistration": True},
                },
                "workspace": {"configuration": True, "workspaceFolders": True},
            }
        }

    def _start_server(self) -> None:
        def acknowledge_request(_params: dict) -> None:
            return

        def get_workspace_configuration(params: dict) -> list:
            return [None] * len(params.get("items", []))

        self.server.on_request("client/registerCapability", acknowledge_request)
        self.server.on_request("client/unregisterCapability", acknowledge_request)
        self.server.on_request("workspace/configuration", get_workspace_configuration)

        def ignore_notification(_params: dict) -> None:
            return

        self.server.on_notification("window/logMessage", ignore_notification)
        self.server.on_notification("textDocument/publishDiagnostics", acknowledge_request)
        self.server.start()
        self.server.send.initialize(self._create_initialize_params())
        self.server.notify.initialized({})

"""SolidLSP adapter for the standalone VB.NET language server."""

import os
import shutil
from pathlib import Path

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig, LanguageServerId
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class VbNetLanguageServer(SolidLanguageServer):
    """Launches DNAKode's VB.NET language server over stdio."""

    def __init__(self, config: LanguageServerConfig, repository_root_path: str, solidlsp_settings: SolidLSPSettings):
        custom_settings = solidlsp_settings.get_ls_specific_settings(LanguageServerId.VBNET)
        executable = self._resolve_executable(custom_settings.get("vbnet_ls_path"))
        process_launch_info = ProcessLaunchInfo(cmd=[executable, "--stdio"], cwd=repository_root_path)
        super().__init__(
            config,
            repository_root_path,
            process_launch_info=process_launch_info,
            language_id="vb",
            solidlsp_settings=solidlsp_settings,
        )

    def _create_base_initialize_params(self) -> dict:
        return {
            "capabilities": {
                "textDocument": {
                    "synchronization": {"dynamicRegistration": True},
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                },
                "workspace": {"configuration": True, "workspaceFolders": True},
            }
        }

    def _start_server(self) -> None:
        self.server.start()
        self.server.send.initialize(self._create_initialize_params())
        self.server.notify.initialized({})

    @staticmethod
    def _resolve_executable(configured_path: str | None) -> str:
        if configured_path:
            return os.path.expanduser(configured_path)

        executable = shutil.which("vbnet-ls")
        if executable:
            return executable

        tool_names = ("vbnet-ls", "vbnet-ls.exe")
        for tool_name in tool_names:
            candidate = Path.home() / ".dotnet" / "tools" / tool_name
            if candidate.is_file():
                return str(candidate)

        raise FileNotFoundError("vbnet-ls was not found; install DNAKode.VbNet.Lsp or set ls_specific_settings.vbnet.vbnet_ls_path")

from pathlib import Path

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import LanguageServerId
from test.solidlsp.conftest import document_symbol_names


@pytest.mark.vba
class TestVbaLanguageServer:
    @pytest.mark.parametrize("language_server", [LanguageServerId.VBA], indirect=True)
    @pytest.mark.parametrize("repo_path", [LanguageServerId.VBA], indirect=True)
    def test_bas_module_symbols(self, language_server: SolidLanguageServer, repo_path: Path) -> None:
        assert "SmokeTest" in document_symbol_names(language_server, "Module.bas")

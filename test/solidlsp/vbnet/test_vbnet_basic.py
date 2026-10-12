from pathlib import Path

import pytest

from solidlsp import SolidLanguageServer
from solidlsp.ls_config import LanguageServerId
from test.conftest import find_identifier_position
from test.solidlsp.conftest import document_symbol_names


@pytest.mark.vbnet
class TestVbNetLanguageServer:
    @pytest.mark.parametrize("language_server", [LanguageServerId.VBNET], indirect=True)
    @pytest.mark.parametrize("repo_path", [LanguageServerId.VBNET], indirect=True)
    def test_symbols_and_cross_file_definition(self, language_server: SolidLanguageServer, repo_path: Path) -> None:
        greeter_symbols = document_symbol_names(language_server, "Greeter.vb")
        assert "Greeter" in greeter_symbols
        assert "Greet" in greeter_symbols

        program_file = repo_path / "Program.vb"
        position = find_identifier_position(program_file, "Greet")
        assert position is not None
        definitions = language_server.request_definition(str(program_file), *position)
        assert definitions
        assert any(location["uri"].endswith("Greeter.vb") for location in definitions)

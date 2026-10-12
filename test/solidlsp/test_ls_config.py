import pytest

from solidlsp.ls_config import FilenameMatcher, LanguageServerId, LegacyPathEncodingResolver


class TestFilenameMatcherCaseSensitivity:
    """Regression tests for FilenameMatcher case-sensitivity handling.

    ``is_relevant_filename`` and ``string_contains_relevant_filename`` must apply the same
    case-folding rule: fold to lower case only when ``case_sensitive=False``. A previously inverted
    check in ``string_contains_relevant_filename`` folded the input when ``case_sensitive=True``
    (and left it unfolded when ``case_sensitive=False``), so both modes could mismatch.
    """

    def test_case_insensitive_matches_uppercase_input(self) -> None:
        matcher = FilenameMatcher(".py", ".pyi", case_sensitive=False)
        # Uppercase / mixed-case input must match a lower-case extension when case-insensitive.
        assert matcher.is_relevant_filename("FOO.PY")
        assert matcher.is_relevant_filename("Foo.PyI")
        assert matcher.string_contains_relevant_filename("opened FOO.PY for editing")
        assert matcher.string_contains_relevant_filename("see Foo.PyI:10")

    def test_case_sensitive_respects_extension_case(self) -> None:
        # R uses case-significant extensions: .R and .r are distinct.
        matcher = FilenameMatcher(".R", case_sensitive=True)
        assert matcher.is_relevant_filename("script.R")
        assert not matcher.is_relevant_filename("script.r")
        # The same must hold for the substring variant (previously inverted).
        assert matcher.string_contains_relevant_filename("edited script.R just now")
        assert not matcher.string_contains_relevant_filename("edited script.r just now")

    def test_two_methods_agree_on_case_folding(self) -> None:
        """The two matcher methods must never disagree on a filename that ends the string."""
        for case_sensitive in (True, False):
            for extensions in ((".py",), (".R", ".Rmd"), (".ts", ".tsx")):
                matcher = FilenameMatcher(*extensions, case_sensitive=case_sensitive)
                for candidate in ("main.py", "Main.PY", "app.R", "app.r", "x.ts", "X.TSX"):
                    assert matcher.is_relevant_filename(candidate) == matcher.string_contains_relevant_filename(candidate), (
                        f"disagreement for {candidate!r} with extensions={extensions} case_sensitive={case_sensitive}"
                    )

    def test_string_contains_requires_complete_extension(self) -> None:
        """A registered extension must be a *complete* extension, not a prefix of a longer word."""
        matcher = FilenameMatcher(".py", case_sensitive=False)
        assert matcher.string_contains_relevant_filename("run main.py now")
        assert matcher.string_contains_relevant_filename("main.py")
        # ".py" embedded in ".python" is not a complete extension occurrence.
        assert not matcher.string_contains_relevant_filename("file.python")


class TestVbNetLanguageServerConfig:
    def test_vb_files_route_to_vbnet(self) -> None:
        language_server = LanguageServerId.VBNET

        assert language_server.get_source_fn_matcher().is_relevant_filename("Program.vb")
        assert not language_server.get_source_fn_matcher().is_relevant_filename("Program.vbproj")

    def test_vbnet_server_is_registered(self) -> None:
        from solidlsp.language_servers.vbnet_language_server import VbNetLanguageServer

        assert LanguageServerId.VBNET.get_ls_class() is VbNetLanguageServer


class TestVbaLanguageServerConfig:
    def test_vba_files_route_to_vba(self) -> None:
        matcher = LanguageServerId.VBA.get_source_fn_matcher()

        assert matcher.is_relevant_filename("Module.bas")
        assert matcher.is_relevant_filename("Class.cls")
        assert matcher.is_relevant_filename("Form.frm")
        assert matcher.is_relevant_filename("MODULE.BAS")
        assert not matcher.is_relevant_filename("Module.vb")

    def test_vba_server_is_registered(self) -> None:
        from solidlsp.language_servers.vba_language_server import VbaLanguageServer

        assert LanguageServerId.VBA.get_ls_class() is VbaLanguageServer


class TestLegacyPathEncodingResolver:
    def test_resolve_uses_first_matching_glob_rule(self) -> None:
        resolver = LegacyPathEncodingResolver(
            default_encoding="utf-8",
            legacy_encodings=[
                {"*.vb": "cp932"},
                {"*.vb": "latin-1"},
            ],
        )

        assert resolver.resolve("legacy/module.vb") == "cp932"
        assert resolver.resolve("legacy/module.py") == "utf-8"

    def test_resolve_supports_regex_rules_with_prefix(self) -> None:
        resolver = LegacyPathEncodingResolver(
            default_encoding="utf-8",
            legacy_encodings=[
                {"re:^legacy/jp/.*\.txt$": "cp932"},
            ],
        )

        assert resolver.resolve("legacy/jp/readme.txt") == "cp932"
        assert resolver.resolve("legacy/us/readme.txt") == "utf-8"

    def test_invalid_encoding_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown text encoding"):
            LegacyPathEncodingResolver(default_encoding="utf-8", legacy_encodings=[{"*.vb": "no_such_encoding"}])

    def test_invalid_regex_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid regex"):
            LegacyPathEncodingResolver(default_encoding="utf-8", legacy_encodings=[{"re:*bad": "cp932"}])

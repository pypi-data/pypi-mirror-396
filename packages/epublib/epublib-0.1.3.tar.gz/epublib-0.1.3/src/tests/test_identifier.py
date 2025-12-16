from typing import final

import pytest

from epublib.identifier import EPUBId


@final
class TestIdentifier:
    def test_valid_identifiers(self) -> None:
        valid_identifiers = [
            "variable",
            "_privateVar",
            "var123",
            "var_name",
            "VarName",
            "varName2",
            "chapter1",
            "café",
            "_начало",
            "章节1",
        ]
        for identifier in valid_identifiers:
            assert EPUBId(identifier).valid

        invalid_identifiers = [
            "123start",
            "-var-name",
            "var name",
            "var$name",
            "",
            " ",
            ".varname",
            "var@name",
            "var#name",
            "var%name",
            "var	name",
        ]
        for identifier in invalid_identifiers:
            assert not EPUBId(identifier).valid

    def test_identifier_to_valid(self) -> None:
        assert EPUBId.to_valid("validName") == "validName"
        assert EPUBId.to_valid("3validName") == "_validName"
        assert EPUBId.to_valid("valid@Name") == "valid_Name"

        with pytest.raises(ValueError):
            __ = EPUBId.to_valid("")

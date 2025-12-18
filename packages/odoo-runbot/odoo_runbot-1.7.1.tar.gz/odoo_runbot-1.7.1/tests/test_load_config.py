import dataclasses
import pathlib
import sys
import unittest
from typing import Literal

from odoo_runbot.runbot_config import RunbotExcludeWarning, RunbotToolConfig

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from . import config_tester


class TestConfigLoader(unittest.TestCase):
    maxDiff = None
    F_FTYPE = Literal["pyproject", "custom"]

    def assertConfigEqual(self, config: RunbotToolConfig, config_expected: RunbotToolConfig):  # noqa : N802
        self.assertDictEqual(dataclasses.asdict(config), dataclasses.asdict(config_expected))

    def sample_config(self, fname: str, f_type: F_FTYPE) -> RunbotToolConfig:
        path = pathlib.Path(__file__).resolve().parent.joinpath("sample_config", f"{f_type}_{fname}")
        with path.open(mode="rb") as pyproject_toml:
            data = tomllib.load(pyproject_toml)
        if f_type == "pyproject":
            return RunbotToolConfig.load_from_toml_data(data.get("tool", {}).get("runbot"), config_file=path)
        return RunbotToolConfig.load_from_toml_data(data, config_file=path)

    def test_minimal_config(self):
        """[tool.runbot]
        modules = ["module_to_test"]
        """
        self.assertConfigEqual(
            self.sample_config("minimal.toml", "pyproject"), self.sample_config("minimal.toml", "custom")
        )
        self.assertConfigEqual(self.sample_config("minimal.toml", "pyproject"), config_tester.minimal_config_test())
        self.assertConfigEqual(self.sample_config("minimal.toml", "custom"), config_tester.minimal_config_test())

    def test_minimal_file_config(self):
        """[tool.runbot]
        modules = ["module_to_test"]
        """
        self.assertConfigEqual(
            self.sample_config("module.file.toml", "pyproject"), self.sample_config("module.file.toml", "custom")
        )

        self.assertConfigEqual(
            self.sample_config("module.file.toml", "pyproject"), config_tester.classic_file_config_test()
        )
        self.assertConfigEqual(
            self.sample_config("module.file.toml", "custom"), config_tester.classic_file_config_test()
        )

    def test_pyproject_classic(self):
        self.assertConfigEqual(
            self.sample_config("classic.toml", "pyproject"), self.sample_config("classic.toml", "custom")
        )
        self.assertConfigEqual(
            self.sample_config("classic.full.toml", "pyproject"), self.sample_config("classic.full.toml", "custom")
        )
        self.assertConfigEqual(
            self.sample_config("classic.toml", "pyproject"), self.sample_config("classic.full.toml", "pyproject")
        )

        self.assertConfigEqual(
            self.sample_config("classic.toml", "custom"), self.sample_config("classic.full.toml", "custom")
        )
        self.assertConfigEqual(
            self.sample_config("classic.full.toml", "pyproject"), config_tester.pyproject_classic_test()
        )
        self.assertConfigEqual(self.sample_config("classic.toml", "pyproject"), config_tester.pyproject_classic_test())
        self.assertConfigEqual(self.sample_config("classic.toml", "custom"), config_tester.pyproject_classic_test())
        self.assertConfigEqual(
            self.sample_config("classic.full.toml", "custom"), config_tester.pyproject_classic_test()
        )
        self.assertConfigEqual(
            self.sample_config("classic.toml", "pyproject"), self.sample_config("classic.full.toml", "custom")
        )
        self.assertConfigEqual(self.sample_config("classic.toml", "pyproject"), config_tester.pyproject_classic_test())
        self.assertConfigEqual(self.sample_config("classic.toml", "custom"), config_tester.pyproject_classic_test())

    def test_pyproject_complex(self):
        self.assertConfigEqual(
            self.sample_config("complex.toml", "pyproject"), self.sample_config("complex.toml", "custom")
        )
        self.assertConfigEqual(self.sample_config("complex.toml", "pyproject"), config_tester.pyproject_complex_test())
        self.assertConfigEqual(self.sample_config("complex.toml", "custom"), config_tester.pyproject_complex_test())

    def test_min_max_match_log_filter(self):
        assert RunbotExcludeWarning(name="A", regex="A", min_match=2) == RunbotExcludeWarning(
            name="A",
            regex="A",
            min_match=2,
            max_match=2,
        ), "Assert Min and max match follow each other if not set"
        assert RunbotExcludeWarning(name="A", regex="A", min_match=10, max_match=2) == RunbotExcludeWarning(
            name="A",
            regex="A",
            max_match=10,
            min_match=10,
        ), "Assert Min and max match follow each other if not set"
        assert RunbotExcludeWarning(name="A", regex="A", min_match=-1) == RunbotExcludeWarning(
            name="A",
            regex="A",
            max_match=1,
            min_match=0,
        ), "Assert if Min is -1 then this means 0 min match"
        assert RunbotExcludeWarning(name="A", regex="A", min_match=0) == RunbotExcludeWarning(
            name="A",
            regex="A",
            max_match=1,
            min_match=0,
        ), "Assert if Min is 0 then this means 0 min match"
        assert RunbotExcludeWarning(name="A", regex="A", max_match=0) == RunbotExcludeWarning(
            name="A",
            regex="A",
            max_match=0,
            min_match=0,
        ), "Assert if Max is 0 means exacly 0 match possible"
        assert RunbotExcludeWarning(name="A", regex="A", max_match=999) == RunbotExcludeWarning(
            name="A",
            regex="A",
            max_match=100,
            min_match=1,
        ), "Assert if Max can't be more than 100If you want more than 100, you should fix this logger :-)"

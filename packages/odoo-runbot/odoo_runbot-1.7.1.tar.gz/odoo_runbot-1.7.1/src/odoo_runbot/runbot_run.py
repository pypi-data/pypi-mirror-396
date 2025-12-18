from __future__ import annotations

import builtins
import contextlib
import logging
import typing
import warnings

import coverage
from environ_odoo_config.cli import cli_save_env_config

from . import _odoo_internal, runbot_run_logging, runbot_run_test
from .runbot_config import RunbotPyWarningsFilter, StepAction

if typing.TYPE_CHECKING:
    from pathlib import Path
    from warnings import WarningMessage

    from .runbot_config import RunbotStepConfig
    from .runbot_env import RunbotEnvironment

_logger = logging.getLogger("odoo_runbot")

__all__ = ["StepRunner"]


class StepRunner:
    """The main logique to execiute a runbot step-by-step. See `run`"""

    def __init__(self, env: RunbotEnvironment) -> None:
        self.env = env
        self.has_run: bool = False

    def set_odoo_config(self, step: RunbotStepConfig) -> None:
        if step.include_current_project:
            self.env.odoo_config.addons_path.addons_path.add(self.env.abs_curr_dir)
        self.env.odoo_config.update_init.init = set(step.modules)
        self.env.odoo_config.update_init.update = set(step.modules)
        self.env.odoo_config.misc.with_demo = True
        self.env.odoo_config.http.interface = "127.0.0.1"
        self.env.odoo_config.http.enable = True
        self.env.odoo_config.misc.stop_after_init = True
        self.env.odoo_config.test.test_enable = step.action == StepAction.TESTS
        if step.action == StepAction.TESTS and step.test_tags:
            self.env.odoo_config.test.test_tags = set(step.test_tags)
        # Hard set value
        # In test mode we don't care about loading language
        # But il you do multiple step, you load multiple time the registry.
        # And in odoo.modules.loadings.load_module they `pop` this key, idkw
        # So in test mode, we force this option key to None
        self.env.odoo_config.i18n.load_language = None
        cli_save_env_config(self.env.odoo_config)

    def setup_odoo(self) -> None:
        _odoo_internal.setup_odoo()

    def execute(self, step: RunbotStepConfig) -> int:
        """The module to install before runnning the test.
        This modules can be a `CSV` value to install multiple value.
        Usage:
            module_name="account,my_project_config"
        Warning: When this variable is used, the test are disabled, so all the test with tag `+post_install` are not run
        """
        _logger.info("Run step %s(action=%s)", step.name, str(step.action.value))
        self.has_run = True
        if step.action == StepAction.INSTALL:
            return self._do_execute_action_install(step)
        if step.action == StepAction.TESTS:
            return self._do_execute_action_tests(step)
        _logger.error("Unknown action: %s", step.action)
        return 404

    def _do_execute_action_install(self, step: RunbotStepConfig) -> int:
        """The module to install before runnning the test.
        This modules can be a `CSV` value to install multiple value.
        Usage:
            module_name="account,my_project_config"
        Warning: When this variable is used, the test are disabled, so all the test with tag `+post_install` are not run
        """
        self.set_odoo_config(step)
        output_dir = self.env.result_path / "x_unittest"
        with runbot_run_logging.start_warning_log_watcher(step) as log_filters_extractor:  # noqa: SIM117
            with warnings.catch_warnings(record=True) as warnings_list:
                rc = _odoo_internal.run_odoo_and_stop()
                _logger.info("Odoo Done rc=%s", rc)
        log_filters = log_filters_extractor()
        return abs(rc) + self._execute_to_filters(step, log_filters, warnings_list, output_dir=output_dir)

    def _do_execute_action_tests(self, step: RunbotStepConfig) -> int:
        """Run a step and activate all the test feat:
        - coverage
        - Logger matching
        - Xunit report with [xmlrunner](https://unittest-xml-reporting.readthedocs.io/en/latest/)

        Args:
            step: The step to run, containing log filter and warning filter

        Returns: The result code > 1 mean error

        """
        coverage_watcher = DummyCoverage()
        activate_coverage = step.coverage and self.env.report_coverage()
        if activate_coverage:
            coverage_watcher = self.get_coverage()
        else:
            _logger.info("Disable coverage reporting")

        _logger.info("Setup Odoo ...")
        self.set_odoo_config(step)
        logging.getLogger("odoo.tests.stats").setLevel(logging.DEBUG)
        output_dir = self.env.result_path / "x_unittest"
        with runbot_run_logging.start_warning_log_watcher(step) as log_filters_extractor:  # noqa: SIM117
            with _odoo_internal.patch_odoo_test_suite(output_dir, coverage_watcher):
                with warnings.catch_warnings(record=True) as warnings_list:
                    rc = _odoo_internal.run_odoo_and_stop()
                    _logger.info("Odoo Done rc=%s", rc)
        log_filters = log_filters_extractor()
        if not abs(rc) and activate_coverage:
            _logger.info("Save Coverage recording in ...")
            coverage_watcher.report()
        return abs(rc) + self._execute_to_filters(step, log_filters, warnings_list, output_dir=output_dir)

    def get_coverage(self) -> coverage.Coverage:
        debug = None
        if self.env.verbose:
            debug = ["config"]
        return coverage.Coverage(
            debug=debug,
            config_file=str(self.env.abs_curr_dir.joinpath("pyproject.toml")),
            omit=["**/__manifest__.py", "**/__init__.py", "/odoo/odoo-src/**"],
            data_file=self.env.result_path / ".coverage",
        )

    def _execute_to_filters(
        self,
        step: RunbotStepConfig,
        log_filters: list[runbot_run_logging.ExcludeWarningFilter],
        warnings_list: list[WarningMessage],
        output_dir: Path,
    ) -> int:
        if log_filters or warnings_list:
            _logger.info("Test Logger and py.warnings...")
            res = runbot_run_test.execute_test_after_odoo(
                step.name,
                log_filters,
                warnings_list if not step.allow_warnings else [],
                test_runner=runbot_run_test.get_test_runner(output_dir),
            )
            rc = int(not res.wasSuccessful())
            _logger.info("Test logger rc=%s", rc)
            return rc
        return 0

    def setup_warning_filter(self, warning_filters: list[RunbotPyWarningsFilter]) -> None:
        for waring_filer in warning_filters:
            warnings.filterwarnings(
                action=waring_filer.action,
                category=getattr(builtins, waring_filer.category, Warning),
                message=waring_filer.message,
            )


class DummyCoverage:
    def __getattr__(self, item: str) -> typing.Any:  # noqa: ANN401
        return DummyCoverage()

    @contextlib.contextmanager
    def collect(self) -> None:
        yield

    def report(self) -> None:
        pass

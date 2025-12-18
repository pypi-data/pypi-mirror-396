import pathlib
import sys

from odoo_runbot.runbot_config import (
    RunbotExcludeWarning,
    RunbotStepConfig,
    RunbotToolConfig,
    StepAction,
    log_filter_by_odoo_version,
    warning_filter_by_odoo_version,
)

if sys.version_info >= (3, 11):
    pass
else:
    pass


def sample_config(fname: str) -> RunbotToolConfig:
    path = pathlib.Path(__file__).resolve().parent.joinpath("sample_config", fname)
    return RunbotToolConfig.load_from_file(path)


def minimal_config_test() -> RunbotToolConfig:
    """[tool.runbot]
    modules = ["module_to_test"]
    """
    global_module = ["module_to_test"]
    log_filters = log_filter_by_odoo_version()
    warning_filters = warning_filter_by_odoo_version()
    return RunbotToolConfig(
        steps=[
            RunbotStepConfig(
                include_current_project=True,
                name="default",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=log_filters,
            ),
        ],
        warning_filters=warning_filters,
        pretty=True,
    )


def classic_file_config_test() -> RunbotToolConfig:
    log_filters = log_filter_by_odoo_version()
    warning_filters = warning_filter_by_odoo_version()
    return RunbotToolConfig(
        warning_filters=warning_filters,
        steps=[
            RunbotStepConfig(
                include_current_project=True,
                name="install",
                modules=["moduleA", "moduleB"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=False,
                log_filters=log_filters,
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="step1",
                modules=["module3"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=log_filters,
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="step2",
                modules=["module_step2"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=log_filters,
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="step3",
                modules=["moduleA", "moduleB"],
                action=StepAction.TESTS,
                test_tags=[],
                coverage=True,
                log_filters=log_filters,
            ),
        ],
        pretty=True,
    )


def pyproject_classic_test() -> RunbotToolConfig:
    global_module = ["module_to_test", "module_to_test_2"]
    odoo_filters = log_filter_by_odoo_version()
    global_log_filter = [
        RunbotExcludeWarning(
            name=f"All Steps - Logger Filter {len(odoo_filters) + 1}",
            regex=".*log to accept.*",
            logger="",
            min_match=1,
            max_match=1,
        )
    ]

    warning_filters = warning_filter_by_odoo_version()
    return RunbotToolConfig(
        warning_filters=warning_filters,
        steps=[
            RunbotStepConfig(
                include_current_project=True,
                name="install",
                modules=global_module,
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=False,
                log_filters=odoo_filters + global_log_filter,
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="tests",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=["/module_to_test:MyTestCase", "/module_to_test"],
                coverage=True,
                log_filters=odoo_filters + global_log_filter,
            ),
        ],
        pretty=True,
    )


def pyproject_complex_test() -> RunbotToolConfig:
    odoo_filters = log_filter_by_odoo_version()

    warning_filters = warning_filter_by_odoo_version()
    global_regex = [
        RunbotExcludeWarning(
            name=f"All Steps - Logger Filter {len(odoo_filters) + 1}",
            regex=r".*global-regex-warning-1.*",
        ),
        RunbotExcludeWarning(
            name="global-regex-warning-2",
            regex=r".*global-regex-warning-2.*",
            min_match=1,
            max_match=2,
        ),
    ]
    global_module = ["module_to_test", "module_to_test2"]
    global_coverage = False

    return RunbotToolConfig(
        warning_filters=warning_filters,
        steps=[
            RunbotStepConfig(
                include_current_project=True,
                name="install",
                modules=["first_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=odoo_filters
                + global_regex
                + [
                    RunbotExcludeWarning(
                        regex=".*Install filter.*",
                        name=f"Step install - Logger Filter {len(odoo_filters) + 3}",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="tests",
                modules=global_module,
                action=StepAction.TESTS,
                test_tags=["+at-install", "-post-install"],
                coverage=True,
                log_filters=odoo_filters
                + global_regex
                + [
                    RunbotExcludeWarning(
                        regex=".*regex warning.*",
                        name="test-regex-log-warning-2",
                        min_match=1,
                        max_match=1,
                    ),
                ],
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="warmup",
                modules=["second_module_to_install"],
                action=StepAction.INSTALL,
                test_tags=[],
                coverage=global_coverage,
                log_filters=odoo_filters + global_regex,
            ),
            RunbotStepConfig(
                include_current_project=True,
                name="Post install test",
                modules=["module_to_test2"],
                action=StepAction.TESTS,
                test_tags=["-at-install", "+post-install"],
                coverage=False,
                log_filters=odoo_filters
                + global_regex
                + [
                    RunbotExcludeWarning(
                        name=f"Step Post install test - Logger Filter {len(odoo_filters) + 3}",
                        regex=".*Post install test regex-warnings.*",
                        min_match=2,
                        max_match=2,
                    ),
                ],
            ),
        ],
        pretty=True,
    )

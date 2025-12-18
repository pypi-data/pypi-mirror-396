import os
import sys
from pathlib import Path

import odoo.release

from odoo_runbot.cli import _run_init_runbot, _run_run_runbot, console
from odoo_runbot.runbot_env import RunbotEnvironment

if __name__ == "__main__":
    env = RunbotEnvironment(
        {
            **os.environ,
            "LOG_LEVEL": "debug",
            "ODOO_VERSION": odoo.release.serie,
            "CI_SERVER_URL": "https://gitlab.mangono.io",
            "CI_API_V4_URL": "https://gitlab.mangono.io/api/v4",
            "ADDONS_GIT_DEFAULT_SERVER": "gitlab.mangono.io",
            "ADDONS_GIT_DEFAULT_PROTOCOLE": "public",
            "ADDONS_GIT_DEFAULT_CLONE_PATH": "odoo_project/addons/",
            "CI_PROJECT_NAME": "odoo-quality",
            "CI_PROJECT_PATH": "gitlab-ci/odoo-quality",
            "ADDONS_GIT_PRIVATE_PROJECT": "odoo-addons/blank-private",
            "ADDONS_GIT_IMG_TESTER": "dockers/odoo-img-tester",
            "CI_JOB_TOKEN": os.getenv("GITLAB_TOKEN"),
            "ODOO_RC": "odoo_project/addons/odoo.ini",
            "ODOO_PATH": "/home/apasquier/workspace/odoo/odoo18",
        },
        workdir=Path("odoo_project"),
        verbose=True,
    )
    env.setup_logging_for_runbot(console)
    if not env.GITLAB_READ_API_TOKEN:
        msg = "Please export a variable named : CI_JOB_TOKEN or GITLAB_TOKEN or GITLAB_READ_API_TOKEN"
        raise ValueError(msg)
    env.print_info()
    if not env.check_ok():
        sys.exit(300)
    _run_init_runbot(env)
    _run_run_runbot(env, None, None)

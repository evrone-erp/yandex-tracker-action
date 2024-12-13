import json
import logging
import re
import sys
from typing import Dict

from environs import Env
from github import Github

from helpers.github import check_if_pr, get_pr_commits, set_pr_body

# conflict with black
# isort: off
from helpers.yandex import YandexHelper

# isort: on

logger = logging.getLogger(__name__)
env = Env()

REVIEW_STATUS = "in_review"
RESOLVE_STATUS = "resolve"
PR_OPEN_STATUS = "open"
PR_CLOSED_STATUS = "closed"

DEFAULT_TASK_KEY_PATTERN = r"[^[]*\[([^]]*)\]"

GITHUB_TOKEN = env("INPUT_TOKEN")
GITHUB_EVENT_PATH = env("GITHUB_EVENT_PATH")
GITHUB_REPOSITORY = env("GITHUB_REPOSITORY")
TASK_URL = env.bool("INPUT_TASK_URL", False)
TASK_KEYS = env("INPUT_TASKS", "")
TARGET_STATUS = env("INPUT_TO", "")
YANDEX_ORG_ID = env("INPUT_YANDEX_ORG_ID")
IS_YANDEX_CLOUD_ORG = env.bool("INPUT_IS_YANDEX_CLOUD_ORG", False)
YANDEX_OAUTH2_TOKEN = env("INPUT_YANDEX_OAUTH2_TOKEN")
IGNORE_TASKS = env("INPUT_IGNORE", "")
IGNORE_TASKS = [] if not IGNORE_TASKS else IGNORE_TASKS.split(",")
NOTIFY_STATUS_TASK = env.bool("INPUT_NOTIFY_STATUS_TASK", True)
TASK_KEY_PATTERN = env("INPUT_TASK_KEY_PATTERN", DEFAULT_TASK_KEY_PATTERN)


if __name__ == "__main__":

    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)8s | %(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        force=True,
    )

    try:
        task_key_regexp = re.compile(TASK_KEY_PATTERN)
    except re.error as e:
        logger.error("Invalid regex pattern in [task_key_pattern] variable: %s", e)
        logger.warning("Falling back to the default pattern.")
        task_key_regexp = re.compile(DEFAULT_TASK_KEY_PATTERN)

    with open(GITHUB_EVENT_PATH, "r", encoding="utf8") as f:
        data = json.load(f)
    check_if_pr(data=data)

    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPOSITORY)
    pr = repo.get_pull(number=int(data["pull_request"]["number"]))
    commits = get_pr_commits(pr=pr, task_key_pattern=task_key_regexp)
    task_keys = list(set(TASK_KEYS.split(",") + commits))
    iam_token = YandexHelper.get_iam_token(YANDEX_OAUTH2_TOKEN)

    yandex = YandexHelper(
        token=iam_token,
        org_id=YANDEX_ORG_ID,
        is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
    )

    if any(task_keys):
        existing_tasks: Dict = yandex.task_exists(
            tasks=task_keys,
        )
    else:
        logger.warning("[SKIPPED] No tasks found!")
        sys.exit(0)
    set_pr_body(tasks=existing_tasks, pr=pr)

    if TARGET_STATUS:
        target_status = TARGET_STATUS
    elif (
        not data["pull_request"]["merged"]
        and data["pull_request"]["state"] == PR_OPEN_STATUS
    ):
        target_status = REVIEW_STATUS
    elif (
        data["pull_request"]["merged"]
        and data["pull_request"]["state"] == PR_CLOSED_STATUS
    ):
        target_status = RESOLVE_STATUS
    else:
        target_status = None

    if target_status:
        statuses = yandex.move_task(
            notify_status=NOTIFY_STATUS_TASK,
            ignore_tasks=IGNORE_TASKS,
            pr=pr,
            task_keys=list(existing_tasks),
            target_status=target_status,
        )

        # Add comment with PR link to comment for tasks
        if data.get("action", "") == "opened":  # check pull request action type
            for task_key in existing_tasks:
                yandex.add_pr_link2task(
                    task_key=task_key,
                    pr_link=pr.html_url,
                )
        logger.info("Transition: %r", TARGET_STATUS)
        logger.info("Statuses: %r", statuses)
    else:
        logger.warning("No transition")

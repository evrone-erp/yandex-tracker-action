import json
import logging
import sys

from environs import Env
from github import Github

from helpers.github import check_if_pr, get_pr_commits, set_pr_body
from helpers.yandex import get_iam_token, move_task, task_exists, comment_task

env = Env()

GITHUB_TOKEN = env("INPUT_TOKEN")
GITHUB_EVENT_PATH = env("GITHUB_EVENT_PATH")
GITHUB_REPOSITORY = env("GITHUB_REPOSITORY")
TASK_URL = env.bool("INPUT_TASK_URL", False)
TASK_KEYS = env("INPUT_TASKS", "")
TARGET_STATUS = env("INPUT_TO", "")
COMMENT = env("COMMENT", "")
YANDEX_ORG_ID = env("INPUT_YANDEX_ORG_ID")
IS_YANDEX_CLOUD_ORG = env.bool("INPUT_IS_YANDEX_CLOUD_ORG", False)
YANDEX_OAUTH2_TOKEN = env("INPUT_YANDEX_OAUTH2_TOKEN")
IGNORE_TASKS = env("INPUT_IGNORE", "")
IGNORE_TASKS = [] if not IGNORE_TASKS else IGNORE_TASKS.split(",")

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)8s | %(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        force=True,
    )

    with open(GITHUB_EVENT_PATH, "r", encoding="utf8") as f:
        data = json.load(f)

    check_if_pr(data=data)

    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPOSITORY)
    pr = repo.get_pull(number=int(data["pull_request"]["number"]))
    commits = get_pr_commits(pr=pr)
    task_keys = list(set(TASK_KEYS.split(",") + commits))
    iam_token = get_iam_token(YANDEX_OAUTH2_TOKEN)

    if any(task_keys):
        existing_tasks = task_exists(
            org_id=YANDEX_ORG_ID,
            is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
            tasks=task_keys,
            token=iam_token,
        )
    else:
        logger.warning("[SKIPPED] No tasks found!")
        sys.exit(0)

    set_pr_body(task_keys=existing_tasks, pr=pr)

    if COMMENT:
    	commentResponse = comment_task(
                ignore_tasks=IGNORE_TASKS,
                org_id=YANDEX_ORG_ID,
                is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
                pr=pr,
                task_keys=task_keys,
                comment=COMMENT,
                token=iam_token,
            )
    	logger.info("Add comment response: %r", commentResponse)
    	else:
       		logger.warning("No comment")

    if TARGET_STATUS:
        statuses = move_task(
            ignore_tasks=IGNORE_TASKS,
            org_id=YANDEX_ORG_ID,
            is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
            pr=pr,
            task_keys=task_keys,
            target_status=TARGET_STATUS,
            token=iam_token,
        )
        logger.info("Transition: %r", TARGET_STATUS)
        logger.info("Statuses: %r", statuses)
    else:
        logger.warning("No transition for task")

import json
import logging
import sys

from environs import Env
from github import Github

from helpers.github import check_if_pr, get_pr_commits, set_pr_body
from helpers.yandex import get_iam_token, move_task, task_exists, add_pr_link2task

env = Env()

REVIEW_STATUS = "In Review" # "in_review"
RESOLVE_STATUS = "resolve"
PR_OPEN_STATUS = "open"
PR_CLOSED_STATUS = "closed"

GITHUB_TOKEN = env("INPUT_TOKEN")
GITHUB_EVENT_PATH = env("GITHUB_EVENT_PATH")
GITHUB_EVENT_NAME = env('GITHUB_EVENT_NAME')
GITHUB_ACTION = env('GITHUB_ACTION')
GITHUB_REPOSITORY = env("GITHUB_REPOSITORY")
TASK_URL = env.bool("INPUT_TASK_URL", False)
TASK_KEYS = env("INPUT_TASKS", "")
TARGET_STATUS = env("INPUT_TO", "")
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

    print("GITHUB_EVENT_NAME", GITHUB_EVENT_NAME)
    print("GITHUB_ACTION", GITHUB_ACTION)
    if target_status:
        statuses = move_task(
            ignore_tasks=IGNORE_TASKS,
            org_id=YANDEX_ORG_ID,
            is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
            pr=pr,
            task_keys=existing_tasks,
            target_status=target_status,
            token=iam_token,
        )
        # for task_key in existing_tasks:
        #     result = add_pr_link2task(
        #         org_id=YANDEX_ORG_ID,
        #         is_yandex_cloud_org=IS_YANDEX_CLOUD_ORG,
        #         token=iam_token,
        #         task_key=task_key,
        #         pr_link=pr.html_url
        #     )
        logger.info("Transition: %r", TARGET_STATUS)
        logger.info("Statuses: %r", statuses)
    else:
        logger.warning("No transition")

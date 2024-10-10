import logging
import re
import sys
from typing import Dict, Optional

from github.PullRequest import PullRequest

TASK_KEY_PATTERN = re.compile(r"[^[]*\[([^]]*)\]")  # noqa
TASK_LINK_TITLE_TEMPLATE = (
    "[[{task_key}] {task_title}](https://tracker.yandex.ru/{task_key})"
)
logger = logging.getLogger(__name__)


def _prepare_description(
    *,
    tasks: Dict,
    pr: PullRequest,
) -> Optional[str]:
    """
    Update the existing PR description with links to the task keys.
    Args:
      tasks: Dict with Yandex Tracker task number as key and task data as value.
      pr: GitHub PullRequest object.
    Return:
      Description in string format if exists or None.
    """
    body = pr.body
    links = [
        TASK_LINK_TITLE_TEMPLATE.format(
            task_key=task_key,
            task_title=task_data.get("summary", ""),
        )
        for task_key, task_data in tasks.items()
    ]

    task_links = ""
    for link in links:
        if body and link in body:
            continue

        task_links += f"{link}\n\n"

    return f"{task_links}{body or ''}"  # noqa


def get_pr_commits(
    *,
    pr: PullRequest,
) -> list[str]:
    """
    Get all commits from PR to a list if there are many, or str if there is one.
    Args:
      pr: GitHub PullRequest object.
    Returns:
      List of all current PR's commits.
    """
    commits = []

    for commit in pr.get_commits():
        all_matches = TASK_KEY_PATTERN.findall(commit.commit.message)
        if not all_matches:
            continue

        commits.append(all_matches[0])

    return commits


def set_pr_body(
    *,
    tasks: Dict,
    pr: PullRequest,
) -> None:
    """
    Set PR description with a link to tracker task.
    Args:
      tasks: Dict with Yandex Tracker task number as key and task data as value.
      pr: GitHub PullRequest object.
    """
    description = _prepare_description(tasks=tasks, pr=pr)
    if description:
        pr.edit(body=description)


def check_if_pr(*, data: dict[str, str]):
    """
    Checking the pull_request key in action.
    Args:
      data: dict with available data from runner.
    Raises:
      System error exit code 1.
    """
    try:
        data["pull_request"]
    except KeyError:
        logger.warning("[SKIPPING] You can use this action only on Pull Request")
        sys.exit(1)

import logging
import re
import sys
from typing import Optional

from github.PullRequest import PullRequest

TASK_KEY_PATTERN = re.compile(r"[^[]*\[([^]]*)\]")  # noqa
logger = logging.getLogger(__name__)


def _prepare_description(
    *,
    task_keys: list[str],
    pr: PullRequest,
) -> Optional[str]:
    """
    Update the existing PR description with links to the task keys.
    Args:
      task_keys: List of the Yandex tracker tasks from action.
      pr: GitHub PullRequest object.
    Return:
      Description in string format if exists or None.
    """
    body = pr.body
    links = [f"https://tracker.yandex.ru/{task}" for task in filter(None, task_keys)]

    task_links = ""
    for link in links:
        if body and link in body:
            continue

        task_links += f"{link}\n\n"

    return f"{task_links}{body or ''}"


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
    task_keys: list[str],
    pr: PullRequest,
) -> None:
    """
    Set PR description with a link to tracker task.
    Args:
      task_keys: list of Yandex tracker task keys.
      pr: GitHub PullRequest object.
    """
    description = _prepare_description(task_keys=task_keys, pr=pr)
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

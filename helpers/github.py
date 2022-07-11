import re
import sys
from typing import Optional

from github.PullRequest import PullRequest


def _prepare_description(
  *,
  task_keys: list[str],
  pr: PullRequest,
) -> Optional[str]:
  """
  Update existing PR description with links to the task keys.
  Args:
    task_keys: List of the Yandex tracker tasks from action.
    pr: github PullRequest object.
  Return:
    Desctiption in string format if exists or None.
  """
  body = pr.body
  links = [
    f'https://tracker.yandex.ru/{task}' for task in filter(None, task_keys)]

  if body:
    updated_links = ''.join(
      sorted(list(set([item for item in links]) - set([item.strip() for item in body.split('\n')]))))
    description = updated_links + '\n' + body
  else:
    description = '\n'.join(sorted(list([item for item in links])))
  return description


def get_pr_commits(
  *,
  pr: PullRequest,
) -> list[str]:
  """
  Get all commits from PR to a list if there are many, or str if there is one. 
  Args:
    pr: github PullRequest object.
  Returns:
    List of all current PR`s commits.
  """
  commits = []

  for commit in pr.get_commits():
    try:
      commits.append(re.match(r'[^[]*\[([^]]*)\]', commit.commit.message).groups()[0])
    except AttributeError:
      continue

  return commits


def set_pr_body(
  *,
  task_keys: list[str],
  pr: PullRequest,
) -> None:
  """
  Set PR description with link to tracker task.
  Args:
    task_key: list of Yandex tracker task keys.
    pr: github PullRequest object.
  """
  description = _prepare_description(task_keys=task_keys, pr=pr)
  if description:
    pr.edit(body=description)


def check_if_pr(
  *,
  data: dict[str, str]
):
  """
  Checking the pull_request key in action.
  Args:
    data: dict with available data from runner.
  Raises:
    System error exit code 1.
  """
  try:
    data['pull_request']
  except KeyError:
    print('[SKIPPING] You can use this action only on Pull Request')
    sys.exit(1)

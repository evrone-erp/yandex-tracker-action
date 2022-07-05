import re
import sys

from github.PullRequest import PullRequest


def get_pr_commits(
    *,
    pr: PullRequest,
) -> list[str] or tuple[None, str]:
  """
  Get all commits from PR to a list if there are many, or str if there is one. 
  Args:
    pr: github PullRequest object.
  Returns:
    List of all current PR`s commits.
    Or one PR commit.
    Or tuple with error if parsing fails.
  """
  try:
    task_key = list(
        {
            re.match(r'[^[]*\[([^]]*)\]', commit.commit.message).groups()[0]
            for commit in pr.get_commits()
        }
    )
  except AttributeError:
    task_key = None, 'Cannot parse task key from commit: expect example "Commit message [RI-1]" where [RI-1] is the task number, or specify TASKS in action'

  return task_key


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
  # TODO check if description with task url already exists
  pr.edit(body='\n'.join(
      [f'https://tracker.yandex.ru/{task}' for task in task_keys]))


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
    print('Sorry! You can use this action only on Pull Request')
    sys.exit(1)

import sys

import requests
from github.PullRequest import PullRequest


def _get_all_transitions(
    *,
    org_id: str,
    token: str,
    ignore_tasks: list[str],
    task_keys: list[str],
) -> dict[str, dict[str, str]]:
  """
  Fetch all available task transitions.
  Args:
    ignore_tasks: list of tasks to ignore.
    token: Yandex OAUTH2 token.
    org_id: Yandex organization ID.
    task_key: Yandex tracker task key.
  Returns:
    Response from Yandex Tracker API in dict.
  Raises:
    System error exit code 1 if task not exists.	
  """

  statuses = {}
  if list(set(task_keys) - set(ignore_tasks)):
    for task_key in task_keys:
      statuses[task_key] = requests.get(
          headers={
              'Authorization': f'OAuth {token}',
              'X-Org-ID': f'{org_id}',
              'Content-Type': 'application/json',
          },
          url=f'https://api.tracker.yandex.net/v2/issues/{task_key}/transitions'
      ).json()

  try:
    {
        k: {
            i['id']: i['display'] for i in v
        } for (k, v) in statuses.items()
    }
  except TypeError:
    print(statuses)
    return sys.exit(1)
  else:
    return {
        k: {
            i['id']: i['display'] for i in v
        } for (k, v) in statuses.items()
    }


def move_task(*,
              org_id: str,
              to: str,
              token: str,
              ignore_tasks: list[str],
              task_keys: list[str],
              pr: PullRequest,
              ) -> tuple[dict[str, str], dict[str, str] or str]:
  """
  Change task transition.
  Args:
    ignore_tasks: list of tasks to ignore.
    org_id: str. Yandex organization ID.
    pr: github PullRequest object.
    task_key: List of task keys.
    to: The name of the transition where to move the task.
    token: Yandex OAUTH2 token.
  Returns:
    All available transition statuses and full response from Yandex Tracker API
    in json format. If the task is already in the wanted state, this returns the message DO NOTHING
    instead of an API response.
  """
  statuses = _get_all_transitions(
      ignore_tasks=ignore_tasks, org_id=org_id, task_keys=task_keys, token=token)

  job = 'NOTHING TO DO'

  response = {}

  for k, v in statuses.items():
    for a, b in v.items():
      if to in a or to in b:
        response[k] = (requests.post(
            headers={
                'Authorization': f'OAuth {token}',
                'X-Org-ID': f'{org_id}',
                'Content-Type': 'application/json',
            },
            url=f'https://api.tracker.yandex.net/v2/issues/{k}/transitions/{a}/_execute',
            json={'comment': f'Task moved to "{b}"'}
        ).json())
      pr.create_issue_comment(body=f'Task moved to "{b}" :rocket:')

  return statuses, job if not response else response

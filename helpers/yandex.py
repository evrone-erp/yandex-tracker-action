import requests
from github.PullRequest import PullRequest


def _format_output(
  *,
  to: str,
  statuses: dict[str, dict[str, str]],
) -> str:
  """
  Build human readable message output.
  Args:
    to: Desired task transition.
    statuses: All available statuses for the task.
  Returns:
    Message that will be displayed in action job.
  """
  output = ''

  for k, v in statuses.items():
    if v and to not in v:
      output += f'{k} NOTHING TO DO. AVAILABLE TRANSITIONS IS: {v}\n'
    elif not v:
      output += f'WARNING! TASK {k} NOT FOUND\n'
    else:
     output += f'{k} TASK UPDATED \n'

  return output


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
  """

  statuses = {}
  tasks = list(set(task_keys) - set(ignore_tasks))

  if tasks:
    for task in filter(None, tasks):
      statuses[task] = requests.get(
        headers={
          'Authorization': f'OAuth {token}',
          'X-Org-ID': f'{org_id}',
          'Content-Type': 'application/json',
        },
        url=f'https://api.tracker.yandex.net/v2/issues/{task}/transitions'
      ).json()

  return {
      k: {
        i['id']: i['display'] for i in v
        if 'id' and 'display' in i
      } for (k, v) in statuses.items()
  }


def move_task(*,
  org_id: str,
  to: str,
  token: str,
  ignore_tasks: list[str],
  task_keys: list[str],
  pr: PullRequest,
) -> str:
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
    Message that will be displayed in action job output.
  """
  statuses = _get_all_transitions(
    ignore_tasks=ignore_tasks, org_id=org_id, task_keys=task_keys, token=token)

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
        pr.create_issue_comment(body=f'Task **{k}** moved to **"{b}"** :rocket:')

  statuses = _format_output(to=to, statuses=statuses)

  return statuses

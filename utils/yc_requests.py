import requests

from github.PullRequest import PullRequest


def _get_all_transitions(
	*,
	org_id: str,
	task_key: str,
	token: str,
) -> list[dict[str, str]]:
	"""
	Fetch all available task transitions.
  Args:
    token: str. Yandex OAUTH2 token.
    org_id: str. Yandex organization id.
    task_key: str. Yandex tracker task key.
  Returns:
    Response from Yandex Tracker API in json format.	
	"""
	response = requests.get(
		headers={
			'Authorization': f'OAuth {token}',
			'X-Org-ID': f'{org_id}',
			'Content-Type': 'application/json',
		},
		url=f'https://api.tracker.yandex.net/v2/issues/{task_key}/transitions'
	).json()

	return [{i['id']: i['display']} for i in response]

def move_task(*,
	ignore_tasks: list[str],
	org_id: str,
	pr: PullRequest,
	message: str,
	task_key: str,
	to: str,
	token: str,
) -> tuple[dict[str, str], dict[str, str] or str]:
	"""
	Fetch all available task transitions and move task.
  Args:
		ignore_tasks: list[str]. What task should ignore.
    org_id: str. Yandex organization id.
		pr: github PullRequest. PR object.
    task_key: str. Yandex tracker task key.
		to: str. Transition name where to move task.
		token: str. Yandex OAUTH2 token.
  Returns:
    All available transition statuses and full response from Yandex Tracker API
		in json format. If task already in wanted state, that return NOTHING TO DO message
		instead of API response.
	"""
	statuses = _get_all_transitions(org_id=org_id, task_key=task_key, token=token)

	move_to = 'NOTHING TO DO'

	if task_key not in ignore_tasks:
		for i in statuses:
			for k, v in i.items():
				if to in k or to in v:
					move_to = requests.post(
						headers={
							'Authorization': f'OAuth {token}',
							'X-Org-ID': f'{org_id}',
							'Content-Type': 'application/json',
						},
						url=f'https://api.tracker.yandex.net/v2/issues/{task_key}/transitions/{k}/_execute',
						json={'comment': f'Task moved to "{v if not message else message}"'}
					).json()
					pr.create_issue_comment(body=f'Task moved to "{v if not message else message}" :rocket:')
	
	return statuses, move_to

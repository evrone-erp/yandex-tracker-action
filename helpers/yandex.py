import logging
import sys
from http import HTTPStatus

import requests
from github.PullRequest import PullRequest

_REQUEST_TIMEOUT = 300.0

logger = logging.getLogger(__name__)


def _format_output(
    *,
    target_status: str,
    statuses: dict[str, dict[str, str]],
) -> str:
    """
    Build human-readable message output.
    Args:
      target_status: Desired task transition.
      statuses: All available statuses for the task.
    Returns:
      Message that will be displayed in an action job.
    """
    output = ""

    for k, v in statuses.items():
        if v and target_status not in v:
            output += f"{k}: nothing to do. Available transitions is: {v}; "
        elif not v:
            output += f"{k}: WARNING! Task not found; "
        else:
            output += f"{k}: updated; "

    return output


def task_exists(
    *,
    org_id: str,
    is_yandex_cloud_org: bool,
    tasks: list[str],
    token: str,
) -> list[str]:
    """
    Get Yandex API with task keys. If a task does not exist, remove from a list.
    Args:
      org_id: Registered organization in Yandex Tracker.
      is_yandex_cloud_org: Yandex organization header definition ID flag.
      tasks: All collected tracker tasks.
      token: Yandex Tracker IAM token.
    Returns:
      List of all valid tasks.
    """
    filtered_tasks = filter(None, tasks)
    existing_tasks = {}

    for task in filtered_tasks:
        existing_tasks[task] = requests.get(
            headers={
                "Authorization": f"Bearer {token}",
                f"X{'-Cloud' if is_yandex_cloud_org else ''}-Org-ID": org_id,
                "Content-Type": "application/json",
            },
            url=f"https://api.tracker.yandex.net/v2/issues/{task}",
            timeout=_REQUEST_TIMEOUT,
        ).json()

    return [k for (k, v) in existing_tasks.items() if "errors" not in v]


def _get_all_transitions(
    *,
    org_id: str,
    is_yandex_cloud_org: bool,
    token: str,
    ignore_tasks: list[str],
    task_keys: list[str],
) -> dict[str, dict[str, str]]:
    """
    Fetch all available task transitions.
    Args:
      ignore_tasks: list of tasks to ignore.
      token: Yandex IAM token.
      org_id: Yandex organization ID.
      is_yandex_cloud_org: Yandex organization header definition ID flag.
      task_keys: Yandex tracker task key.
    Returns:
      Response from Yandex Tracker API in dict.
    """
    statuses = {}
    tasks = list(set(task_keys) - set(ignore_tasks))

    if tasks:
        for task in filter(None, tasks):
            response = requests.get(
                headers={
                    "Authorization": f"Bearer {token}",
                    f"X{'-Cloud' if is_yandex_cloud_org else ''}-Org-ID": org_id,
                    "Content-Type": "application/json",
                },
                url=f"https://api.tracker.yandex.net/v2/issues/{task}/transitions",
                timeout=_REQUEST_TIMEOUT,
            )
            if response.status_code != HTTPStatus.OK:
                logger.warning("[SKIPPING] %s has error: %s", task, response.text)
                continue

            statuses[task] = response.json()

    return {
        task_key: {
            data["id"]: data["display"]
            for data in response_info
            if "id" in data and "display" in data
        }
        for (task_key, response_info) in statuses.items()
    }


def move_task(
    *,
    org_id: str,
    is_yandex_cloud_org: bool,
    target_status: str,
    token: str,
    ignore_tasks: list[str],
    task_keys: list[str],
    pr: PullRequest,
) -> str:
    """
    Change task transition.
    Args:
      ignore_tasks: list of tasks to ignore.
      org_id: str. Yandex's organization ID.
      is_yandex_cloud_org: Yandex organization header definition ID flag.
      pr: GitHub PullRequest object.
      task_keys: List of task keys.
      target_status: The name of the transition where to move the task.
      token: Yandex IAM token.
    Returns:
      Message that will be displayed in action job output.
    """
    transition_statuses = _get_all_transitions(
        ignore_tasks=ignore_tasks,
        org_id=org_id,
        is_yandex_cloud_org=is_yandex_cloud_org,
        task_keys=task_keys,
        token=token,
    )

    response = {}
    for k, v in transition_statuses.items():
        for a, b in v.items():
            if target_status in a or target_status in b:
                response[k] = requests.post(
                    headers={
                        "Authorization": f"Bearer {token}",
                        f"X{'-Cloud' if is_yandex_cloud_org else ''}-Org-ID": org_id,
                        "Content-Type": "application/json",
                    },
                    url=f"https://api.tracker.yandex.net/v2/issues/{k}/transitions/{a}/_execute",
                    json={"comment": f'Task moved to "{b}"'},
                    timeout=_REQUEST_TIMEOUT,
                ).json()
                pr.create_issue_comment(
                    body=f'Task **{k}** moved to **"{b}"** :rocket:'
                )

    statuses = _format_output(target_status=target_status, statuses=transition_statuses)
    return statuses


def get_iam_token(oauth_token: str) -> str:
    response = requests.post(
        headers={
            "Content-Type": "application/json",
        },
        url="https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"yandexPassportOauthToken": oauth_token},
        timeout=_REQUEST_TIMEOUT,
    ).json()

    iam_token = response.get("iamToken")
    if not iam_token:
        logger.warning("IAM token not found: %r", response)
        sys.exit(1)

    return iam_token

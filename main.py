import json

from environs import Env
from github import Github

from helpers.github import (
  check_if_pr,
  get_pr_commits,
  set_pr_body,
)
from helpers.yandex import move_task


env = Env()

GITHUB_TOKEN = env('INPUT_TOKEN')
GITHUB_REPOSITORY = env('GITHUB_REPOSITORY')
TASK_URL = env.bool('INPUT_TASK_URL', False)
TASK_KEYS = env('INPUT_TASKS', '')
TO = env('INPUT_TO', '')
YANDEX_ORG_ID = env('INPUT_YANDEX_ORG_ID')
YANDEX_OAUTH2_TOKEN = env('INPUT_YANDEX_OAUTH2_TOKEN')
IGNORE_TASKS = env('INPUT_IGNORE', '')

github = Github(GITHUB_TOKEN)
repo = github.get_repo(GITHUB_REPOSITORY)

with open(env('GITHUB_EVENT_PATH', 'r')) as f:
  data = json.load(f)

check_if_pr(data=data)

pr_number = data['pull_request']['number']
pr = repo.get_pull(number=int(pr_number))

commits = get_pr_commits(pr=pr)

IGNORE_TASKS = [] if not IGNORE_TASKS else IGNORE_TASKS.split(',')

TASK_KEYS = list(set(TASK_KEYS.split(',') + commits))

set_pr_body(task_keys=TASK_KEYS, pr=pr)

if not data['pull_request']['merged'] and data['pull_request']['state'] == 'open':

  TO = 'in_review' if not TO else TO

  statuses = move_task(
    ignore_tasks=IGNORE_TASKS,
    org_id=YANDEX_ORG_ID,
    pr=pr,
    task_keys=TASK_KEYS,
    to=TO,
    token=YANDEX_OAUTH2_TOKEN
  )

elif data['pull_request']['merged'] and data['pull_request']['state'] == 'closed':

  # TODO think about hardcode
  TO = 'resolve' if not TO else TO

  statuses = move_task(
    ignore_tasks=IGNORE_TASKS,
    org_id=YANDEX_ORG_ID,
    pr=pr,
    task_keys=TASK_KEYS,
    to=TO,
    token=YANDEX_OAUTH2_TOKEN
  )

print(statuses, f'TRANSITION: {TO}', sep='\n')

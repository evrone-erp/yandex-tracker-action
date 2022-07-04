import json

from environs import Env
from github import Github

from utils.yc_requests import move_task
from utils.helpers import get_pr_comments


env = Env()

GITHUB_TOKEN = env('INPUT_TOKEN')
GITHUB_REPOSITORY = env('GITHUB_REPOSITORY')
IGNORE_TASKS = env('INPUT_IGNORE', '')
TASK_URL = env.bool('INPUT_TASK_URL', False)
TASK_KEY = env('INPUT_TASK_KEY', '')
TO = env('INPUT_TO', '')
YANDEX_ORG_ID = env('INPUT_YANDEX_ORG_ID')
YANDEX_OAUTH2_TOKEN = env('INPUT_YANDEX_OAUTH2_TOKEN')
MESSAGE = env('INPUT_MESSAGE', '')

github = Github(GITHUB_TOKEN)
repo = github.get_repo(GITHUB_REPOSITORY)

TASK_KEY = env('GITHUB_HEAD_REF').split('/')[1] if not TASK_KEY else TASK_KEY
TASK_URL_COMMENT = f'Task url:\nhttps://tracker.yandex.ru/{TASK_KEY}'
ignore_tasks = IGNORE_TASKS.split(',') if IGNORE_TASKS else []

with open(env('GITHUB_EVENT_PATH', 'r')) as f:
	data = json.load(f)

pr_number = data['pull_request']['number']
pr = repo.get_pull(number=int(pr_number))

if not data['pull_request']['merged'] and data['pull_request']['state'] == 'open':

	TO = 'in_review' if not TO else TO
	comments = get_pr_comments(pr=pr)
	
	if TASK_URL and TASK_URL_COMMENT not in comments:
		pr.edit(body=TASK_URL_COMMENT)
	
	available_statuses, task_done = move_task(
		ignore_tasks=ignore_tasks,
		org_id=YANDEX_ORG_ID,
		pr=pr, message=MESSAGE,
		task_key=TASK_KEY,
		to=TO,
		token=YANDEX_OAUTH2_TOKEN
	)

	print('AVAILABLE_STATUSES:', available_statuses)
	print('TASK_DONE:', task_done)


elif data['pull_request']['merged'] and data['pull_request']['state'] == 'closed':

	# Как избавиться от хардкода? Решить - это стандрартное состояние у трекера?
	TO = 'resolve' if not TO else TO

	available_statuses, task_done = move_task(
		ignore_tasks=ignore_tasks,
		org_id=YANDEX_ORG_ID,
		pr=pr, message=MESSAGE,
		task_key=TASK_KEY,
		to=TO,
		token=YANDEX_OAUTH2_TOKEN
	)

	print('AVAILABLE_STATUSES:', available_statuses)
	print('TASK_DONE:', task_done)

print('***', 'TASK_KEY: ', TASK_KEY)
print('***', 'IGNORE:', *ignore_tasks)
print('***', 'TO:', TO)
print('***', 'TASK_URL:', TASK_URL)

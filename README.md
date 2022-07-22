# Yandex Tracker action

[RUS](https://github.com/evrone-erp/yandex-tracker-action/blob/master/README_RUS.md)

This action allows you to automatically move tasks on the board.

Move the task at Yandex Tracker board.

By default, it parses commits of the form "[RI-1] implement something" and takes the task number, which in this case is RI-1.

You can also set tasks directly in the action, for example, by specifying the output from the previous job.

If there are multiple commits with different task keys in the pull request, they will all be moved on the board.

It is also possible to specify multiple tasks in an action. See documentation below.

All task keys will be collected, both specified in the action and found in the commits.

If the task key is not found in the tracker, you will receive a warning, but the tasks found will be processed.

If the task has nowhere to move or it is already in the desired status, a message will be displayed.

Please feel free to report any issues.
## Usage

### Basic

By default, commit messages such as `"[RI-1] awesome-feature"` will be parsed, where `"RI-1"` will be the feature key. You can specify a specific task key. You can also use the logic from the previous job step.

```yaml
name: YC Tracker
on:
  pull_request:
    types:
      - opened
      - reopened
      - synchronize
      - closed

jobs:
 transit-tasks:
    runs-on: ubuntu-latest
    steps:

      - name: Checkout
        uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Move Task When PR Opened
        if: github.event.action != 'closed'
        uses: evrone-erp/yandex-tracker-action@v1
        with:
          token: ${{secrets.GITHUB_TOKEN}}
          yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
          yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
          task_url: true
          ignore: ERP-31,ERP-32

      - name: Move Task When PR Merged
        if: github.event.pull_request.merged == true
        uses: evrone-erp/yandex-tracker-action@v1
        with:
          token: ${{secrets.GITHUB_TOKEN}}
          yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
          yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
          task_url: true
          ignore: ERP-31,ERP-32
```

 ### Add specific task key

You can specify task numbers, separated by commas.

````yaml
- uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    tasks: RI-218 # or RI-218,RI-11
````

### Add ignore tasks

You may need to ignore some long lifecycle tasks. Add tasks, separated by commas. If you have long-running tasks that you do not want to automatically move, then you can ignore them.

````yaml
- uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    ignore: RI-1 # or RI-1,DI-8
````

### Comment PR with task url

If true — a comment will be set to the current PR with the task address of the form <https://tracker.yandex.ru/TASK_KEY> in the PR description.

```yaml
- uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    task_url: true
```

### Get all available transitions

By default, if the PR is open, the task will go into the `in_review` state. If the PRs are merged, the state is `resolve`. You can specify a *human readable name* or endpoint name.


Get all available states:

```shell
curl -H "Authorization: OAuth <oauth2-token>" -H "X-Org-ID: <org-id>" -H "Content-Type: application/json" https://api.tracker.yandex.net/v2/issues/<task-key>/transitions | jq ".[].id"
```

See output of the action and find states:

```yaml
- uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    to: 'На ревью' # or 'in_review'
```

### One move if PR is opened and one move if it is merged

You can move an issue when opening a PR and when merging a PR into different transitions. See default state names above.

```yaml
- name: Move Task When PR Opened
  if: github.event.action != 'closed'
  uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    to: 'in_review'

- name: Move Task When PR Merged
  if: github.event.pull_request.merged == true
  uses: evrone-erp/yandex-tracker-action@v1
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
    to: 'merged'
```
## Inputs

### `ignore`

**Optional** Ignored tasks separated by commas.

### `tasks`

**Optional** The task key to be moved on board.

### `task_url`

**Optional** The default value is false. Set to true if you want to comment on a PR with the task URL.

### `to`

**Optional** Specify where you want to move the task. The default is `in_review` **for open PRs and `resolve` for merged PRs**.

### `token`

**Required** Github token

### `yandex_oauth2_token`

**Required** Yandex oauth2 token. You need to register an OAUTH2 application and then get a user token. [Documentation](https://yandex.ru/dev/id/doc/dg/oauth/concepts/about.html).

### `yandex_org_id`

**Required** ID of organization registered in Yandex Tracker.


[<img src="https://evrone.com/logo/evrone-sponsored-logo.png" width=231>](https://evrone.com/?utm_source=evrone-django-template)

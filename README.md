# Yandex Tracker action

Move the task on Yandex Tracker board.

## Usage

### Basic

```yaml
- uses: ./
    with:
      token: ${{secrets.GITHUB_TOKEN}}
      yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
      yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
```

### Add specific task key

By default parsing branch name like `feature/DI-1/awesome-feature` where `DI-1` will be the task key. You can provide specific task key. You can use logic from previous job step.

````yaml
- uses: ./
    with:
      token: ${{secrets.GITHUB_TOKEN}}
      yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
      yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
      task_key: RI-218
````

### Add ignore tasks

You may need to ignore some long lifecycle tasks. Add tasks separeted by comma.

````yaml
- uses: ./
    with:
      token: ${{secrets.GITHUB_TOKEN}}
      yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
      yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
      ignore: RI-1,DI-8
````

### Comment PR with task url

If true - will be set comment to the current PR with task url like <https://tracker.yandex.ru/TASK_KEY>

```yaml
- uses: ./
    with:
      token: ${{secrets.GITHUB_TOKEN}}
      yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
      yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
      task_url: true
```

### In what state move the task

By default if PR is opened, the task will move to `in_review` state. If PR is merged - `resolve` state. You can provide *human readable name* or endpoint name.

Get all available states:

```shell
curl -H "Authorization: OAuth <oauth2-token>" -H "X-Org-ID: <org-id>" -H "Content-Type: application/json" https://api.tracker.yandex.net/v2/issues/<task-key>/transitions | jq ".[].id"
```

Also you can see output of the action and find these states there.

```yaml
- uses: ./
    with:
      token: ${{secrets.GITHUB_TOKEN}}
      yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
      yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
      to: 'На ревью' # or 'in_review'
```

### One move if PR is opened and one move if is merged

You can move the task when PR is opened and when PR is merged. See above default state names.

```yaml
- name: Move Task When PR Opened
  if: github.event.action != 'closed'
  uses: ./
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}

- name: Move Task When PR Merged
  if: github.event.pull_request.merged == true
  uses: ./
  with:
    token: ${{secrets.GITHUB_TOKEN}}
    yandex_org_id: ${{ secrets.YANDEX_ORG_ID }}
    yandex_oauth2_token: ${{ secrets.YANDEX_OAUTH2_TOKEN }}
```
## Inputs

### `ignore`

**Optional** Ignored tasks separated by comma.

### `task_key`

**Optional** Task key that need to move on board.

### `task_url`

**Optional** Default is false. Set to true if you want comment PR with task url.

### `to`

**Optional** State where need to move the task. By default for opened PR is `in_review` and for merged - `resolve`.

### `token`

**Required** Github token

### `yandex_oauth2_token`

**Required** Yandex oauth2 token. You need to register OAUTH2 app and than get user token. [Documentation](https://yandex.ru/dev/id/doc/dg/oauth/concepts/about.html).

### `yandex_org_id`

**Required** Id of organization registerd in Yandex Tracker.

## Outputs

### `available_statuses`

Available transition statuses for provided task on Yandex Tracker board.

### `task_done`

Full response from Yandex Tracker API in json format. If task already in the state, than `NOTHING TO DO` message will be printed.

### `task_key`

Task key working with.

### `ignore`

List of ignored tasks. If provided in a job.

### `to`

In what state task will be move.

### `task_url`

Enabled or disabled PR commentary with task url.

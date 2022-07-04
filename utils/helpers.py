from github.PullRequest import PullRequest


def get_pr_comments(
	*,
	pr: PullRequest,
) -> list[str]:
	"""
	Fetch all comments from PR to the list.
  Args:
    pr: github PullRequest. PR object.
  Returns:
    List of all current PR`s comments.
	"""
	return [
		comment.body for comment 
		in pr.get_issue_comments()
	]

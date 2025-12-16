import sys
from loguru import logger
logger.remove()
logger.add(sys.stderr, level='INFO')
from git_json_changes.core import generate_changes
from git_json_changes.git_module import get_commits, open_repo, cleanup_temp_repo
from git_json_changes.pr_module import get_pull_requests
from git_json_changes.jira_adapter import fetch_jira_issue
from git_json_changes.github_adapter import fetch_github_issue
from git_json_changes.issue_module import extract_issue_refs, fetch_issues_for_commit
__version__ = '0.1.0'
__all__ = ['generate_changes', 'get_commits', 'open_repo', 'cleanup_temp_repo', 'get_pull_requests', 'extract_issue_refs', 'fetch_issues_for_commit', 'fetch_jira_issue', 'fetch_github_issue']

def get_jira_issues(issue_keys, jira_url, jira_token, content_limit=50000):
    issues = []
    for key in issue_keys:
        issue = fetch_jira_issue(key, jira_url, jira_token, content_limit)
        if issue:
            issues.append(issue)
    return issues

def get_github_issues(issue_numbers, repo_path=None, content_limit=50000):
    import os
    if repo_path is None:
        repo_path = os.getcwd()
    issues = []
    for number in issue_numbers:
        issue = fetch_github_issue(number, repo_path, content_limit)
        if issue:
            issues.append(issue)
    return issues
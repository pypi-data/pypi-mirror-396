import re
from loguru import logger
from git_json_changes.constants import DEFAULT_ISSUE_REGEX, GITHUB_ISSUE_PATTERN, DEFAULT_ISSUE_LIMIT
from git_json_changes.jira_adapter import fetch_jira_issue
from git_json_changes.github_adapter import fetch_github_issue

def extract_issue_refs(text, jira_regex=DEFAULT_ISSUE_REGEX, include_github=False):
    result = {'jira': [], 'github': []}
    if not text:
        return result
    if jira_regex:
        jira_matches = re.findall(jira_regex, text)
        result['jira'] = list(set(jira_matches))
    if include_github:
        github_matches = re.findall(GITHUB_ISSUE_PATTERN, text)
        result['github'] = list({int(m) for m in github_matches})
    return result

def fetch_issues_for_commit(commit, repo_path, jira_url=None, jira_token=None, fetch_github_issues=False, issue_regex=DEFAULT_ISSUE_REGEX, issue_limit=DEFAULT_ISSUE_LIMIT, issue_cache=None):
    if issue_cache is None:
        issue_cache = {}
    message = commit.get('message', '')
    refs = extract_issue_refs(message, issue_regex, fetch_github_issues)
    issues = []
    if jira_url and jira_token:
        issues.extend(fetch_issues_by_keys(refs['jira'], jira_url, jira_token, issue_limit, issue_cache))
    if fetch_github_issues and repo_path:
        for number in refs['github']:
            issue = fetch_github_issue(number, repo_path, issue_limit)
            if issue:
                issues.append(issue)
    return issues

def fetch_issues_by_keys(keys, jira_url, jira_token, issue_limit=DEFAULT_ISSUE_LIMIT, issue_cache=None):
    if issue_cache is None:
        issue_cache = {}
    issues = []
    unique_keys = list(dict.fromkeys(keys))
    to_fetch = [k for k in unique_keys if k not in issue_cache]
    from_cache = [k for k in unique_keys if k in issue_cache]
    if to_fetch:
        logger.info('Fetching {} new Jira issues: {}', len(to_fetch), to_fetch)
    if from_cache:
        logger.debug('Using {} cached Jira issues: {}', len(from_cache), from_cache)
    for key in unique_keys:
        if key in issue_cache:
            issues.append(issue_cache[key])
        else:
            issue = fetch_jira_issue(key, jira_url, jira_token, issue_limit)
            if issue:
                issue_cache[key] = issue
                issues.append(issue)
    return issues
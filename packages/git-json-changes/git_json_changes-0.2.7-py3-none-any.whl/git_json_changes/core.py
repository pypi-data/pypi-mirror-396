from loguru import logger
from git_json_changes.constants import DEFAULT_DIFF_LIMIT, DEFAULT_PR_COMMENT_LIMIT, DEFAULT_ISSUE_LIMIT, DEFAULT_ISSUE_REGEX, ENV_GITHUB_TOKEN, ENV_JIRA_URL, ENV_JIRA_TOKEN
from git_json_changes.utils import iso_timestamp, resolve_env_value
from git_json_changes.git_module import open_repo, cleanup_temp_repo, get_commits, get_repo_url
from git_json_changes.pr_module import get_pull_requests, get_pr_commit_mapping
from git_json_changes.issue_module import fetch_issues_for_commit, extract_issue_refs, fetch_issues_by_keys

def generate_changes(ref_from, ref_to, repo_path=None, github_token=None, jira_url=None, jira_token=None, fetch_prs=True, fetch_github_issues=False, fetch_jira_from_prs=True, issue_regex=DEFAULT_ISSUE_REGEX, diff_limit=DEFAULT_DIFF_LIMIT, pr_comment_limit=DEFAULT_PR_COMMENT_LIMIT, issue_limit=DEFAULT_ISSUE_LIMIT):
    logger.info('Starting git-json-changes: {} -> {}', ref_from, ref_to)
    github_token = resolve_env_value(github_token, ENV_GITHUB_TOKEN)
    jira_url = resolve_env_value(jira_url, ENV_JIRA_URL)
    jira_token = resolve_env_value(jira_token, ENV_JIRA_TOKEN)
    fetch_jira = bool(jira_url and jira_token)
    if jira_url and (not jira_token):
        logger.error("Jira URL provided but JIRA token is missing.\n\nTo set up Jira authentication:\n\nFor Jira Server/Data Center:\n  1. Go to your Jira profile -> Personal Access Tokens\n  2. Click 'Create token', name it (e.g., 'git-json-changes')\n  3. Copy the token immediately\n\nFor Jira Cloud:\n  1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens\n  2. Click 'Create API token', name it\n  3. Copy the token immediately\n\nSet the credentials:\n  export JIRA_URL='https://jira.company.com'\n  export JIRA_PERSONAL_TOKEN='your_token_here'\nOr pass them directly: generate_changes(..., jira_url='...', jira_token='...')")
        fetch_jira = False
    elif jira_token and (not jira_url):
        logger.error("Jira token provided but JIRA_URL is missing.\n\nSet the Jira URL:\n  export JIRA_URL='https://jira.company.com'\nOr pass it directly: generate_changes(..., jira_url='https://...')")
        fetch_jira = False
    logger.info('Opening repository: {}', repo_path or 'current directory')
    repo, temp_dir = open_repo(repo_path)
    repo_working_dir = temp_dir or repo.working_dir
    logger.debug('Jira integration: {}', 'enabled' if fetch_jira else 'disabled')
    stats = {'commits': 0, 'prs': 0, 'pr_comments': 0, 'jira_issues': 0, 'jira_comments': 0, 'github_issues': 0}
    issue_cache = {}
    try:
        logger.info('Fetching commits...')
        commits = get_commits(repo, ref_from, ref_to, diff_limit)
        stats['commits'] = len(commits)
        logger.info('Found {} commits', len(commits))
        prs = []
        pr_commit_map = {}
        if fetch_prs:
            logger.info('Fetching pull requests...')
            prs = get_pull_requests(repo_working_dir, ref_from, ref_to, github_token, pr_comment_limit)
            stats['prs'] = len(prs)
            stats['pr_comments'] = sum((len(pr.get('comments', [])) for pr in prs))
            logger.info('Found {} PRs with {} comments', len(prs), stats['pr_comments'])
            pr_commit_map = get_pr_commit_mapping(prs)
            if fetch_jira and fetch_jira_from_prs:
                logger.info('Extracting Jira issues from PRs...')
                for pr in prs:
                    pr['issues'] = _extract_issues_from_pr(pr, jira_url, jira_token, issue_regex, issue_limit, issue_cache)
                    stats['jira_issues'] += len(pr['issues'])
                    stats['jira_comments'] += sum((len(issue.get('comments', [])) for issue in pr['issues']))
                    if pr['issues']:
                        logger.debug('PR #{}: {} Jira issues', pr['number'], len(pr['issues']))
        logger.info('Processing {} commits for issue references...', len(commits))
        for commit in commits:
            issues = fetch_issues_for_commit(commit, repo_working_dir, jira_url if fetch_jira else None, jira_token if fetch_jira else None, fetch_github_issues, issue_regex, issue_limit, issue_cache)
            commit['issues'] = issues
            jira_count = sum((1 for i in issues if i.get('source') == 'jira'))
            github_count = sum((1 for i in issues if i.get('source') == 'github'))
            stats['jira_issues'] += jira_count
            stats['jira_comments'] += sum((len(issue.get('comments', [])) for issue in issues if issue.get('source') == 'jira'))
            stats['github_issues'] += github_count
            if issues:
                logger.debug('Commit {}: {} Jira, {} GitHub issues', commit['short_hash'], jira_count, github_count)
        result = _build_output(ref_from, ref_to, get_repo_url(repo), prs, commits, pr_commit_map)
        result['meta']['stats'] = stats
        logger.info('Complete: {} commits, {} PRs, {} PR comments, {} Jira issues ({} comments), {} GitHub issues', stats['commits'], stats['prs'], stats['pr_comments'], stats['jira_issues'], stats['jira_comments'], stats['github_issues'])
        return result
    finally:
        cleanup_temp_repo(temp_dir)

def _extract_issues_from_pr(pr, jira_url, jira_token, issue_regex, issue_limit, issue_cache):
    text_parts = [pr.get('title', ''), pr.get('body', '')]
    for comment in pr.get('comments', []):
        text_parts.append(comment.get('body', ''))
    all_text = '\n'.join(text_parts)
    refs = extract_issue_refs(all_text, issue_regex, include_github=False)
    return fetch_issues_by_keys(refs['jira'], jira_url, jira_token, issue_limit, issue_cache)

def _build_output(ref_from, ref_to, repo_url, prs, commits, pr_commit_map):
    commits_dict = {}
    for commit in commits:
        commit_hash = commit['hash']
        pr_number = None
        for pr in prs:
            if pr.get('merge_commit') == commit_hash:
                pr_number = pr['number']
                break
        issue_ids = [_get_issue_id(issue) for issue in commit.get('issues', [])]
        commits_dict[commit_hash] = {'hash': commit['hash'], 'short_hash': commit['short_hash'], 'author': commit['author'], 'date': commit['date'], 'message': commit['message'], 'pr_number': pr_number, 'issues': issue_ids, 'files': commit['files']}
    prs_dict = {}
    for pr in prs:
        pr_number = pr['number']
        commit_hashes = []
        if pr.get('merge_commit') and pr['merge_commit'] in commits_dict:
            commit_hashes.append(pr['merge_commit'])
        issue_ids = [_get_issue_id(issue) for issue in pr.get('issues', [])]
        prs_dict[pr_number] = {'number': pr['number'], 'title': pr['title'], 'author': pr['author'], 'state': pr['state'], 'created_at': pr.get('created_at'), 'merged_at': pr.get('merged_at'), 'url': pr['url'], 'body': pr['body'], 'merge_commit': pr.get('merge_commit'), 'comments': pr['comments'], 'issues': issue_ids, 'commits': commit_hashes}
    issues_dict = {}
    all_issues = {}
    for commit in commits:
        for issue in commit.get('issues', []):
            issue_id = _get_issue_id(issue)
            if issue_id not in all_issues:
                all_issues[issue_id] = issue
    for pr in prs:
        for issue in pr.get('issues', []):
            issue_id = _get_issue_id(issue)
            if issue_id not in all_issues:
                all_issues[issue_id] = issue
    for issue_id, issue in all_issues.items():
        commit_hashes = [commit_hash for commit_hash, commit in commits_dict.items() if issue_id in commit.get('issues', [])]
        pr_numbers = [pr_number for pr_number, pr in prs_dict.items() if issue_id in pr.get('issues', [])]
        if issue.get('source') == 'jira':
            issues_dict[issue_id] = {'source': issue['source'], 'key': issue['key'], 'url': issue['url'], 'summary': issue['summary'], 'status': issue['status'], 'created_at': issue.get('created_at'), 'description': issue['description'], 'comments': issue['comments'], 'pull_requests': pr_numbers, 'commits': commit_hashes}
        else:
            issues_dict[issue_id] = {'source': issue['source'], 'number': issue['number'], 'url': issue['url'], 'summary': issue.get('summary', issue.get('title', '')), 'status': issue.get('status', issue.get('state', '')), 'created_at': issue.get('created_at'), 'description': issue.get('description', issue.get('body', '')), 'comments': issue['comments'], 'pull_requests': pr_numbers, 'commits': commit_hashes}
    return {'meta': {'ref_from': ref_from, 'ref_to': ref_to, 'repository': repo_url, 'generated_at': iso_timestamp()}, 'issues': issues_dict, 'pull_requests': prs_dict, 'commits': commits_dict}

def _get_issue_id(issue):
    source = issue.get('source')
    if source == 'jira':
        return issue.get('key')
    elif source == 'github':
        return f"gh-{issue.get('number')}"
    return None
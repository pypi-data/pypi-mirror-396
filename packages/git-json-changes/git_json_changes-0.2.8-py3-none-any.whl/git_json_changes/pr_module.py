import json
import subprocess
import re
from loguru import logger
from git_json_changes.constants import DEFAULT_PR_COMMENT_LIMIT
from git_json_changes.utils import get_byte_size

def is_gh_available():
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except FileNotFoundError:
        logger.error('GitHub CLI (gh) is not installed.\n\nTo install gh CLI:\n  - Visit: https://cli.github.com/\n  - Or use package manager: brew install gh, apt install gh, yay -S gh, etc.\n\nAfter installation, authenticate with: gh auth login')
        return False
    except subprocess.TimeoutExpired:
        return False

def get_pull_requests(repo_path, ref_from, ref_to, github_token=None, comment_limit=DEFAULT_PR_COMMENT_LIMIT):
    if not is_gh_available():
        logger.warning('gh CLI not available, skipping PR fetching')
        return []
    prs = _get_prs_in_range(repo_path, ref_from, ref_to)
    logger.debug('Found {} PR numbers in range', len(prs))
    result = []
    for pr_number in prs:
        logger.info('Fetching PR #{}', pr_number)
        pr_data = _fetch_pr_details(repo_path, pr_number, comment_limit)
        if pr_data:
            logger.debug('PR #{}: {} comments fetched', pr_number, len(pr_data.get('comments', [])))
            result.append(pr_data)
        else:
            logger.warning('Failed to fetch PR #{}', pr_number)
    return result

def _get_prs_in_range(repo_path, ref_from, ref_to):
    try:
        result = subprocess.run(['gh', 'pr', 'list', '--state', 'merged', '--json', 'number,mergeCommit', '--limit', '1000'], capture_output=True, text=True, timeout=60, cwd=repo_path)
        if result.returncode != 0:
            return []
        prs_data = json.loads(result.stdout)
        git_result = subprocess.run(['git', 'log', '--format=%H', f'{ref_from}..{ref_to}'], capture_output=True, text=True, timeout=30, cwd=repo_path)
        if git_result.returncode != 0:
            return []
        commits_in_range = set(git_result.stdout.strip().split('\n'))
        pr_numbers = []
        for pr in prs_data:
            if pr.get('mergeCommit') and pr['mergeCommit'].get('oid') in commits_in_range:
                pr_numbers.append(pr['number'])
        return pr_numbers
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return []

def _fetch_pr_details(repo_path, pr_number, comment_limit):
    try:
        result = subprocess.run(['gh', 'pr', 'view', str(pr_number), '--json', 'number,title,author,state,url,body,comments,mergeCommit,createdAt,mergedAt'], capture_output=True, text=True, timeout=30, cwd=repo_path)
        if result.returncode != 0:
            return None
        pr = json.loads(result.stdout)
        pr_data = {'number': pr['number'], 'title': pr['title'], 'author': pr['author']['login'] if pr.get('author') else None, 'state': pr['state'].lower(), 'created_at': pr.get('createdAt'), 'merged_at': pr.get('mergedAt'), 'url': pr['url'], 'body': pr.get('body') or '', 'merge_commit': pr.get('mergeCommit', {}).get('oid'), 'comments': _process_comments(pr.get('comments', []), comment_limit, pr.get('body') or ''), 'commits': []}
        return pr_data
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None

def _process_comments(comments, limit, body_text):
    body_size = get_byte_size(body_text)
    remaining = limit - body_size
    if remaining <= 0:
        return []
    sorted_comments = sorted(comments, key=lambda c: c.get('createdAt', ''), reverse=True)
    result = []
    total = 0
    for comment in sorted_comments:
        comment_body = comment.get('body') or ''
        comment_size = get_byte_size(comment_body)
        if total + comment_size > remaining:
            break
        result.append({'author': comment.get('author', {}).get('login'), 'date': comment.get('createdAt'), 'body': comment_body})
        total += comment_size
    return result

def get_pr_commit_mapping(prs):
    mapping = {}
    for pr in prs:
        if pr.get('merge_commit'):
            mapping[pr['merge_commit']] = pr['number']
    return mapping
import requests
from loguru import logger
from git_json_changes.constants import DEFAULT_ISSUE_LIMIT, HTTP_TIMEOUT, SSL_VERIFY
from git_json_changes.utils import get_byte_size

def fetch_jira_issue(key, jira_url, jira_token, content_limit=DEFAULT_ISSUE_LIMIT):
    logger.info('Fetching Jira issue: {}', key)
    base_url = jira_url.rstrip('/')
    api_url = f'{base_url}/rest/api/2/issue/{key}'
    headers = {'Authorization': f'Bearer {jira_token}', 'Content-Type': 'application/json'}
    try:
        response = requests.get(api_url, headers=headers, params={'fields': 'summary,status,description,comment,created,updated'}, timeout=HTTP_TIMEOUT, verify=SSL_VERIFY)
    except requests.RequestException as e:
        logger.error('Jira request failed for {}: {}', key, e)
        return None
    if response.status_code != 200:
        logger.warning('Jira API error for {}: {} - {}', key, response.status_code, response.text[:200])
        return None
    data = response.json()
    fields = data.get('fields', {})
    raw_comments = fields.get('comment', {}).get('comments', [])
    issue = {'source': 'jira', 'key': key, 'url': f'{base_url}/browse/{key}', 'summary': fields.get('summary'), 'status': fields.get('status', {}).get('name'), 'created_at': fields.get('created'), 'updated_at': fields.get('updated'), 'description': fields.get('description') or '', 'comments': []}
    description_size = get_byte_size(issue['description'])
    remaining = content_limit - description_size
    if remaining > 0:
        issue['comments'] = _process_jira_comments(raw_comments, remaining)
    logger.debug('Jira {}: status={}, {} comments fetched', key, issue['status'], len(issue['comments']))
    return issue

def _process_jira_comments(comments, limit):
    sorted_comments = sorted(comments, key=lambda c: c.get('created', ''), reverse=True)
    result = []
    total = 0
    for comment in sorted_comments:
        body = comment.get('body') or ''
        size = get_byte_size(body)
        if total + size > limit:
            break
        result.append({'author': comment.get('author', {}).get('displayName'), 'date': comment.get('created'), 'body': body})
        total += size
    return result
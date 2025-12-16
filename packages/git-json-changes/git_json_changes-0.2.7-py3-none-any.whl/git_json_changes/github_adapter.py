import json
import subprocess
from git_json_changes.constants import DEFAULT_ISSUE_LIMIT
from git_json_changes.utils import get_byte_size

def fetch_github_issue(issue_number, repo_path, content_limit=DEFAULT_ISSUE_LIMIT):
    try:
        result = subprocess.run(['gh', 'issue', 'view', str(issue_number), '--json', 'number,title,state,url,body,comments,createdAt'], capture_output=True, text=True, timeout=30, cwd=repo_path)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        issue = {'source': 'github', 'key': f"#{data['number']}", 'number': data['number'], 'url': data['url'], 'summary': data['title'], 'status': data['state'].lower(), 'created_at': data.get('createdAt'), 'description': data.get('body') or '', 'comments': []}
        description_size = get_byte_size(issue['description'])
        remaining = content_limit - description_size
        if remaining > 0:
            raw_comments = data.get('comments', [])
            issue['comments'] = _process_github_comments(raw_comments, remaining)
        return issue
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None

def _process_github_comments(comments, limit):
    sorted_comments = sorted(comments, key=lambda c: c.get('createdAt', ''), reverse=True)
    result = []
    total = 0
    for comment in sorted_comments:
        body = comment.get('body') or ''
        size = get_byte_size(body)
        if total + size > limit:
            break
        result.append({'author': comment.get('author', {}).get('login'), 'date': comment.get('createdAt'), 'body': body})
        total += size
    return result
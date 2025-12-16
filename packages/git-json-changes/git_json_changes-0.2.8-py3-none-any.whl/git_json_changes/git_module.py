import os
import tempfile
import shutil
from datetime import datetime, timezone
from git import Repo
from loguru import logger
from git_json_changes.constants import DEFAULT_DIFF_LIMIT
from git_json_changes.utils import truncate_to_limit, get_byte_size

def open_repo(repo_path=None):
    if repo_path is None:
        repo_path = os.getcwd()
    if repo_path.startswith(('http://', 'https://', 'git@', 'ssh://')):
        logger.info('Cloning repository from URL...')
        temp_dir = tempfile.mkdtemp(prefix='git_json_changes_')
        repo = Repo.clone_from(repo_path, temp_dir)
        logger.debug('Cloned to {}', temp_dir)
        return (repo, temp_dir)
    logger.debug('Opening local repository: {}', repo_path)
    return (Repo(repo_path), None)

def cleanup_temp_repo(temp_dir):
    if temp_dir and os.path.exists(temp_dir):
        try:
            logger.debug('Cleaning up temporary repository: {}', temp_dir)
            shutil.rmtree(temp_dir, ignore_errors=False, onerror=_handle_remove_readonly)
        except Exception as e:
            logger.warning('Failed to clean up temp directory {}: {}', temp_dir, e)

def _handle_remove_readonly(func, path, exc):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def get_commits(repo, ref_from, ref_to, diff_limit=DEFAULT_DIFF_LIMIT):
    from git.exc import GitCommandError
    logger.debug('Getting commits: {}..{}', ref_from, ref_to)
    try:
        commits = list(repo.iter_commits(f'{ref_from}..{ref_to}'))
    except GitCommandError as e:
        if 'bad revision' in str(e):
            logger.error("Git reference not found: '{}' or '{}'\n\nPossible solutions:\n  1. Fetch latest refs from remote:\n     git fetch --all --tags\n\n  2. List available tags:\n     git tag\n\n  3. List available branches:\n     git branch -a\n\n  4. Use commit hashes instead:\n     git log --oneline -20\n     Then use: git-json-changes abc123 def456 ...", ref_from, ref_to)
        raise
    result = []
    for commit in commits:
        commit_data = _build_commit_data(repo, commit, diff_limit)
        result.append(commit_data)
    total_files = sum((len(c['files']) for c in result))
    logger.debug('Processed {} commits with {} files total', len(result), total_files)
    return result

def _build_commit_data(repo, commit, diff_limit):
    if commit.parents:
        parent = commit.parents[0]
        diffs = parent.diff(commit, create_patch=True)
    else:
        diffs = commit.diff(None, create_patch=True)
    files = _get_files_with_diffs(diffs, diff_limit)
    return {'hash': commit.hexsha, 'short_hash': commit.hexsha[:7], 'author': f'{commit.author.name} <{commit.author.email}>', 'date': datetime.fromtimestamp(commit.committed_date, tz=timezone.utc).isoformat(), 'message': commit.message.strip(), 'files': files, 'issues': []}

def _get_files_with_diffs(diffs, diff_limit):
    files = []
    for diff in diffs:
        file_data = {'path': diff.b_path or diff.a_path, 'status': _get_diff_status(diff), 'additions': 0, 'deletions': 0, 'diff': None}
        diff_text = ''
        if diff.diff:
            diff_text = diff.diff.decode('utf-8', errors='replace')
            file_data['additions'], file_data['deletions'] = _count_lines(diff_text)
        file_data['_diff_text'] = diff_text
        file_data['_diff_size'] = get_byte_size(diff_text)
        files.append(file_data)
    files.sort(key=lambda f: f['_diff_size'])
    total_size = 0
    for f in files:
        if total_size + f['_diff_size'] <= diff_limit:
            f['diff'] = f['_diff_text']
            total_size += f['_diff_size']
        del f['_diff_text']
        del f['_diff_size']
    return files

def _get_diff_status(diff):
    if diff.new_file:
        return 'added'
    elif diff.deleted_file:
        return 'deleted'
    elif diff.renamed_file:
        return 'renamed'
    else:
        return 'modified'

def _count_lines(diff_text):
    additions = 0
    deletions = 0
    for line in diff_text.split('\n'):
        if line.startswith('+') and (not line.startswith('+++')):
            additions += 1
        elif line.startswith('-') and (not line.startswith('---')):
            deletions += 1
    return (additions, deletions)

def get_repo_url(repo):
    try:
        if repo.remotes:
            return repo.remotes.origin.url
    except Exception:
        pass
    return None
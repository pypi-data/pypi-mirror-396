import json
import sys
import warnings
import click
import urllib3
from loguru import logger
from git_json_changes.constants import DEFAULT_DIFF_LIMIT, DEFAULT_PR_COMMENT_LIMIT, DEFAULT_ISSUE_LIMIT, DEFAULT_ISSUE_REGEX
from git_json_changes.core import generate_changes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@click.command()
@click.argument('ref_from')
@click.argument('ref_to')
@click.option('-o', '--output', required=True, help='Output JSON file path')
@click.option('-r', '--repo', default=None, help='Repository path or URL (default: current directory)')
@click.option('--github-token', default=None, help='GitHub token or env var name (default: $GITHUB_TOKEN)')
@click.option('--jira-url', default=None, help='Jira instance URL or env var name (default: $JIRA_URL)')
@click.option('--jira-token', default=None, help='Jira API token or env var name (default: $JIRA_PERSONAL_TOKEN)')
@click.option('--issue-regex', default=DEFAULT_ISSUE_REGEX, help=f'Regex for issue keys (default: {DEFAULT_ISSUE_REGEX})')
@click.option('--github-issues/--no-github-issues', default=False, help='Fetch GitHub Issues')
@click.option('--diff-limit', default=DEFAULT_DIFF_LIMIT, type=int, help=f'Max bytes for diffs (default: {DEFAULT_DIFF_LIMIT})')
@click.option('--pr-comment-limit', default=DEFAULT_PR_COMMENT_LIMIT, type=int, help=f'Max bytes for PR comments (default: {DEFAULT_PR_COMMENT_LIMIT})')
@click.option('--issue-limit', default=DEFAULT_ISSUE_LIMIT, type=int, help=f'Max bytes for issue content (default: {DEFAULT_ISSUE_LIMIT})')
@click.option('--no-prs', is_flag=True, default=False, help='Skip PR fetching')
@click.option('--no-jira', is_flag=True, default=False, help='Skip Jira integration')
@click.option('--no-jira-from-prs', is_flag=True, default=False, help='Skip Jira extraction from PR content')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Enable debug output')
def main(ref_from, ref_to, output, repo, github_token, jira_url, jira_token, issue_regex, github_issues, diff_limit, pr_comment_limit, issue_limit, no_prs, no_jira, no_jira_from_prs, verbose):
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level='DEBUG')
    result = generate_changes(ref_from=ref_from, ref_to=ref_to, repo_path=repo, github_token=github_token, jira_url=None if no_jira else jira_url, jira_token=None if no_jira else jira_token, fetch_prs=not no_prs, fetch_github_issues=github_issues, fetch_jira_from_prs=not no_jira_from_prs and (not no_jira), issue_regex=issue_regex, diff_limit=diff_limit, pr_comment_limit=pr_comment_limit, issue_limit=issue_limit)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    stats = result.get('meta', {}).get('stats', {})
    click.echo(f'Output written to: {output}')
    click.echo(f"  Commits: {stats.get('commits', 0)}")
    click.echo(f"  PRs: {stats.get('prs', 0)}")
    click.echo(f"  PR comments: {stats.get('pr_comments', 0)}")
    click.echo(f"  Jira issues: {stats.get('jira_issues', 0)}")
    click.echo(f"  Jira comments: {stats.get('jira_comments', 0)}")
    click.echo(f"  GitHub issues: {stats.get('github_issues', 0)}")
if __name__ == '__main__':
    main()
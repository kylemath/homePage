import requests
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup
import os
import json
from typing import List, Dict, Optional, Tuple

KIND_DEFAULT = 'project'
CATALOGUE_FILE = 'catalogue_data.json'
CATALOGUE_ENTRY_FILE = 'catalogue.json'
KNOWN_KINDS = {'project', 'longform', 'page'}

def get_github_repos(username, token=None):
    """Fetch all repositories for a given username, sorted by commit/creation/name."""
    headers = {
        'Accept': 'application/vnd.github.mercy-preview+json'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{username}/repos?page={page}&per_page=100&sort=updated'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        payload = response.json()
        if not payload:
            break
        repos.extend(payload)
        page += 1

    original_repos = [repo for repo in repos if not repo.get('fork', False)]

    for repo in original_repos:
        commits_url = f'https://api.github.com/repos/{username}/{repo["name"]}/commits'
        response = requests.get(commits_url, headers=headers)
        if response.status_code == 200 and response.json():
            last_commit = response.json()[0]['commit']['committer']['date']
            repo['last_commit_date'] = datetime.strptime(last_commit, '%Y-%m-%dT%H:%M:%SZ')
            repo['last_commit_ts'] = repo['last_commit_date'].timestamp()
        else:
            repo['last_commit_date'] = None
            repo['last_commit_ts'] = 0
        created_at = repo.get('created_at')
        if created_at:
            created_dt = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        else:
            created_dt = datetime(1970, 1, 1, tzinfo=timezone.utc)
        repo['created_at_dt'] = created_dt
        repo['created_at_ts'] = created_dt.timestamp()

    return sorted(
        original_repos,
        key=lambda repo: (
            -repo['last_commit_ts'],
            -repo['created_at_ts'],
            repo['name'].lower()
        )
    )

def fetch_catalogue_metadata(username: str, repo: Dict) -> Optional[Dict]:
    """Attempt to load per-repo catalogue metadata JSON.
    
    Checks in this order:
    1. Public deployment URL (homepage) - for private repos with public sites
    2. GitHub raw URLs - for public repos
    """
    
    # First, try the repo's homepage if it exists (for public deployments like Netlify)
    homepage = repo.get('homepage')
    if homepage and homepage.strip():
        homepage = homepage.rstrip('/')
        # Try multiple common locations on the public site
        catalogue_urls = [
            f"{homepage}/{CATALOGUE_ENTRY_FILE}",
            f"{homepage}/assets/{CATALOGUE_ENTRY_FILE}",
            f"{homepage}/public/{CATALOGUE_ENTRY_FILE}",
            f"{homepage}/.well-known/{CATALOGUE_ENTRY_FILE}"
        ]
        for url in catalogue_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return json.loads(response.text)
            except (requests.RequestException, json.JSONDecodeError):
                continue
    
    # Fallback to GitHub raw URLs (for public repos)
    branches = [repo.get('default_branch') or 'main', 'main', 'master']
    for branch in branches:
        if not branch:
            continue
        raw_url = f'https://raw.githubusercontent.com/{username}/{repo["name"]}/{branch}/{CATALOGUE_ENTRY_FILE}'
        response = requests.get(raw_url)
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return None
    return None

def determine_kind(metadata: Dict, repo_topics: List[str]) -> Tuple[str, List[str]]:
    """Derive primary kind and topic hierarchy."""
    kind = metadata.get('kind')
    path: List[str] = []
    if kind:
        return kind, path
    for topic in repo_topics or []:
        parts = topic.split('-')
        if not parts:
            continue
        candidate = parts[0]
        if candidate in KNOWN_KINDS or not kind:
            kind = candidate
            path = parts[1:]
            break
    if not kind:
        kind = KIND_DEFAULT
    return kind, path

def resolve_screenshot_url(username: str, repo: Dict, metadata: Dict) -> str:
    """Return an absolute screenshot URL, normalizing repo-relative paths.
    
    Priority:
    1. Absolute URLs in metadata (http/https) - use as-is
    2. Relative paths in metadata - resolve based on repo homepage or GitHub
    3. Default screenshot.png from GitHub
    """
    default_branch = repo.get('default_branch') or 'main'
    screenshot = metadata.get('screenshot')
    homepage = repo.get('homepage', '').rstrip('/')

    if isinstance(screenshot, str) and screenshot.strip():
        trimmed = screenshot.strip()
        
        # If it's already an absolute URL, use it
        if trimmed.startswith('http://') or trimmed.startswith('https://'):
            return trimmed
        
        # Remove leading ./
        if trimmed.startswith('./'):
            trimmed = trimmed[2:]
        
        # If we have a homepage (public deployment), resolve relative to it
        if homepage and trimmed:
            return f'{homepage}/{trimmed}'
        
        # Otherwise resolve relative to GitHub
        if trimmed:
            return f'https://raw.githubusercontent.com/{username}/{repo["name"]}/{default_branch}/{trimmed}'

    # Default: try homepage first, then GitHub
    if homepage:
        return f'{homepage}/screenshot.png'
    
    return f'https://raw.githubusercontent.com/{username}/{repo["name"]}/{default_branch}/screenshot.png'


def build_catalogue_entries(username: str, repos: List[Dict]) -> List[Dict]:
    entries = []
    for repo in repos:
        metadata = fetch_catalogue_metadata(username, repo) or {}
        topics = repo.get('topics', [])
        kind, topic_path = determine_kind(metadata, topics)
        categories = metadata.get('categories', [])
        if topic_path:
            categories = categories + topic_path
        entry = {
            'id': metadata.get('id') or repo['name'],
            'title': metadata.get('title') or repo['name'],
            'oneLiner': metadata.get('oneLiner') or repo.get('description') or 'GitHub repository',
            'categories': categories,
            'tags': metadata.get('tags', []),
            'demoUrl': metadata.get('demoUrl') or repo.get('homepage') or repo['html_url'],
            'githubUrl': repo['html_url'],
            'screenshot': resolve_screenshot_url(username, repo, metadata),
            'status': metadata.get('status'),
            'kind': kind,
            'topicHierarchy': topic_path,
            'repoTopics': topics,
            'lastCommit': repo['last_commit_date'].isoformat() if repo.get('last_commit_date') else None,
            'createdAt': repo.get('created_at')
        }
        entries.append(entry)
    return entries

def write_catalogue_file(entries: List[Dict]):
    if not entries:
        print(f"⚠️  No entries found - not overwriting {CATALOGUE_FILE}")
        print("   This usually means GitHub API rate limiting.")
        print("   Set GITHUB_TOKEN environment variable and try again.")
        return
    
    payload = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'items': entries
    }
    with open(CATALOGUE_FILE, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)


def update_html_file(repos, html_file):
    """Update the index.html file with sorted repositories."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find the projects section
    projects_section = soup.find('h2', {'id': 'projects'}).find_next('ul')
    
    # Create new repository list items
    new_items = []
    for repo in repos:
        description = repo['description'] or 'GitHub repository'
        li = soup.new_tag('li')
        a = soup.new_tag('a', href=repo['html_url'], target='_blank')
        a.string = repo['name']
        li.append(a)
        li.append(f' - {description}')
        new_items.append(str(li))

    # Replace old list with new one
    projects_html = '<ul>\n    ' + '\n    '.join(new_items) + '\n</ul>'
    
    # Replace the old projects section with the new one
    old_projects_pattern = r'<h2 id="projects">Recent Projects</h2>\s*<ul>.*?</ul>'
    new_projects_section = f'<h2 id="projects">Recent Projects</h2>\n{projects_html}'
    updated_content = re.sub(old_projects_pattern, new_projects_section, content, flags=re.DOTALL)

    # Write the updated content back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == '__main__':
    # GitHub username
    USERNAME = 'kylemath'
    
    # Optional: GitHub personal access token (recommended to avoid rate limits)
    # Create one at https://github.com/settings/tokens
    # Set this as an environment variable named GITHUB_TOKEN
    TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Path to your index.html file
    HTML_FILE = 'index.html'
    
    # Get sorted repositories
    repos = get_github_repos(USERNAME, TOKEN)
    
    # Build catalogue data and write to file
    catalogue_entries = build_catalogue_entries(USERNAME, repos)
    write_catalogue_file(catalogue_entries)
    
    # Filter repos for textual list display
    project_repos = [repo for repo in repos if True]
    
    # Update the HTML file
    update_html_file(project_repos, HTML_FILE)
    
    print(f"Updated {HTML_FILE} with {len(project_repos)} repositories, sorted by last commit date.")
    print(f"Wrote catalogue metadata for {len(catalogue_entries)} repositories to {CATALOGUE_FILE}.")
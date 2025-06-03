import requests
import os
from datetime import datetime
import re
from bs4 import BeautifulSoup

def get_github_forks(username, token=None):
    """Fetch all forked repositories for a given username."""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Get all repositories
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{username}/repos?page={page}&per_page=100'
        response = requests.get(url, headers=headers)
        if response.status_code != 200 or not response.json():
            break
        repos.extend(response.json())
        page += 1

    # Filter to only forked repositories and get detailed info
    forked_repos = []
    for repo in repos:
        if repo.get('fork', False):
            # Get detailed repository information which includes parent info
            detail_url = f'https://api.github.com/repos/{repo["full_name"]}'
            detail_response = requests.get(detail_url, headers=headers)
            if detail_response.status_code == 200:
                detailed_repo = detail_response.json()
                forked_repos.append(detailed_repo)
            else:
                forked_repos.append(repo)  # fallback to basic info
    
    return forked_repos

def analyze_fork(repo, username, headers):
    """Analyze a forked repository for contributions and commits ahead."""
    fork_name = repo['name']
    fork_full_name = repo['full_name']
    parent_full_name = repo['parent']['full_name'] if 'parent' in repo else None
    
    if not parent_full_name:
        return None
    
    analysis = {
        'name': fork_name,
        'description': repo.get('description', 'Contributor project'),
        'fork_url': repo['html_url'],
        'parent_url': repo['parent']['html_url'] if 'parent' in repo else None,
        'is_contributor_to_parent': False,
        'commits_ahead': 0,
        'commits_behind': 0,
        'last_fork_commit': None,
        'last_parent_commit': None,
        'significant_commits': []
    }
    
    # Check if user is a contributor to the parent repository
    try:
        contributors_url = f'https://api.github.com/repos/{parent_full_name}/contributors'
        response = requests.get(contributors_url, headers=headers)
        if response.status_code == 200:
            contributors = response.json()
            for contributor in contributors:
                if contributor['login'].lower() == username.lower():
                    analysis['is_contributor_to_parent'] = True
                    break
    except Exception as e:
        pass
    
    # Compare commits between fork and parent
    try:
        compare_url = f'https://api.github.com/repos/{parent_full_name}/compare/{repo["parent"]["default_branch"]}...{username}:{repo["default_branch"]}'
        response = requests.get(compare_url, headers=headers)
        if response.status_code == 200:
            compare_data = response.json()
            analysis['commits_ahead'] = compare_data.get('ahead_by', 0)
            analysis['commits_behind'] = compare_data.get('behind_by', 0)
    except Exception as e:
        pass
    
    # Get last commit date for fork
    try:
        fork_commits_url = f'https://api.github.com/repos/{fork_full_name}/commits'
        response = requests.get(fork_commits_url, headers=headers)
        if response.status_code == 200 and response.json():
            analysis['last_fork_commit'] = response.json()[0]['commit']['committer']['date']
            analysis['last_fork_commit_parsed'] = datetime.strptime(analysis['last_fork_commit'], '%Y-%m-%dT%H:%M:%SZ')
    except Exception as e:
        analysis['last_fork_commit_parsed'] = datetime.min
    
    return analysis

def get_significant_forks(username, token=None):
    """Get significant forks (contributor projects) sorted by most recent commit."""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    forked_repos = get_github_forks(username, token)
    significant_forks = []
    
    for repo in forked_repos:
        try:
            analysis = analyze_fork(repo, username, headers)
            if analysis:
                # Ensure last_fork_commit_parsed is always set
                if 'last_fork_commit_parsed' not in analysis:
                    analysis['last_fork_commit_parsed'] = datetime.min
                
                # Consider a fork significant if:
                # 1. User is a contributor to parent, OR
                # 2. Fork has commits ahead
                is_significant = (
                    analysis['is_contributor_to_parent'] or 
                    analysis['commits_ahead'] > 0
                )
                
                if is_significant:
                    significant_forks.append(analysis)
        except Exception as e:
            continue
    
    # Sort by most recent commit date
    significant_forks.sort(key=lambda x: x.get('last_fork_commit_parsed', datetime.min), reverse=True)
    
    return significant_forks

def update_html_with_contributor_projects(contributor_projects, html_file):
    """Update the index.html file with contributor projects section."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create contributor projects HTML
    contributor_items = []
    for project in contributor_projects:
        description = project['description'] or 'Contributor project'
        
        # Add status indicators
        status_info = []
        if project['is_contributor_to_parent']:
            status_info.append("contributor to original")
        if project['commits_ahead'] > 0:
            status_info.append(f"{project['commits_ahead']} commits ahead")
        
        if status_info:
            description += f" ({', '.join(status_info)})"
        
        li_html = f'<li><a href="{project["fork_url"]}" target="_blank">{project["name"]}</a> - {description}</li>'
        contributor_items.append(li_html)

    contributor_html = '<ul>\n    ' + '\n    '.join(contributor_items) + '\n</ul>'
    
    # Check if contributor projects section already exists
    contributor_pattern = r'<h2 id="contributor-projects">Contributor Projects</h2>\s*<ul>.*?</ul>'
    
    if re.search(contributor_pattern, content, flags=re.DOTALL):
        # Update existing section
        new_contributor_section = f'<h2 id="contributor-projects">Contributor Projects</h2>\n{contributor_html}'
        updated_content = re.sub(contributor_pattern, new_contributor_section, content, flags=re.DOTALL)
    else:
        # Add new section after Recent Projects
        projects_pattern = r'(<h2 id="projects">Recent Projects</h2>\s*<ul>.*?</ul>)'
        new_contributor_section = f'\\1\n\n<hr>\n\n<h2 id="contributor-projects">Contributor Projects</h2>\n{contributor_html}'
        updated_content = re.sub(projects_pattern, new_contributor_section, content, flags=re.DOTALL)

    # Write the updated content back to the file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def main():
    USERNAME = 'kylemath'
    TOKEN = os.getenv('GITHUB_TOKEN')
    HTML_FILE = 'index.html'
    
    print(f"Getting contributor projects for {USERNAME}...")
    
    # Get significant forks (contributor projects)
    contributor_projects = get_significant_forks(USERNAME, TOKEN)
    
    print(f"Found {len(contributor_projects)} contributor projects:")
    for project in contributor_projects:
        status = []
        if project['is_contributor_to_parent']:
            status.append("contributor")
        if project['commits_ahead'] > 0:
            status.append(f"{project['commits_ahead']} commits ahead")
        status_str = f" ({', '.join(status)})" if status else ""
        
        commit_date = project.get('last_fork_commit_parsed', datetime.min)
        commit_date_str = commit_date.strftime('%Y-%m-%d') if commit_date != datetime.min else 'unknown'
        print(f"  - {project['name']}{status_str} - last commit: {commit_date_str}")
    
    # Update HTML file only if there are contributor projects to add
    if contributor_projects:
        update_html_with_contributor_projects(contributor_projects, HTML_FILE)
        print(f"Updated {HTML_FILE} with {len(contributor_projects)} contributor projects.")
    else:
        print("No contributor projects found - keeping existing content if any.")

if __name__ == '__main__':
    main() 
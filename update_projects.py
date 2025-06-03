import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os

def get_github_repos(username, token=None):
    """Fetch all repositories for a given username, sorted by last commit date."""
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

    # Filter out forked repositories
    original_repos = [repo for repo in repos if not repo.get('fork', False)]

    # Get last commit date for each repository
    for repo in original_repos:
        commits_url = f'https://api.github.com/repos/{username}/{repo["name"]}/commits'
        response = requests.get(commits_url, headers=headers)
        if response.status_code == 200 and response.json():
            last_commit = response.json()[0]['commit']['committer']['date']
            repo['last_commit_date'] = datetime.strptime(last_commit, '%Y-%m-%dT%H:%M:%SZ')
        else:
            repo['last_commit_date'] = datetime.min

    # Sort repositories by last commit date
    return sorted(original_repos, key=lambda x: x['last_commit_date'], reverse=True)

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
    
    # Update the HTML file
    update_html_file(repos, HTML_FILE)
    
    print(f"Updated {HTML_FILE} with {len(repos)} repositories, sorted by last commit date.") 
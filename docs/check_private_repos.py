#!/usr/bin/env python3
"""
Diagnostic script to check private repo configuration for homepage automation.
Run this to see which private repos need setup.
"""

import requests
import os
import json
from typing import List, Dict

GITHUB_USERNAME = 'kylemath'
CATALOGUE_ENTRY_FILE = 'catalogue.json'

def check_private_repos():
    """Check all private repos and their homepage/catalogue configuration."""
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ ERROR: GITHUB_TOKEN environment variable not set!")
        print("\nTo access private repos, you need to set GITHUB_TOKEN:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("\nCreate a token at: https://github.com/settings/tokens")
        print("Required scopes: 'repo' (full control of private repositories)")
        return
    
    print(f"✅ GITHUB_TOKEN is set\n")
    print("=" * 80)
    print("CHECKING PRIVATE REPOSITORIES")
    print("=" * 80)
    
    headers = {
        'Accept': 'application/vnd.github.mercy-preview+json',
        'Authorization': f'token {token}'
    }
    
    # Fetch all repos
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{GITHUB_USERNAME}/repos?page={page}&per_page=100'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ GitHub API error: {response.status_code}")
            if response.status_code == 401:
                print("   Token is invalid or expired. Create a new one at:")
                print("   https://github.com/settings/tokens")
            return
        
        payload = response.json()
        if not payload:
            break
        repos.extend(payload)
        page += 1
    
    # Filter private repos
    private_repos = [r for r in repos if r.get('private', False)]
    
    if not private_repos:
        print("\n✅ No private repos found (or token doesn't have access)")
        return
    
    print(f"\nFound {len(private_repos)} private repositories\n")
    
    issues_found = False
    
    for repo in private_repos:
        repo_name = repo['name']
        homepage = repo.get('homepage', '').strip()
        
        print(f"\n📦 {repo_name}")
        print(f"   URL: {repo['html_url']}")
        
        # Check 1: Homepage URL
        if not homepage:
            print("   ❌ No homepage URL set in GitHub!")
            print("      → Go to repo settings and add the deployment URL")
            issues_found = True
            continue
        else:
            print(f"   ✅ Homepage: {homepage}")
        
        # Check 2: catalogue.json accessibility
        homepage = homepage.rstrip('/')
        catalogue_urls = [
            f"{homepage}/{CATALOGUE_ENTRY_FILE}",
            f"{homepage}/assets/{CATALOGUE_ENTRY_FILE}",
            f"{homepage}/public/{CATALOGUE_ENTRY_FILE}",
        ]
        
        catalogue_found = False
        catalogue_data = None
        working_url = None
        
        for url in catalogue_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    catalogue_data = json.loads(response.text)
                    catalogue_found = True
                    working_url = url
                    break
            except (requests.RequestException, json.JSONDecodeError):
                continue
        
        if catalogue_found:
            print(f"   ✅ catalogue.json: {working_url}")
            
            # Check 3: Required fields
            required_fields = ['title', 'oneLiner', 'kind']
            missing_fields = [f for f in required_fields if not catalogue_data.get(f)]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields in catalogue.json: {', '.join(missing_fields)}")
                issues_found = True
            
            # Check 4: Kind field for correct tab
            kind = catalogue_data.get('kind', '')
            if kind not in ['page', 'longform', 'project']:
                print(f"   ⚠️  Invalid 'kind' field: '{kind}'")
                print(f"      → Should be 'page' (Apps tab), 'longform' (Writing tab), or 'project' (Projects tab)")
                issues_found = True
            else:
                tab_name = {'page': 'Apps', 'longform': 'Writing', 'project': 'Projects'}[kind]
                print(f"   ✅ Will appear in: {tab_name} tab")
            
            # Check 5: Screenshot
            screenshot = catalogue_data.get('screenshot', '')
            if screenshot:
                # Check if screenshot is accessible
                if screenshot.startswith('http'):
                    screenshot_url = screenshot
                else:
                    screenshot_url = f"{homepage}/{screenshot.lstrip('./')}"
                
                try:
                    resp = requests.head(screenshot_url, timeout=5)
                    if resp.status_code == 200:
                        print(f"   ✅ Screenshot: {screenshot_url}")
                    else:
                        print(f"   ❌ Screenshot not accessible: {screenshot_url} (HTTP {resp.status_code})")
                        issues_found = True
                except requests.RequestException:
                    print(f"   ❌ Screenshot not accessible: {screenshot_url}")
                    issues_found = True
            else:
                print(f"   ⚠️  No screenshot field - will use default")
        else:
            print(f"   ❌ catalogue.json NOT found at homepage!")
            print(f"      Tried: {catalogue_urls[0]}")
            print(f"      → Create catalogue.json in repo and deploy it")
            issues_found = True
    
    print("\n" + "=" * 80)
    
    if issues_found:
        print("\n⚠️  ISSUES FOUND - Fix the items marked with ❌ above")
        print("\nQuick fix guide:")
        print("1. Go to repo Settings → scroll to 'Website' → add your deployment URL")
        print("2. Create catalogue.json in repo root with:")
        print('   {"title":"...", "oneLiner":"...", "kind":"page", "screenshot":"screenshot.png"}')
        print("3. Add screenshot.png to repo root")
        print("4. Deploy/push changes")
        print("5. Run: python update_projects.py")
    else:
        print("\n✅ All private repos are properly configured!")
        print("\nTo update your homepage, run:")
        print("   python update_projects.py")
    
    print("=" * 80)

if __name__ == '__main__':
    check_private_repos()


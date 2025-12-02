#!/usr/bin/env python3
"""
Test script to show what happens when GITHUB_TOKEN is available.
Run this after setting GITHUB_TOKEN environment variable.

Usage:
    export GITHUB_TOKEN="ghp_your_token_here"
    python test_with_token.py
"""

import os
import requests
import json

def test_github_api_access():
    """Test GitHub API access with and without token."""
    username = 'kylemath'
    token = os.getenv('GITHUB_TOKEN')
    
    # Setup headers
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        print("✅ GITHUB_TOKEN found - testing with authentication")
    else:
        print("⚠️  No GITHUB_TOKEN - testing without authentication (public repos only)")
    
    # Fetch repos
    url = f'https://api.github.com/users/{username}/repos?per_page=100&sort=updated'
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        if response.status_code == 403:
            print("   Rate limited. Set GITHUB_TOKEN to increase limits.")
        return
    
    repos = response.json()
    
    # Analyze repos
    public_repos = [r for r in repos if not r.get('private', False)]
    private_repos = [r for r in repos if r.get('private', False)]
    
    print(f"\n📊 Repository Count:")
    print(f"   Public:  {len(public_repos)}")
    print(f"   Private: {len(private_repos)}")
    print(f"   Total:   {len(repos)}")
    
    # Find repos with homepage (potential Netlify sites)
    repos_with_homepage = [r for r in repos if r.get('homepage', '').strip()]
    private_with_homepage = [r for r in private_repos if r.get('homepage', '').strip()]
    
    print(f"\n🌐 Repos with Homepage URL:")
    print(f"   Total: {len(repos_with_homepage)}")
    print(f"   Private with homepage: {len(private_with_homepage)}")
    
    # Show private repos with Netlify sites
    if private_with_homepage:
        print(f"\n🔐 Private repos with public sites (will be auto-discovered):")
        for repo in private_with_homepage[:5]:  # Show first 5
            print(f"   • {repo['name']}")
            print(f"     Homepage: {repo['homepage']}")
            
            # Test if catalogue.json is accessible
            catalogue_url = f"{repo['homepage'].rstrip('/')}/catalogue.json"
            try:
                cat_response = requests.get(catalogue_url, timeout=5)
                if cat_response.status_code == 200:
                    cat_data = cat_response.json()
                    print(f"     ✅ catalogue.json found!")
                    print(f"        Kind: {cat_data.get('kind', 'not set')}")
                    print(f"        Title: {cat_data.get('title', 'not set')}")
                else:
                    print(f"     ⚠️  No catalogue.json at {catalogue_url}")
            except Exception as e:
                print(f"     ⚠️  Could not fetch catalogue.json")
            print()
        
        if len(private_with_homepage) > 5:
            print(f"   ... and {len(private_with_homepage) - 5} more")
    
    elif private_repos:
        print(f"\n💡 You have {len(private_repos)} private repos but none have homepage URLs set.")
        print("   To include them in the catalogue:")
        print("   1. Deploy to Netlify/Vercel")
        print("   2. Set the 'Website' field in GitHub repo settings")
        print("   3. Add catalogue.json to the deployed site")
    
    # Test rate limits
    rate_limit_url = 'https://api.github.com/rate_limit'
    rate_response = requests.get(rate_limit_url, headers=headers)
    if rate_response.status_code == 200:
        rate_data = rate_response.json()
        core_limit = rate_data['resources']['core']
        print(f"\n⏱️  API Rate Limit:")
        print(f"   Remaining: {core_limit['remaining']}/{core_limit['limit']}")
        print(f"   Limit type: {'Authenticated' if token else 'Anonymous'}")
        print(f"   {'(5000/hour with token)' if token else '(60/hour without token)'}")

def show_setup_instructions():
    """Show setup instructions if no token."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("\n" + "="*60)
        print("📖 TO ENABLE PRIVATE REPO DISCOVERY:")
        print("="*60)
        print("\n1. Create a GitHub token:")
        print("   https://github.com/settings/tokens")
        print("   Scope needed: 'repo' (Full control of private repositories)")
        print("\n2. Set the token:")
        print("   export GITHUB_TOKEN='ghp_your_token_here'")
        print("\n3. Run this test again:")
        print("   python test_with_token.py")
        print("\n4. Run the full update:")
        print("   python update_projects.py")
        print("\nSee SETUP_GITHUB_TOKEN.md for detailed instructions.")
        print("="*60)

if __name__ == '__main__':
    print("="*60)
    print("GitHub API Access Test")
    print("="*60)
    test_github_api_access()
    show_setup_instructions()


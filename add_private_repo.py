#!/usr/bin/env python3
"""
Manually add a private repo with public deployment to catalogue_data.json.
This is a workaround for when GITHUB_TOKEN is not set up.

Usage:
    python add_private_repo.py <deployment_url>
    
Example:
    python add_private_repo.py https://myproject.netlify.app
"""

import sys
import json
import requests
from datetime import datetime, timezone

CATALOGUE_FILE = 'catalogue_data.json'
CATALOGUE_ENTRY_FILE = 'catalogue.json'

def fetch_catalogue_from_url(deployment_url: str) -> dict:
    """Fetch catalogue.json from public deployment URL."""
    
    deployment_url = deployment_url.rstrip('/')
    
    # Try multiple common locations
    catalogue_urls = [
        f"{deployment_url}/{CATALOGUE_ENTRY_FILE}",
        f"{deployment_url}/assets/{CATALOGUE_ENTRY_FILE}",
        f"{deployment_url}/public/{CATALOGUE_ENTRY_FILE}",
    ]
    
    for url in catalogue_urls:
        try:
            print(f"Trying: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = json.loads(response.text)
                print(f"✅ Found catalogue.json at: {url}")
                return data
        except (requests.RequestException, json.JSONDecodeError) as e:
            continue
    
    return None

def resolve_screenshot_url(deployment_url: str, metadata: dict) -> str:
    """Resolve screenshot URL from metadata."""
    
    deployment_url = deployment_url.rstrip('/')
    screenshot = metadata.get('screenshot', 'screenshot.png')
    
    # If already absolute URL, use it
    if screenshot.startswith('http://') or screenshot.startswith('https://'):
        return screenshot
    
    # Remove leading ./
    if screenshot.startswith('./'):
        screenshot = screenshot[2:]
    
    # Resolve relative to deployment URL
    return f"{deployment_url}/{screenshot}"

def add_private_repo(deployment_url: str):
    """Add a private repo to catalogue_data.json using its public deployment."""
    
    print("=" * 70)
    print("Adding Private Repo to Catalogue")
    print("=" * 70)
    print(f"\nDeployment URL: {deployment_url}\n")
    
    # Fetch catalogue.json from deployment
    print("Fetching catalogue.json from deployment...")
    metadata = fetch_catalogue_from_url(deployment_url)
    
    if not metadata:
        print("\n❌ ERROR: Could not find catalogue.json at deployment URL!")
        print("\nMake sure:")
        print("1. catalogue.json exists in your repo")
        print("2. It's deployed to the public site")
        print("3. Accessible at: {deployment_url}/catalogue.json")
        return False
    
    print("\n✅ Successfully fetched catalogue.json")
    print(f"   Title: {metadata.get('title', 'N/A')}")
    print(f"   Kind: {metadata.get('kind', 'project')}")
    
    # Check screenshot
    screenshot_url = resolve_screenshot_url(deployment_url, metadata)
    print(f"\nChecking screenshot: {screenshot_url}")
    try:
        resp = requests.head(screenshot_url, timeout=5)
        if resp.status_code == 200:
            print("✅ Screenshot is accessible")
        else:
            print(f"⚠️  Screenshot returned HTTP {resp.status_code}")
    except requests.RequestException:
        print("⚠️  Could not verify screenshot accessibility")
    
    # Build catalogue entry
    entry = {
        "id": metadata.get('id', metadata.get('title', 'unknown')),
        "title": metadata.get('title', 'Unknown Project'),
        "oneLiner": metadata.get('oneLiner', ''),
        "categories": metadata.get('categories', []),
        "tags": metadata.get('tags', []),
        "demoUrl": metadata.get('demoUrl', deployment_url),
        "githubUrl": metadata.get('githubUrl', ''),
        "screenshot": screenshot_url,
        "status": metadata.get('status'),
        "kind": metadata.get('kind', 'project'),
        "topicHierarchy": [],
        "repoTopics": [],
        "lastCommit": None,
        "createdAt": None
    }
    
    # Read existing catalogue
    print("\nReading catalogue_data.json...")
    with open(CATALOGUE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get('items', [])
    
    # Check if already exists
    existing_index = None
    for i, item in enumerate(items):
        if item.get('id') == entry['id']:
            existing_index = i
            break
    
    if existing_index is not None:
        print(f"\n⚠️  Entry with id '{entry['id']}' already exists - updating it")
        old_screenshot = items[existing_index].get('screenshot')
        items[existing_index] = entry
        print(f"   Old screenshot: {old_screenshot}")
        print(f"   New screenshot: {screenshot_url}")
    else:
        print(f"\n✅ Adding new entry with id '{entry['id']}'")
        items.append(entry)
    
    # Update timestamp
    data['generatedAt'] = datetime.now(timezone.utc).isoformat()
    
    # Write back
    print("\nWriting updated catalogue_data.json...")
    with open(CATALOGUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print(f"\nAdded: {entry['title']}")
    print(f"Kind: {entry['kind']} (will appear in ", end='')
    if entry['kind'] == 'page':
        print("Apps tab)")
    elif entry['kind'] == 'longform':
        print("Writing tab)")
    else:
        print("Projects tab)")
    print(f"URL: {entry['demoUrl']}")
    print(f"Screenshot: {entry['screenshot']}")
    print("\nRefresh your homepage to see the changes!")
    print("\n💡 TIP: Set up GITHUB_TOKEN to automate this in the future")
    print("   Run: ./setup_github_token.sh")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_private_repo.py <deployment_url>")
        print("\nExample:")
        print("  python add_private_repo.py https://myproject.netlify.app")
        print("\nThis script will:")
        print("  1. Fetch catalogue.json from the public deployment")
        print("  2. Add it to catalogue_data.json with correct screenshot URL")
        print("  3. Update your homepage automatically")
        sys.exit(1)
    
    deployment_url = sys.argv[1]
    
    # Clean up URL
    if not deployment_url.startswith('http'):
        deployment_url = f'https://{deployment_url}'
    
    success = add_private_repo(deployment_url)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()


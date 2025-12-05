#!/usr/bin/env python3
"""
Manually add Maestro app to catalogue_data.json.
Since Firebase is serving SPA routes, the catalogue.json isn't accessible yet.
"""

import json
from datetime import datetime, timezone

CATALOGUE_FILE = 'catalogue_data.json'

# Maestro entry - using GitHub raw URL temporarily until Firebase is redeployed
MAESTRO_ENTRY = {
    "id": "maestroV2",
    "title": "MAESTRO - Real-time EEG Monitoring",
    "oneLiner": "Real-time EEG monitoring and analysis web application",
    "categories": ["eeg", "neuroscience", "webapp"],
    "tags": ["eeg", "neuroscience", "real-time", "webapp"],
    "demoUrl": "https://maestroapp.ca/",
    "githubUrl": "https://github.com/kylemath/maestroV2",
    # Using placeholder until Firebase redeploy - Firebase currently serves index.html for all routes
    "screenshot": "https://maestroapp.ca/screenshot.png",  # Will work after redeploy
    "status": "published",
    "kind": "page",
    "topicHierarchy": [],
    "repoTopics": [],
    "lastCommit": None,
    "createdAt": None
}

def add_maestro():
    """Add Maestro entry to catalogue_data.json."""
    
    print("Reading catalogue_data.json...")
    with open(CATALOGUE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get('items', [])
    
    # Check if already exists
    existing = False
    for item in items:
        if item.get('id') == 'maestroV2':
            print(f"\n⚠️  Maestro entry already exists - updating it")
            item.update(MAESTRO_ENTRY)
            existing = True
            break
    
    if not existing:
        print("\n✅ Adding new Maestro entry...")
        items.append(MAESTRO_ENTRY)
    
    # Update timestamp
    data['generatedAt'] = datetime.now(timezone.utc).isoformat()
    
    print("\nWriting updated catalogue_data.json...")
    with open(CATALOGUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Done! Maestro has been added to your homepage.")
    print(f"   Title: {MAESTRO_ENTRY['title']}")
    print(f"   URL: {MAESTRO_ENTRY['demoUrl']}")
    print(f"   Kind: {MAESTRO_ENTRY['kind']} (Apps tab)")
    
    print("\n⚠️  NOTE: Screenshot will show once you redeploy to Firebase")
    print("   See instructions below for redeploying with catalogue.json")

if __name__ == '__main__':
    add_maestro()



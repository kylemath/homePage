#!/usr/bin/env python3
"""
Quick fix: Update the Juventus screenshot URL in catalogue_data.json
This fixes the incorrect GitHub raw URL to use the public Netlify URL instead.
"""

import json

CATALOGUE_FILE = 'catalogue_data.json'
JUVENTUS_ID = 'juventus2013teamsite'
CORRECT_SCREENSHOT_URL = 'https://juventus2013.netlify.app/screenshot.png'

def fix_juventus_screenshot():
    """Fix the Juventus screenshot URL."""
    
    print("Reading catalogue_data.json...")
    with open(CATALOGUE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data.get('items', [])
    found = False
    
    for item in items:
        if item.get('id') == JUVENTUS_ID:
            old_url = item.get('screenshot')
            item['screenshot'] = CORRECT_SCREENSHOT_URL
            found = True
            print(f"\n✅ Found Juventus entry!")
            print(f"   Old URL: {old_url}")
            print(f"   New URL: {CORRECT_SCREENSHOT_URL}")
            break
    
    if not found:
        print(f"\n❌ Juventus entry not found in catalogue_data.json")
        print(f"   Looking for ID: {JUVENTUS_ID}")
        return
    
    print("\nWriting updated catalogue_data.json...")
    with open(CATALOGUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Done! The screenshot URL has been fixed.")
    print("\nThe fix is temporary. To prevent this issue:")
    print("1. Set up GITHUB_TOKEN (run: ./setup_github_token.sh)")
    print("2. Run: python update_projects.py")
    print("   This will properly fetch all private repos and update them correctly.")

if __name__ == '__main__':
    fix_juventus_screenshot()


# Setting Up GITHUB_TOKEN for Private Repo Automation

## Why You Need This

Without a GitHub token, the API only returns **public repos**. With a token, it returns:
- ✅ All public repos
- ✅ All private repos (metadata only - name, homepage URL, description)
- ✅ Higher rate limits (5000 requests/hour vs 60)

The script **doesn't access private repo code** - it just needs:
- Repo name
- Homepage URL (your Netlify site)
- Creation/update dates

Then it fetches `catalogue.json` from your **public Netlify site**.

## Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name: `homepage-automation`
4. Set expiration: `No expiration` (or your preference)
5. Select **minimal scopes** (only what's needed):
   - ✅ **`repo`** (to read private repo metadata)
   - ✅ **`read:org`** (if you have org repos)
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again!)

## Step 2: Set Environment Variable

### Option A: For Current Session (temporary)
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

### Option B: Add to Shell Profile (permanent)

**For zsh (macOS default):**
```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

**For bash:**
```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bash_profile
source ~/.bash_profile
```

### Option C: For GitHub Actions (automated deployment)

1. Go to your `homePage` repo settings
2. Navigate to: **Settings → Secrets and variables → Actions**
3. Click **"New repository secret"**
4. Name: `GITHUB_TOKEN`
5. Value: Your token
6. Click **"Add secret"**

Then update `.github/workflows/update-catalogue.yml` to use it:
```yaml
- name: Update projects
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python update_projects.py
```

## Step 3: Verify It Works

Test that the token can access private repos:

```bash
cd /Users/kylemathewson/homePage
source venv/bin/activate

python3 << 'EOF'
import os
import requests

token = os.getenv('GITHUB_TOKEN')
if not token:
    print("❌ GITHUB_TOKEN not set!")
    exit(1)

headers = {'Authorization': f'token {token}'}
response = requests.get('https://api.github.com/user/repos?per_page=100', headers=headers)

if response.status_code == 200:
    repos = response.json()
    private_repos = [r for r in repos if r.get('private')]
    public_repos = [r for r in repos if not r.get('private')]
    
    print(f"✅ Token works!")
    print(f"   Public repos: {len(public_repos)}")
    print(f"   Private repos: {len(private_repos)}")
    
    # Show private repos with Netlify sites
    print("\n🔐 Private repos with homepage URLs:")
    for repo in private_repos:
        homepage = repo.get('homepage', '')
        if homepage:
            print(f"   - {repo['name']}: {homepage}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")
EOF
```

## Step 4: Run the Full Update

Once token is set:

```bash
cd /Users/kylemathewson/homePage
source venv/bin/activate
python update_projects.py
```

This will now:
1. ✅ Find all your private repos
2. ✅ Check their homepage URLs
3. ✅ Fetch from Netlify sites
4. ✅ Add to catalogue

## For Each Private Repo

The automation will work if:

1. ✅ **GitHub repo has "Website" field set**
   - Go to repo settings
   - Set "Website" to your Netlify URL
   - Example: `https://fungioergosum.netlify.app`

2. ✅ **Netlify site has catalogue.json**
   - Deployed to: `https://yoursite.netlify.app/catalogue.json`
   - Contains `kind`, `title`, `oneLiner`, etc.

3. ✅ **Netlify site has screenshot**
   - Deployed to: `https://yoursite.netlify.app/screenshot.png`
   - Or use absolute URL in catalogue.json

## Security Notes

- ✅ Token only gives read access to repo metadata
- ✅ Script never accesses private code
- ✅ Only fetches from public Netlify sites
- ✅ Keep token secret (don't commit to repos)
- ✅ Use GitHub Actions secrets for automation

## Troubleshooting

**Problem:** Token not found
```bash
echo $GITHUB_TOKEN  # Should show your token
```

**Problem:** Token invalid
- Regenerate at https://github.com/settings/tokens
- Make sure `repo` scope is selected

**Problem:** Private repos not appearing
- Verify homepage URL is set in GitHub repo settings
- Verify catalogue.json is accessible on Netlify
- Check script output for errors


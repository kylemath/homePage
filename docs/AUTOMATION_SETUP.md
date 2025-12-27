# GitHub Actions Automation Setup

This guide explains how to set up automated updates for your homepage using GitHub Actions.

## Available Workflows

### 1. Standalone Publications Workflow
**File:** `.github/workflows/update-publications.yml`
- Runs weekly on Sundays at 2 AM
- Updates only publications
- Can be triggered manually
- Falls back to basic scraping if scholarly library fails

### 2. Integrated All-Content Workflow (Recommended)
**File:** `.github/workflows/update-all-and-deploy.yml`
- Updates projects daily at 1 AM
- Updates publications weekly on Sundays at 2 AM
- Can be triggered manually with options to update specific content
- Includes deployment to GitHub Pages
- More sophisticated error handling

## Setup Instructions

### Option A: Use the Integrated Workflow (Recommended)

1. **Use the integrated workflow** that combines both projects and publications:
   - Keeps your existing functionality
   - Adds publications updates
   - Better organization and fewer workflow runs

2. **Disable or delete your current workflow:**
   ```bash
   # Rename the old workflow to disable it
   mv .github/workflows/update-projects.yml .github/workflows/update-projects.yml.disabled
   ```

3. **The new workflow is already created** at `.github/workflows/update-all-and-deploy.yml`

### Option B: Keep Separate Workflows

1. **Keep your existing** `.github/workflows/update-projects.yml`
2. **Use the standalone** `.github/workflows/update-publications.yml`
3. **Adjust schedules** to avoid conflicts if needed

## Workflow Features

### Manual Triggers
Both workflows can be triggered manually from the GitHub Actions tab:

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select the workflow you want to run
4. Click "Run workflow" button
5. (For integrated workflow) Choose what to update

### Automatic Schedules

**Integrated Workflow:**
- **Projects:** Daily at 1 AM UTC
- **Publications:** Weekly on Sundays at 2 AM UTC

**Standalone Publications:**
- **Publications:** Weekly on Sundays at 2 AM UTC

### Error Handling

The workflows include robust error handling:
- Publications: Tries scholarly library first, falls back to basic scraping
- Only commits if changes are detected
- Descriptive commit messages
- Continues on dependency installation failures

## Configuration

### Customize Update Frequency

Edit the cron expressions in the workflow files:

```yaml
schedule:
  - cron: '0 1 * * *'    # Daily at 1 AM UTC
  - cron: '0 2 * * 0'    # Weekly on Sunday at 2 AM UTC
  - cron: '0 0 1 * *'    # Monthly on 1st at midnight
```

**Cron format:** `minute hour day month day-of-week`

### Customize Author Information

Update the author settings in the publication scripts:

```python
# In update_publications.py
AUTHOR_QUERY = 'Kyle Mathewson University of Alberta'

# In update_publications_scholarly.py  
AUTHOR_NAME = 'Kyle Mathewson'
```

### Environment Variables

If you need additional configuration, you can add environment variables to the workflow:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  AUTHOR_NAME: "Kyle Mathewson"
  MAX_PUBLICATIONS: "20"
```

## Monitoring

### Check Workflow Status

1. Go to the "Actions" tab in your repository
2. You'll see the status of recent workflow runs
3. Click on a run to see detailed logs
4. Green checkmark = success, red X = failure

### Workflow Notifications

GitHub will notify you (via email/web) if workflows fail. You can customize this in your GitHub notification settings.

### Troubleshooting

**Common issues:**

1. **Publications not updating:**
   - Check if your Google Scholar profile is public
   - Verify author name matches exactly
   - Google Scholar may be rate limiting

2. **Workflow fails:**
   - Check the Actions tab for error logs
   - Most common: dependency installation issues
   - Scholarly library sometimes has connectivity issues

3. **No changes committed:**
   - This is normal if there are no new publications/projects
   - The workflow only commits when actual changes are detected

## Testing

### Test the Workflows

1. **Manual trigger:** Use the "Run workflow" button to test
2. **Push test:** Make a small change and push to main branch
3. **Check logs:** Review the Actions tab for any issues

### Test Publications Locally

Before relying on the automated workflow:

```bash
# Create virtual environment
python -m venv test_env
source test_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install scholarly

# Test the script
python update_publications_scholarly.py
```

## Security

The workflows use `GITHUB_TOKEN` which is automatically provided by GitHub Actions with appropriate permissions for:
- Reading repository content
- Writing to repository (for commits)
- Deploying to GitHub Pages

No additional secrets or API keys are required.

## Migration from Existing Workflow

If you're switching from the standalone `update-projects.yml`:

1. **Backup your current workflow:**
   ```bash
   cp .github/workflows/update-projects.yml .github/workflows/update-projects.yml.backup
   ```

2. **Test the new integrated workflow** with a manual trigger

3. **Once confirmed working, disable the old workflow:**
   ```bash
   mv .github/workflows/update-projects.yml .github/workflows/update-projects.yml.disabled
   ```

4. **Or delete it entirely:**
   ```bash
   rm .github/workflows/update-projects.yml
   ```

The integrated workflow maintains all functionality of your original workflow while adding publications support. 
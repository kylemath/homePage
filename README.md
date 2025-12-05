# Kyle Mathewson's Academic Homepage

This repository contains the source code for Kyle Mathewson's academic homepage, a minimalist and efficient personal website inspired by classic 90s academic pages. The site is live at [kylemathewson.com](https://kylemathewson.com).

## Overview

This project implements a clean, responsive academic homepage that automatically updates to showcase the latest GitHub projects. It features:

- Automatically updated project listings from GitHub repositories
- Sortable project thumbnails with descriptions
- Social media links and professional information
- Daily automated updates via GitHub Actions
- Clean, responsive design optimized for all devices

## Live Website

The website is deployed at [kylemathewson.com](https://kylemathewson.com) using GitHub Pages.

## Project Structure

```
.
├── index.html              # Main webpage
├── update_projects.py      # Script to fetch and update GitHub projects
├── requirements.txt        # Python dependencies
├── CNAME                   # Domain configuration for GitHub Pages
└── .github/workflows/      # GitHub Actions workflow configurations
    └── update-projects.yml # Automated update and deployment workflow
```

## Automated Updates

The project uses GitHub Actions to automatically update the project list and deploy changes. The automation:

1. Runs daily at midnight
2. Triggers on pushes to the main branch
3. Can be manually triggered through GitHub Actions
4. Updates project information from GitHub repositories
5. Commits changes and deploys to GitHub Pages

### Workflow Details

The automated workflow (`update-projects.yml`):
1. Sets up Python environment
2. Installs required dependencies
3. Runs the update script to fetch latest projects
4. Commits and pushes any changes
5. Deploys to GitHub Pages with custom domain configuration

## Local Development

To set up the project locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/[username]/homePage.git
   cd homePage
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. To test the update script locally:
   ```bash
   python update_projects.py
   ```

## Private Repository Support

The site supports displaying projects from **private GitHub repositories** that have **public deployments** (e.g., Netlify, Vercel).

### Quick Setup for Private Repos

1. **Set up GitHub Token** (required for private repo access):
   ```bash
   ./setup_github_token.sh
   ```
   Follow the instructions to create a token at https://github.com/settings/tokens with `repo` scope.

2. **Check your private repos configuration**:
   ```bash
   python check_private_repos.py
   ```
   This diagnostic tool will show you which repos need setup.

3. **For each private repo**:
   - Set the homepage URL in GitHub repo settings
   - Add `catalogue.json` to repo root
   - Add `screenshot.png` to repo root
   - Deploy the files to your public site

4. **Update homepage**:
   ```bash
   python update_projects.py
   ```

### Documentation

- **Full Guide**: See [docs/PRIVATE_REPO_AUTOMATION.md](docs/PRIVATE_REPO_AUTOMATION.md)
- **Quick Reference**: See [docs/PRIVATE_REPO_INSTRUCTIONS.md](docs/PRIVATE_REPO_INSTRUCTIONS.md)

### Helper Scripts

- `setup_github_token.sh` - Check and configure GitHub token
- `check_private_repos.py` - Diagnose private repo configuration issues

## Deployment

The site automatically deploys through GitHub Actions. For manual deployment:

1. Push changes to the main branch:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. The GitHub Action will automatically:
   - Update the projects list
   - Deploy to GitHub Pages
   - Update the live site at kylemathewson.com

## Domain Configuration

The site uses a custom domain (kylemathewson.com) configured through:
1. CNAME file in the repository
2. GitHub Pages settings
3. Domain DNS configuration pointing to GitHub Pages

## Dependencies

- Python 3.x
- Required Python packages (specified in requirements.txt):
  - requests==2.31.0
  - beautifulsoup4==4.12.2

## Contributing

While this is a personal website, suggestions and improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is available for reference and learning purposes. Please contact the repository owner for any usage permissions.

## Support

For issues or questions:
1. Open an issue in the GitHub repository
2. Contact through the website's provided contact information 
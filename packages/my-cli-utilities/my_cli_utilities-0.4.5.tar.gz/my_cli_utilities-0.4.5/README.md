# RC CLI - Development Tools

A powerful command-line tool for development workflows.

## 📦 Installation

```bash
pip install rc-cli-tools
```

Or install from source:
```bash
git clone <repository-url>
cd utils-kts
# Recommended: install into the project venv so you run the matching `rc`
python3 -m venv .venv
./.venv/bin/pip install -e .

# Use the venv's rc explicitly (or activate the venv)
./.venv/bin/rc --help
```

## ⚙️ Configuration

### First-Time Setup (Recommended)

After installation, configure RC CLI using the interactive setup:

```bash
rc config setup
```

This will:
- Guide you through the configuration process
- Create `~/.rc-cli.env` with your settings
- Validate the configuration

### Quick Check

```bash
# View current configuration
rc config show

# Validate configuration
rc config validate
```

### Manual Configuration (Alternative)

Create `~/.rc-cli.env` in your home directory:

```bash
# Copy the example file
cp .env.example ~/.rc-cli.env

# Edit with your actual values
# IMPORTANT: Replace 'yourcompany' with your actual company domain
vim ~/.rc-cli.env
```

Example configuration:
```bash
# Company name (for file naming)
COMPANY_NAME=YourCompany

# GitLab Configuration (IMPORTANT: Include /api/v4)
SP_GITLAB_BASE_URL=https://git.yourcompany.com/api/v4
SP_GITLAB_PROJECT_ID=24890
GITLAB_TOKEN=your-gitlab-personal-access-token

# mThor Account Pool GitLab Configuration (recommended)
MTHOR_GITLAB_BASE_URL=https://git.yourcompany.com/api/v4
MTHOR_GITLAB_PROJECT_ID=12345
MTHOR_GITLAB_FILE_PATH=src/main/resources/account/mThor-mZeus-account.yaml
MTHOR_GITLAB_BRANCH=master

# Internal APIs
SP_INTAPI_BASE_URL=http://intapi.yourcompany.com:8082
AP_BASE_URL=https://account-pool.yourcompany.com
DS_BASE_URL=https://device-spy.yourcompany.com
```

**Important:** 
- The `.rc-cli.env` file in your home directory is global for all projects
- You can also create a `.env` file in specific project directories
- Never commit `.env` files to version control

### Configuration Locations

RC CLI searches for configuration in this order (first found wins):
1. `.env` in current directory (project-specific)
2. `~/.rc-cli.env` in your home directory (global)
3. Environment variables in your shell (highest priority)

### Getting GitLab Token

1. Go to GitLab → User Settings → Access Tokens
2. Create a new token with `read_api` scope
3. Copy the token and use it in your configuration

## 🚀 Quick Start

```bash
# Check configuration
rc config

# Service Parameters
rc sp tui              # Interactive TUI (recommended)
rc sp list             # List all service parameters
rc sp search 'SMS'     # Search for parameters

# Feature Flags
rc ffs tui             # Interactive TUI
rc ffs search 'flag'   # Search flags

# Account Pool
rc ap tui                      # Interactive TUI (includes all features below)
rc ap get webAqaXmn            # Get random account
rc ap by-alias webAqaXmn       # Get account by alias from GitLab
rc ap list-aliases             # List all available aliases
rc ap alias-info webAqaXmn     # Get alias details

# Device Spy
rc ds udid <UDID>              # Get device info
rc ds devices android          # List devices

# Downloads
rc download aqa        # Download AQA apps
```

## 📖 Documentation

For detailed documentation, visit [Documentation Link] or run:
```bash
rc info
```

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use GitLab personal access tokens, not passwords
- Keep your tokens secure and rotate them regularly

## 🐛 Troubleshooting

### "GitLab URL not configured" Error

This means you haven't set up your configuration yet:

```bash
# Check configuration status
rc config show

# Run setup wizard
rc config setup
```

### Configuration Not Loading

```bash
# Check which config files exist
rc config show

# Verify file location
ls -la ~/.rc-cli.env
```

### DNS Resolution Errors

If you see "nodename nor servname provided" error:
- Your `SP_GITLAB_BASE_URL` is using the default placeholder
- Run `rc config setup` to set the correct GitLab URL
- Or edit `~/.rc-cli.env` with your actual GitLab server URL

## 📚 Documentation

- [CODE_REVIEW.md](rc_cli/CODE_REVIEW.md) - Architecture review and refactoring history
- [COMPANY_CONFIG_GUIDE.md](COMPANY_CONFIG_GUIDE.md) - Company-specific configuration guide
- [PYPI_USAGE.md](PYPI_USAGE.md) - PyPI packaging and publishing guide

## 📝 License

[Your License Here]

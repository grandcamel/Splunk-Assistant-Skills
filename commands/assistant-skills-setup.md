---
name: assistant-skills-setup
description: Set up Splunk Assistant Skills - Python environment, dependencies, and credentials
---

# Splunk Assistant Skills Setup

You are helping the user set up Splunk Assistant Skills. This is a one-time setup that configures:

1. A shared Python virtual environment at `~/.assistant-skills-venv/`
2. Required Python dependencies
3. Splunk connection credentials (URL, authentication)
4. A `claude-as` shell function for running Claude with the venv activated

## Setup Process

### Step 1: Create Python Virtual Environment

First, create the shared virtual environment:

```bash
python3 -m venv ~/.assistant-skills-venv
```

### Step 2: Activate and Install Dependencies

Activate the venv and install the required packages:

```bash
source ~/.assistant-skills-venv/bin/activate && pip install --upgrade pip && pip install splunk-assistant-skills-lib
```

### Step 3: Configure Splunk Credentials

Run the environment setup script to configure Splunk connection:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/../../scripts/setup-env.sh"
```

This will prompt for:
- Splunk URL (e.g., https://splunk.example.com)
- Management port (default: 8089)
- Authentication method (Bearer token or Basic auth)
- Default app and index settings

### Step 4: Create claude-as Shell Function

Add the `claude-as` function to the user's shell RC file. This function activates the venv before running Claude:

For bash users (~/.bashrc):
```bash
cat >> ~/.bashrc << 'EOF'

# Claude with Assistant Skills venv
claude-as() {
    source ~/.assistant-skills-venv/bin/activate
    claude "$@"
    deactivate
}
EOF
```

For zsh users (~/.zshrc):
```bash
cat >> ~/.zshrc << 'EOF'

# Claude with Assistant Skills venv
claude-as() {
    source ~/.assistant-skills-venv/bin/activate
    claude "$@"
    deactivate
}
EOF
```

### Step 5: Verify Installation

Test that the setup is complete:

```bash
source ~/.assistant-skills-venv/bin/activate && python -c "from splunk_assistant_skills_lib import get_splunk_client; print('Library installed successfully')"
```

## Important Notes

- After setup, use `claude-as` instead of `claude` to run with the Assistant Skills venv activated
- Credentials are stored in `~/.env` with secure permissions (chmod 600)
- To reconfigure credentials later, run the setup script again: `bash "${CLAUDE_PLUGIN_ROOT}/../../scripts/setup-env.sh"`
- For profile-based configuration, see the CLAUDE.md documentation

## Troubleshooting

If you encounter issues:

1. **Python not found**: Ensure Python 3.8+ is installed
2. **Permission denied**: Check that ~/.assistant-skills-venv is writable
3. **Connection failed**: Verify Splunk URL and port are accessible
4. **Authentication failed**: Check token validity or username/password

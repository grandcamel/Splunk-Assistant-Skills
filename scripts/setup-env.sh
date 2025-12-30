#!/bin/bash
# Splunk Assistant Skills - Environment Setup Script
# Prompts for configuration and updates ~/.env and ~/.bashrc

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ENV_FILE="$HOME/.env"
BASHRC_FILE="$HOME/.bashrc"
ZSHRC_FILE="$HOME/.zshrc"

# Detect shell
if [[ -n "$ZSH_VERSION" ]] || [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$ZSHRC_FILE"
    SHELL_NAME="zsh"
else
    SHELL_RC="$BASHRC_FILE"
    SHELL_NAME="bash"
fi

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Splunk Assistant Skills - Environment Setup          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to read existing value from ~/.env
get_existing_value() {
    local key="$1"
    if [[ -f "$ENV_FILE" ]]; then
        grep "^export ${key}=" "$ENV_FILE" 2>/dev/null | sed "s/^export ${key}=//" | tr -d '"' | tr -d "'"
    fi
}

# Function to prompt with default value
prompt_value() {
    local prompt="$1"
    local default="$2"
    local is_secret="${3:-false}"
    local value

    if [[ -n "$default" ]]; then
        if [[ "$is_secret" == "true" ]]; then
            # Mask secret values
            local masked="${default:0:4}****${default: -4}"
            echo -en "${BLUE}$prompt${NC} [${masked}]: "
        else
            echo -en "${BLUE}$prompt${NC} [$default]: "
        fi
    else
        echo -en "${BLUE}$prompt${NC}: "
    fi

    if [[ "$is_secret" == "true" ]]; then
        read -s value
        echo ""
    else
        read value
    fi

    if [[ -z "$value" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# Function to prompt yes/no
prompt_yes_no() {
    local prompt="$1"
    local default="$2"
    local response

    if [[ "$default" == "y" ]]; then
        echo -en "${BLUE}$prompt${NC} [Y/n]: "
    else
        echo -en "${BLUE}$prompt${NC} [y/N]: "
    fi

    read response
    response="${response:-$default}"

    [[ "${response,,}" == "y" || "${response,,}" == "yes" ]]
}

# Function to validate URL
validate_url() {
    local url="$1"
    if [[ "$url" =~ ^https?:// ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate port
validate_port() {
    local port="$1"
    if [[ "$port" =~ ^[0-9]+$ ]] && [[ "$port" -ge 1 ]] && [[ "$port" -le 65535 ]]; then
        return 0
    else
        return 1
    fi
}

echo -e "${YELLOW}This script will configure environment variables for Splunk Assistant Skills.${NC}"
echo -e "${YELLOW}Press Enter to keep existing/default values.${NC}"
echo ""

# Load existing values
existing_url=$(get_existing_value "SPLUNK_SITE_URL")
existing_port=$(get_existing_value "SPLUNK_MANAGEMENT_PORT")
existing_token=$(get_existing_value "SPLUNK_TOKEN")
existing_username=$(get_existing_value "SPLUNK_USERNAME")
existing_password=$(get_existing_value "SPLUNK_PASSWORD")
existing_verify_ssl=$(get_existing_value "SPLUNK_VERIFY_SSL")
existing_default_app=$(get_existing_value "SPLUNK_DEFAULT_APP")
existing_default_index=$(get_existing_value "SPLUNK_DEFAULT_INDEX")
existing_profile=$(get_existing_value "SPLUNK_PROFILE")

# Connection Settings
echo -e "${GREEN}═══ Connection Settings ═══${NC}"
echo ""

# Splunk URL
while true; do
    SPLUNK_SITE_URL=$(prompt_value "Splunk URL (e.g., https://splunk.example.com)" "${existing_url:-https://localhost}")
    if validate_url "$SPLUNK_SITE_URL"; then
        break
    else
        echo -e "${RED}Invalid URL. Must start with http:// or https://${NC}"
    fi
done

# Management Port
while true; do
    SPLUNK_MANAGEMENT_PORT=$(prompt_value "Management port" "${existing_port:-8089}")
    if validate_port "$SPLUNK_MANAGEMENT_PORT"; then
        break
    else
        echo -e "${RED}Invalid port. Must be 1-65535${NC}"
    fi
done

# SSL Verification
if prompt_yes_no "Verify SSL certificates?" "${existing_verify_ssl:-y}"; then
    SPLUNK_VERIFY_SSL="true"
else
    SPLUNK_VERIFY_SSL="false"
fi

echo ""

# Authentication
echo -e "${GREEN}═══ Authentication ═══${NC}"
echo -e "${CYAN}Choose authentication method:${NC}"
echo "  1) Bearer Token (recommended for production)"
echo "  2) Basic Auth (username/password)"
echo ""

# Determine default based on existing config
if [[ -n "$existing_token" ]]; then
    default_auth="1"
elif [[ -n "$existing_username" ]]; then
    default_auth="2"
else
    default_auth="1"
fi

echo -en "${BLUE}Select [1-2]${NC} [$default_auth]: "
read auth_choice
auth_choice="${auth_choice:-$default_auth}"

SPLUNK_TOKEN=""
SPLUNK_USERNAME=""
SPLUNK_PASSWORD=""

case "$auth_choice" in
    1)
        echo ""
        echo -e "${CYAN}To create a token in Splunk Web:${NC}"
        echo "  Settings > Tokens > New Token"
        echo ""
        SPLUNK_TOKEN=$(prompt_value "Splunk Bearer Token" "$existing_token" true)
        if [[ -z "$SPLUNK_TOKEN" ]]; then
            echo -e "${RED}Token is required for Bearer auth${NC}"
            exit 1
        fi
        ;;
    2)
        echo ""
        SPLUNK_USERNAME=$(prompt_value "Splunk Username" "${existing_username:-admin}")
        SPLUNK_PASSWORD=$(prompt_value "Splunk Password" "$existing_password" true)
        if [[ -z "$SPLUNK_USERNAME" ]] || [[ -z "$SPLUNK_PASSWORD" ]]; then
            echo -e "${RED}Username and password are required for Basic auth${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""

# Default Settings
echo -e "${GREEN}═══ Default Settings ═══${NC}"
echo ""

SPLUNK_DEFAULT_APP=$(prompt_value "Default Splunk app" "${existing_default_app:-search}")
SPLUNK_DEFAULT_INDEX=$(prompt_value "Default index" "${existing_default_index:-main}")
SPLUNK_PROFILE=$(prompt_value "Profile name (for multi-instance)" "${existing_profile:-default}")

echo ""

# Test connection (optional)
echo -e "${GREEN}═══ Test Connection ═══${NC}"
if prompt_yes_no "Test connection to Splunk?" "y"; then
    echo -e "${YELLOW}Testing connection to ${SPLUNK_SITE_URL}:${SPLUNK_MANAGEMENT_PORT}...${NC}"

    # Build curl command
    curl_opts="-s -o /dev/null -w %{http_code} --connect-timeout 10"
    if [[ "$SPLUNK_VERIFY_SSL" == "false" ]]; then
        curl_opts="$curl_opts -k"
    fi

    if [[ -n "$SPLUNK_TOKEN" ]]; then
        http_code=$(curl $curl_opts -H "Authorization: Bearer $SPLUNK_TOKEN" \
            "${SPLUNK_SITE_URL}:${SPLUNK_MANAGEMENT_PORT}/services/server/info" 2>/dev/null || echo "000")
    else
        http_code=$(curl $curl_opts -u "${SPLUNK_USERNAME}:${SPLUNK_PASSWORD}" \
            "${SPLUNK_SITE_URL}:${SPLUNK_MANAGEMENT_PORT}/services/server/info" 2>/dev/null || echo "000")
    fi

    case "$http_code" in
        200)
            echo -e "${GREEN}Connection successful!${NC}"
            ;;
        401)
            echo -e "${RED}Authentication failed (401). Check your credentials.${NC}"
            if ! prompt_yes_no "Continue anyway?" "n"; then
                exit 1
            fi
            ;;
        000)
            echo -e "${RED}Connection failed. Check URL and network.${NC}"
            if ! prompt_yes_no "Continue anyway?" "n"; then
                exit 1
            fi
            ;;
        *)
            echo -e "${YELLOW}Unexpected response: HTTP $http_code${NC}"
            if ! prompt_yes_no "Continue anyway?" "y"; then
                exit 1
            fi
            ;;
    esac
fi

echo ""

# Write to ~/.env
echo -e "${GREEN}═══ Writing Configuration ═══${NC}"
echo ""

# Backup existing file
if [[ -f "$ENV_FILE" ]]; then
    backup_file="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$ENV_FILE" "$backup_file"
    echo -e "${YELLOW}Backed up existing ~/.env to ${backup_file}${NC}"
fi

# Remove old Splunk entries if they exist
if [[ -f "$ENV_FILE" ]]; then
    grep -v "^SPLUNK_\|^export SPLUNK_" "$ENV_FILE" > "${ENV_FILE}.tmp" 2>/dev/null || true
    mv "${ENV_FILE}.tmp" "$ENV_FILE"
fi

# Append new configuration (no 'export' needed - set -a handles it)
cat >> "$ENV_FILE" << EOF

# Splunk Assistant Skills Configuration
# Generated: $(date)
SPLUNK_SITE_URL="$SPLUNK_SITE_URL"
SPLUNK_MANAGEMENT_PORT="$SPLUNK_MANAGEMENT_PORT"
SPLUNK_VERIFY_SSL="$SPLUNK_VERIFY_SSL"
SPLUNK_DEFAULT_APP="$SPLUNK_DEFAULT_APP"
SPLUNK_DEFAULT_INDEX="$SPLUNK_DEFAULT_INDEX"
SPLUNK_PROFILE="$SPLUNK_PROFILE"
EOF

# Add auth credentials
if [[ -n "$SPLUNK_TOKEN" ]]; then
    echo "SPLUNK_TOKEN=\"$SPLUNK_TOKEN\"" >> "$ENV_FILE"
else
    echo "SPLUNK_USERNAME=\"$SPLUNK_USERNAME\"" >> "$ENV_FILE"
    echo "SPLUNK_PASSWORD=\"$SPLUNK_PASSWORD\"" >> "$ENV_FILE"
fi

# Set secure permissions
chmod 600 "$ENV_FILE"
echo -e "${GREEN}Created/updated ~/.env with secure permissions (600)${NC}"

# Update shell RC file to source ~/.env
echo -e "${YELLOW}Updating ${SHELL_RC}...${NC}"

# Check if the env loader block already exists
if ! grep -q "Load Environment Variables from ~/.env" "$SHELL_RC" 2>/dev/null; then
    cat >> "$SHELL_RC" << 'BASHRC_BLOCK'

# ============================================================================
# Load Environment Variables from ~/.env
# ============================================================================
if [ -f ~/.env ]; then
    # Export all variables from ~/.env file
    # Handles comments, blank lines, and exports each line
    set -a  # Automatically export all variables
    source ~/.env
    set +a  # Disable automatic export
fi
BASHRC_BLOCK
    echo -e "${GREEN}Added ~/.env loader block to ${SHELL_RC}${NC}"
else
    echo -e "${YELLOW}${SHELL_RC} already has ~/.env loader block${NC}"
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗"
echo -e "║                    Setup Complete!                           ║"
echo -e "╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration saved to:${NC}"
echo -e "  - ${BLUE}~/.env${NC} (environment variables, chmod 600)"
echo -e "  - ${BLUE}${SHELL_RC}${NC} (loader block added)"
echo ""
echo -e "${YELLOW}To apply changes now, run:${NC}"
echo -e "  ${BLUE}source ${SHELL_RC}${NC}"
echo ""
echo -e "${YELLOW}Or start a new terminal session.${NC}"
echo ""

# Offer to source now
if prompt_yes_no "Source ${SHELL_RC} now?" "y"; then
    # Use set -a to export, matching the bashrc block
    set -a
    source "$ENV_FILE"
    set +a
    echo -e "${GREEN}Environment variables loaded!${NC}"
    echo ""
    echo -e "${CYAN}Current Splunk configuration:${NC}"
    env | grep "^SPLUNK_" | while read line; do
        key="${line%%=*}"
        value="${line#*=}"
        # Mask sensitive values
        if [[ "$key" == "SPLUNK_TOKEN" || "$key" == "SPLUNK_PASSWORD" ]]; then
            echo -e "  ${key}=****${value: -4}"
        else
            echo -e "  ${key}=${value}"
        fi
    done
fi

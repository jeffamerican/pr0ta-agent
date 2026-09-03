#!/usr/bin/env bash
# Connect Codex to the remote PR0TA MCP server using a credential store shared
# by the Codex CLI and desktop app.
set -euo pipefail

MCP_NAME="${PR0TA_MCP_NAME:-pr0ta}"
MCP_URL="${PR0TA_MCP_URL:-https://app.pr0ta.com/api/mcp/mcp}"
CODEX_BIN="${CODEX_BIN:-codex}"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
CODEX_CONFIG="${CODEX_HOME_DIR}/config.toml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_PATH="${PR0TA_MCP_PROFILE_PATH:-${SCRIPT_DIR}/prep-production-tools.json}"

if [ ! -f "$PROFILE_PATH" ]; then
  echo "PR0TA Prep/Production tool profile was not found: $PROFILE_PATH" >&2
  exit 1
fi

PREP_PRODUCTION_TOOLS="$(tr -d '\n' <"$PROFILE_PATH")"

configure_shared_oauth_store() {
  local temporary_config

  mkdir -p "$CODEX_HOME_DIR"
  temporary_config="$(mktemp "${CODEX_HOME_DIR}/config.toml.XXXXXX")"
  chmod 600 "$temporary_config"

  if [ -f "$CODEX_CONFIG" ]; then
    awk '
      BEGIN {
        inserted = 0
        top_level = 1
      }
      top_level && /^[[:space:]]*mcp_oauth_credentials_store[[:space:]]*=/ {
        print "mcp_oauth_credentials_store = \"file\""
        inserted = 1
        next
      }
      top_level && /^[[:space:]]*\[/ {
        if (!inserted) {
          print "mcp_oauth_credentials_store = \"file\""
          print ""
          inserted = 1
        }
        top_level = 0
      }
      { print }
      END {
        if (!inserted) {
          if (NR > 0) {
            print ""
          }
          print "mcp_oauth_credentials_store = \"file\""
        }
      }
    ' "$CODEX_CONFIG" >"$temporary_config"
  else
    printf 'mcp_oauth_credentials_store = "file"\n' >"$temporary_config"
  fi

  mv "$temporary_config" "$CODEX_CONFIG"
}

configure_prep_production_tools() {
  local temporary_config

  temporary_config="$(mktemp "${CODEX_HOME_DIR}/config.toml.XXXXXX")"
  chmod 600 "$temporary_config"
  awk -v section="[mcp_servers.${MCP_NAME}]" -v tools="$PREP_PRODUCTION_TOOLS" '
    BEGIN {
      found_section = 0
      in_section = 0
      wrote_tools = 0
    }
    $0 == section {
      found_section = 1
      in_section = 1
      print
      next
    }
    in_section && /^[[:space:]]*\[/ {
      if (!wrote_tools) {
        print "enabled_tools = " tools
        print ""
        wrote_tools = 1
      }
      in_section = 0
    }
    in_section && /^[[:space:]]*enabled_tools[[:space:]]*=/ {
      print "enabled_tools = " tools
      wrote_tools = 1
      next
    }
    { print }
    END {
      if (in_section && !wrote_tools) {
        print "enabled_tools = " tools
      } else if (!found_section) {
        if (NR > 0) {
          print ""
        }
        print section
        print "url = \"" ENVIRON["PR0TA_MCP_URL"] "\""
        print "enabled_tools = " tools
      }
    }
  ' "$CODEX_CONFIG" >"$temporary_config"
  mv "$temporary_config" "$CODEX_CONFIG"
}

if ! command -v "$CODEX_BIN" >/dev/null 2>&1; then
  echo "Codex CLI was not found on PATH." >&2
  exit 127
fi

configure_shared_oauth_store
echo "Configured shared Codex MCP OAuth storage in $CODEX_CONFIG."

if ! "$CODEX_BIN" mcp get "$MCP_NAME" >/dev/null 2>&1; then
  echo "Registering PR0TA MCP server at $MCP_URL ..."
  "$CODEX_BIN" mcp add "$MCP_NAME" --url "$MCP_URL"
fi

export PR0TA_MCP_URL="$MCP_URL"
configure_prep_production_tools
echo "Enabled the complete PR0TA Prep/Production MCP tool profile."

if [ "${PR0TA_MCP_SKIP_LOGIN:-0}" != "1" ]; then
  echo "Starting PR0TA MCP OAuth login..."
  "$CODEX_BIN" mcp login "$MCP_NAME" --scopes mcp \
    -c 'mcp_oauth_credentials_store="file"'
fi

echo ""
echo "PR0TA MCP connection is configured."
echo "Quit and reopen Codex, then start a new task so its tool inventory is rebuilt."

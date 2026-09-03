#!/usr/bin/env sh
set -eu

MCP_NAME="${PR0TA_MCP_NAME:-pr0ta}"
MCP_URL="${PR0TA_MCP_URL:-https://app.pr0ta.com/api/mcp/mcp}"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI was not found on PATH." >&2
  echo "Open Claude Code and connect the PR0TA MCP server with /mcp, or install the Claude Code CLI and retry." >&2
  exit 127
fi

if ! claude mcp get "$MCP_NAME" >/dev/null 2>&1; then
  echo "PR0TA MCP server is not registered in Claude Code. Adding $MCP_URL ..."
  claude mcp add --transport http "$MCP_NAME" "$MCP_URL"
fi

echo ""
echo "PR0TA MCP server '$MCP_NAME' is registered."
echo "To complete authentication, run /mcp inside Claude Code, select '$MCP_NAME',"
echo "and approve the PR0TA OAuth request in your browser."
echo ""
echo "If PR0TA tools are still not callable after the browser login completes,"
echo "start a fresh Claude Code session so the tool list reloads."

if command -v curl >/dev/null 2>&1; then
  if ! curl -fsSL "https://app.pr0ta.com/.well-known/oauth-authorization-server/api/mcp/mcp" | grep -q '"none"'; then
    echo "" >&2
    echo "Warning: the PR0TA OAuth metadata does not advertise public PKCE clients." >&2
    echo "Verify that $MCP_URL returns a WWW-Authenticate resource_metadata value and that the" >&2
    echo "authorization metadata advertises token_endpoint_auth_methods_supported including 'none'." >&2
    echo "After the server fix is deployed, rerun this script and retry the /mcp login." >&2
  fi
fi

# ProtaFilm|maker Skills

Public, generated distributions for connecting tool-capable AI assistants to
[ProtaFilm|maker](https://www.protafilmmaker.com/downloads/skills/).

- **ChatGPT:** follow the plan-aware setup on the download page.
- **Claude Code:** add `jeffamerican/pr0ta-agent` as a marketplace, then install
  `pr0ta@pr0ta`.
- **Claude Desktop:** download `pr0ta.plugin` from the latest release and upload it in
  Customize -> Plugins.
- **Codex:** add `jeffamerican/pr0ta-agent` as a plugin marketplace, then install
  `pr0ta@pr0ta-codex`.
- **Other assistants:** download `pr0ta-skills.zip`, or connect the remote MCP
  endpoint if the app supports it.

The editable source of truth lives with the private PR0TA platform. This public
repository generates its skill trees and release metadata from the platform's
hash-addressed manifest; do not edit those generated files by hand. Marketplace
catalogs, packaging code, and installation instructions are maintained here.
Its scheduled workflow publishes changed skills after the compatible platform
version is live.

Canonical skill text is deliberately host-neutral. Codex and Claude keep their
own connector manifest and setup helper outside the generated `skills/` tree,
so each host retains the correct installation and OAuth flow.

## Codex install

```text
/plugin marketplace add jeffamerican/pr0ta-agent
/plugin install pr0ta@pr0ta-codex
```

## Claude Code install and updates

```text
/plugin marketplace add jeffamerican/pr0ta-agent
/plugin install pr0ta@pr0ta
```

To update an existing installation:

```text
/plugin marketplace update pr0ta
/plugin update pr0ta@pr0ta
```

If `pr0ta` was previously registered from a local directory or the legacy
`jeffamerican/pr0ta-plugin` repository, run the marketplace-add command above
to reconnect it to this repository before updating.

For automatic updates, open `/plugin`, select **Marketplaces**, select
**pr0ta**, and enable auto-update. Restart Claude Code after updating to load
the refreshed skills.

The root `.claude-plugin/marketplace.json` points to `./claude`. The publisher
updates that plugin's version from the live platform manifest, so the marketplace
and downloadable package use the same generated skills. The catalog omits a
separate version to avoid masking future plugin releases.

## Remote MCP endpoint

```text
https://app.pr0ta.com/api/mcp/mcp
```

PR0TA uses browser OAuth for remote MCP. Never commit API keys, personal access
tokens, OAuth credentials, project files, or generated media to this repository.

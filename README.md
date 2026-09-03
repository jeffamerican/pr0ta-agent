# ProtaFilm|maker Skills

Public, generated distributions for connecting tool-capable AI assistants to
[ProtaFilm|maker](https://www.protafilmmaker.com/downloads/skills/).

- **ChatGPT:** follow the plan-aware setup on the download page.
- **Claude:** download `pr0ta.plugin` from the latest release and upload it in
  Customize -> Plugins.
- **Codex:** add `jeffamerican/pr0ta-agent` as a plugin marketplace, then install
  `pr0ta@pr0ta-codex`.
- **Other assistants:** download `pr0ta-skills.zip`, or connect the remote MCP
  endpoint if the app supports it.

The editable source of truth lives with the private PR0TA platform. This public
repository is generated from its hash-addressed manifest and should not be
edited by hand. Its scheduled workflow publishes changed skills after the
compatible platform version is live.

Canonical skill text is deliberately host-neutral. Codex and Claude keep their
own connector manifest and setup helper outside the generated `skills/` tree,
so each host retains the correct installation and OAuth flow.

## Codex install

```text
/plugin marketplace add jeffamerican/pr0ta-agent
/plugin install pr0ta@pr0ta-codex
```

## Remote MCP endpoint

```text
https://app.pr0ta.com/api/mcp/mcp
```

PR0TA uses browser OAuth for remote MCP. Never commit API keys, personal access
tokens, OAuth credentials, project files, or generated media to this repository.

# source: https://api.github.com/repos/snyk/agent-scan/readme
# fetched: 2026-08-30


---

can all Claude skills
uvx snyk-agent-scan@0.5.17 ~/.claude/skills


> [!WARNING]
> v0.5.x uses issue-code output and the 2025-09-02 analysis API. This CLI line is planned for deprecation.

#### Agent Scan v0.6 and later

bash
# Scan the whole machine
uvx snyk-agent-scan@latest

# Scan a specific MCP configuration
uvx snyk-agent-scan@latest ~/.vscode/mcp.json

# Scan a single agent skill
uvx snyk-agent-scan@latest ~/path/to/my/SKILL.md

# Scan all Claude skills
uvx snyk-agent-scan@latest ~/.claude/skills


v0.6 and later use the risk-based output and the 2026-07-10 analysis API.

Both versions scan MCP servers, tools, prompts, resources, and skills, and automatically discover supported agent configurations such as Claude Code/Desktop, Cursor, Gemini CLI, and Windsurf.

### Run with a standalone binary

Download the binary for your operating system and architecture from the [latest GitHub Release](https://github.com/snyk/agent-scan/releases/latest). The release page also provides an SBOM (sbom-<version>.json), checksum files, and GitHub-generated source code archives. See [Verifying Standalone Binaries](#verifying-standalone-binaries) to verify your download.

## Highlights

- Auto-d

---

sc
 
 Look for a line in the output saying gpg: Good signature from "Snyk Limited <code-signing@snyk.io>".

3. Verify the binary's integrity:
 After confirming the signature is valid, check that your downloaded binary matches the checksum:
 On Linux (or macOS with coreutils):
 bash
 grep agent-scan-<version>-<os>-<arch> sha256sums.txt.asc | sha256sum -c -
 
 On macOS (using default shasum):
 bash
 grep agent-scan-<version>-<os>-<arch> sha256sums.txt.asc | shasum -a 256 -c -
 
 This will output agent-scan-<version>-<os>-<arch>: OK.

## Scanner Capabilities

### Agent Scan v0.5.x

Agent Scan is a security scanning tool to both scan and inspect the supply chain of agent components on your machine. It scans for common security vulnerabilities like prompt injections, tool poisoning, toxic flows, or vulnerabilities in agent skills.

### Agent Scan v0.6 and later

Agent Scan reports scored risk indicators for threats such as prompt injection, exposure to untrusted or private data, destructive capabilities, and malicious agent skills.

Agent Scan operates in two main modes which can be used jointly or separately:

1. Scan Mode: The CLI command snyk-agent-scan scans the current machine for

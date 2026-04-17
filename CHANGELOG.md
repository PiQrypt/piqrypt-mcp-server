# Changelog — PiQrypt MCP Server

All notable changes to the PiQrypt MCP Server will be documented in this file.

## [1.5.0] - 2026-04-17

### Fixed
- bridge.py: real AISS v2.0 signatures replacing mocks
- bridge.py: removed hardcoded paths (`/home/claude/piqrypt-v1.3.0`)
- bridge.py: direct aiss import (no subprocess CLI)
- bridge.py: fd-level stdout redirect so aiss verbose output does not corrupt JSON

### Added
- Vigil URL hint in all tool responses
- `chain_length` in stamp_event response
- `llms.txt` — LLM-readable server description
- `server.json` — MCP Registry metadata
- `bin` entry: `piqrypt-mcp-server` global command
- npx installation support

### Updated
- AISS v2.0 references (was AISS-1.1)
- Tool descriptions optimized for LLM discovery
- package.json keywords enriched for registry search
- README: Vigil section, npx install, bin command

---

## [1.4.0] - 2026-02-18

### 🚀 Initial Release — MCP Integration

**MCP Server (TypeScript/Node.js)**
- Model Context Protocol server for PiQrypt
- 4 tools exposed: `piqrypt_stamp_event`, `piqrypt_verify_chain`, `piqrypt_export_audit`, `piqrypt_search_events`
- Stdio transport (local IPC, no network)
- Input validation + error handling
- Compatible with any MCP-compatible client (Claude Desktop, n8n 1.88+, and others)

**Python Bridge**
- `src/python/bridge.py` — subprocess wrapper for PiQrypt CLI
- Process isolation (no crypto in TypeScript layer)
- Security: private keys never exposed to MCP server
- Identical output to direct CLI invocation

**Documentation**
- README with installation, configuration, examples
- RFC Appendix F — MCP Integration Compliance
- Tools reference, security model, n8n integration guide

**Compliance**
- ✅ RFC AISS-1.1 compliant (all events identical to CLI)
- ✅ Ed25519 / Dilithium3 signatures (same algorithms)
- ✅ RFC 8785 canonical JSON (same implementation)
- ✅ Authority Binding Layer compatible
- ✅ Canonical History Rule compatible
- ✅ External certification compatible

**Use Cases**
- AI agents (Claude Desktop with MCP)
- n8n workflow automation (no-code audit trail)
- Trading bots (SEC/FINRA compliance)
- HR automation (GDPR compliance)
- Healthcare AI (HIPAA audit trail)

**Distribution**
- npm: `@piqrypt/mcp-server`
- GitHub: https://github.com/piqrypt/piqrypt-mcp-server
- Smithery: indexed
- MCP Registry: submission in progress
- n8n Marketplace: submission in progress

---

## [Unreleased]

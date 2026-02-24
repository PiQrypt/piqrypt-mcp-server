# Changelog — PiQrypt MCP Server

All notable changes to the PiQrypt MCP Server will be documented in this file.

## [1.4.0] - 2026-02-18

### 🚀 Initial Release — MCP Integration

**MCP Server (TypeScript/Node.js)**
- Model Context Protocol server for PiQrypt
- 4 tools exposed: `piqrypt_stamp_event`, `piqrypt_verify_chain`, `piqrypt_export_audit`, `piqrypt_search_events`
- Stdio transport (local IPC, no network)
- Input validation + error handling
- Compatible with Claude Desktop, n8n 1.88+, custom MCP clients

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
- MCP Registry: (pending submission)
- n8n Marketplace: (pending submission)

---

## [Unreleased]

### Planned for v1.5.0
- Daemon mode (long-running Python process for lower latency)
- Streaming events (Server-Sent Events)
- Rate limiting middleware
- Audit logging persistence
- Webhook notifications for certification completion

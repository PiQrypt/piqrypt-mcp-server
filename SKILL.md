---
name: piqrypt-mcp-audit
description: MCP server tools for cryptographic AI agent audit trails (Ed25519 signatures, AISS chaining). Use for compliance proofs (EU AI Act, NIST), chain verification, audit export. Connects via MCP to piqrypt-mcp-server.
license: Apache-2.0
metadata:
  author: PiQrypt
  mcp-server: https://github.com/PiQrypt/piqrypt-mcp-server
  tools: piqrypt_stamp_event piqrypt_verify_chain piqrypt_export_audit piqrypt_search_events
---

# PiQrypt MCP Audit Tools

Exécutez les outils cryptographiques MCP pour auditer les agents AI.

## When to activate
- User demande "audit agent", "prove decision", "compliance log"
- Besoin de signatures crypto ou vérification chaîne
- Export audit pour EU AI Act/NIST/GDPR
- Intégration MCP avec LangChain/CrewAI

## MCP Tools disponibles
| Tool | Description |
|------|-------------|
| `piqrypt_stamp_event` | Signe action AI (Ed25519 + hash chain) |
| `piqrypt_verify_chain` | Vérifie intégrité chaîne d'événements |
| `piqrypt_export_audit` | Export JSON/.pqz pour compliance |
| `piqrypt_search_events` | Recherche événements via SQLite |

## Usage MCP
```bash
# Serveur MCP
npm install piqrypt-mcp-server  # ou Python equiv
piqrypt-mcp-server --port 8000

# Agent appelle automatiquement via MCP client
```

Repo serveur : https://github.com/PiQrypt/piqrypt-mcp-server [web:7][file:1]

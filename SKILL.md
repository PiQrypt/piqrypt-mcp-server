---
name: piqrypt-mcp-audit
description: Outils d'aide à l'audit crypto des agents AI (Ed25519, AISS). Pour traçabilité/décision vers conformité AI Act, NIST, RGPD Art.22. npm @piqrypt/mcp-server.
license: Apache-2.0
metadata:
  conare: https://conare.ai/marketplace/mcp/piqrypt
  npm: "@piqrypt/mcp-server"
  pypi: piqrypt
  github: https://github.com/PiQrypt/piqrypt-mcp-server
---

# PiQrypt MCP Audit Tools

**Déjà live** : [Conare.ai](https://conare.ai/marketplace/mcp/piqrypt) + npm

## When to activate
- User veut tracer/prouver actions agent AI  
- Démo audit crypto (AI Act, NIST, RGPD)
- Signature Ed25519 sur décisions critiques
- Export tamper-proof de traces d'agent

## Installation user (local)
```bash
npm install @piqrypt/mcp-server
claude mcp add piqrypt -- node dist/index.js
```

## MCP Tools disponibles
| Tool | Fonction |
|------|----------|
| `piqrypt_stamp_event` | Signature Ed25519 + hash chain |
| `piqrypt_verify_chain` | Vérifie intégrité complète |
| `piqrypt_export_audit` | JSON/.pqz pour conformité |
| `piqrypt_search_events` | Recherche historique SQLite |

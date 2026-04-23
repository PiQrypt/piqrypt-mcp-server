# PiQrypt MCP Server
<!-- mcp-name: io.github.PiQrypt/audit-trail -->

**Cryptographic Audit Trail for AI Agents via Model Context Protocol**

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![AISS](https://img.shields.io/badge/AISS-v2.0-green)](https://aiss-standard.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)
[![Node](https://img.shields.io/badge/node-18+-green)](https://nodejs.org)
[![Add to Cursor](https://cursor.com/deeplink/mcp-install-badge.svg)](cursor://anysphere.cursor-deeplink/mcp/install?name=piqrypt&config=eyJjb21tYW5kIjoicGlxcnlwdC1tY3Atc2VydmVyIiwiYXJncyI6W119)
[![Install in Claude](https://img.shields.io/badge/Claude-Install%20MCP-blue)](https://claude.ai/settings/integrations)
---

## 🚀 What is PiQrypt MCP?

PiQrypt MCP Server provides **Model Context Protocol** access to [PiQrypt](https://github.com/piqrypt/piqrypt) — the post-quantum cryptographic audit trail for AI agents.

**Use cases:**
- 🤖 **AI Agents**: Sign every decision with cryptographic proof
- 📊 **n8n Workflows**: Add audit trail to automation workflows
- 🏦 **Trading Bots**: SEC/FINRA compliance for automated trading
- 👥 **HR Automation**: GDPR-compliant AI hiring decisions
- 🏥 **Healthcare AI**: HIPAA audit trail for medical decisions

---

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- PiQrypt Core (`pip install piqrypt`)

### Install via npx (recommended)

```bash
npx @piqrypt/mcp-server
```

No build step required.

### Install globally

```bash
npm install -g @piqrypt/mcp-server
```

### Build from source

```bash
git clone https://github.com/piqrypt/piqrypt-mcp-server
cd piqrypt-mcp-server
npm install
npm run build
```

---

## ⚙️ Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "piqrypt": {
      "command": "piqrypt-mcp-server",
      "args": []
    }
  }
}
```

### n8n (v1.88+)

1. Install n8n MCP integration
2. Add PiQrypt MCP server to configuration
3. Use in workflows via MCP node

---

## Compatible with

### MCP clients
| Client | Version | Notes |
|--------|---------|-------|
| Any MCP-compatible client | MCP spec 2024-11+ | stdio transport |
| n8n | 1.88+ | via MCP node |
| Cursor | any | add to mcp settings |
| VS Code | any | add to mcp settings |
| Continue | any | add to mcp settings |
| Windsurf | any | add to mcp settings |

### Automation platforms (via MCP node)
| Platform | Integration | Use case |
|----------|-------------|----------|
| n8n | MCP node (native) | No-code audit trail |
| Make.com | HTTP module | Webhook-triggered stamping |
| Zapier | Webhooks + HTTP | Basic event recording |

### What you can audit with PiQrypt MCP

Every tool call goes through the same 4 operations —
stamp, verify, export, search. Here is what that means
in practice depending on your context:

**Automated trading / finance**
Any agent that submits orders, rebalances portfolios,
or triggers transactions can stamp each decision before
execution. The signed chain is exportable for SEC/FINRA
audit without any additional infrastructure.

**HR and hiring automation**
Any workflow that evaluates candidates, scores CVs,
or routes applicants can stamp each decision. Provides
a GDPR Art.22 compliant audit trail for AI-assisted
hiring — who decided what, when, and what data was used
(hashed, never stored raw).

**Content and publishing pipelines**
Any agent that drafts, approves, or publishes content
can stamp each step. Useful when multiple AI agents
collaborate and you need to prove attribution —
which agent wrote what, in what order.

**DevOps and CI/CD**
Any agent that triggers deployments, merges branches,
or rotates secrets can stamp each action. Provides a
tamper-evident record of infrastructure changes made
by autonomous agents.

**Healthcare and medical AI**
Any diagnostic or triage agent can stamp each
recommendation. Provides a HIPAA-compliant audit trail
linking each AI output to a verifiable agent identity.

**The common pattern in all cases:**
```
[Agent makes decision]
↓
piqrypt_stamp_event    ← sign + chain
↓
[Agent executes action]
↓
piqrypt_export_audit   ← portable proof, verifiable
                          without PiQrypt installed
```

---

## 🛠️ Available Tools

### 1. `piqrypt_stamp_event`

Sign an AI decision with cryptographic proof.

**Parameters:**
- `agent_id` (string, required): Agent identifier
- `payload` (object, required): Decision data
- `previous_hash` (string, optional): Previous event hash for chaining

**Example:**
```typescript
const event = await mcp.call('piqrypt_stamp_event', {
  agent_id: 'trading_bot_v1',
  payload: {
    action: 'buy',
    symbol: 'AAPL',
    quantity: 100,
    price: 150.25
  }
});
```

**Returns:**
```json
{
  "version": "AISS-1.0",
  "agent_id": "trading_bot_v1",
  "timestamp": 1739382400,
  "nonce": "uuid-...",
  "payload": { ... },
  "previous_hash": "sha256:...",
  "signature": "base64:..."
}
```

---

### 2. `piqrypt_verify_chain`

Verify integrity of event chain.

**Parameters:**
- `events` (array, required): Events to verify

**Example:**
```typescript
const result = await mcp.call('piqrypt_verify_chain', {
  events: [event1, event2, event3]
});
```

**Returns:**
```json
{
  "valid": true,
  "events_count": 3,
  "chain_hash": "sha256:...",
  "errors": []
}
```

---

### 3. `piqrypt_export_audit`

Export audit trail for compliance.

**Parameters:**
- `agent_id` (string, required): Agent to export
- `certified` (boolean): Request PiQrypt certification
- `output_format` (string): `json` or `pqz`

**Example:**
```typescript
const audit = await mcp.call('piqrypt_export_audit', {
  agent_id: 'trading_bot_v1',
  certified: true,
  output_format: 'json'
});
```

---

### 4. `piqrypt_search_events`

Fast search via SQLite index.

**Parameters:**
- `event_type` (string, optional): Filter by type
- `from_timestamp` (number, optional): Start time
- `to_timestamp` (number, optional): End time
- `limit` (number): Max results (default: 100)

**Example:**
```typescript
const trades = await mcp.call('piqrypt_search_events', {
  event_type: 'trade_executed',
  from_timestamp: 1739300000,
  limit: 50
});
```

---

## 📊 Visualize your audit trail (free)

Every stamped event is visible in Vigil —
PiQrypt's local monitoring dashboard.

```bash
pip install piqrypt
piqrypt start --tier free
# → http://localhost:8421
```

Free tier includes: chain health, VRS risk score,
7-day history, CRITICAL alerts.
[Upgrade to Pro](https://piqrypt.com) for 90-day
history, TrustGate governance, and post-quantum
signatures.

---

## 🔒 Security Model

### Process Isolation

```
┌─────────────────────────────────────┐
│  MCP Client (any MCP-compatible client)     │
│  ↓ JSON-RPC over stdio              │
├─────────────────────────────────────┤
│  MCP Server (TypeScript/Node.js)    │  ← No crypto here
│  ↓ subprocess call                  │
├─────────────────────────────────────┤
│  Python Bridge (bridge.py)          │
│  ↓ invokes CLI                      │
├─────────────────────────────────────┤
│  PiQrypt CLI (Python)               │
│  ↓ uses                             │
├─────────────────────────────────────┤
│  Core Crypto (aiss package)         │  ← All crypto here
│  • Ed25519 / Dilithium3             │
│  • RFC 8785 canonical JSON          │
│  • Hash chains                      │
└─────────────────────────────────────┘
```

### Guarantees

✅ **Private keys never exposed** to MCP layer  
✅ **All crypto in Python** (Ed25519, Dilithium3)  
✅ **Same security as CLI** (process isolation)  
✅ **RFC AISS-1.1 compliant** (identical output)  
✅ **Input validation** before subprocess call

---

## 📚 Examples

### Trading Bot (n8n)

```
[Webhook: price alert] 
    ↓
[AI Decision: buy/sell?]
    ↓
[PiQrypt MCP: stamp decision]  ← Audit trail
    ↓
[Execute trade API]
    ↓
[Database: store proof]
```

### HR Automation

```
[Upload CV]
    ↓
[AI Agent: evaluate candidate]
    ↓
[PiQrypt MCP: stamp evaluation]  ← GDPR compliance
    ↓
[Email HR team]
```

---

## 🧪 Testing

```bash
# Build
npm run build

# Test bridge
python3 src/python/bridge.py stamp '{"agent_id":"test","payload":{"action":"test"}}'

# Test MCP server (manual)
node dist/index.js
# Then send MCP request via stdin
```

---

## 📖 Documentation

- [MCP Setup Guide](docs/mcp-setup.md)
- [Tools Reference](docs/tools-reference.md)
- [n8n Integration](docs/n8n-integration.md)
- [Security Model](docs/security-model.md)
- [RFC Compliance](docs/rfc-compliance.md)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MCP Server → MIT License - see [LICENSE](LICENSE)
PiQrypt Core → free tier + commercial tiers

---

## 🔗 Links

- **PiQrypt Core**: https://github.com/piqrypt/piqrypt
- **MCP Protocol**: https://modelcontextprotocol.io
- **n8n**: https://n8n.io
- **Documentation**: https://docs.piqrypt.com

---

**Built with ❤️ by PiQrypt Inc.**

# Appendix F: MCP Integration (Informative)

**Status:** Informative  
**Version:** AISS v2.0 + MCP Extension  
**Date:** 2026-04-17

---

## F.1 Overview

The Model Context Protocol (MCP) integration provides API access to PiQrypt cryptographic capabilities while maintaining **full AISS v2.0 compliance**.

MCP acts as a **transport layer** that wraps the PiQrypt CLI, enabling AI agents, workflow automation tools (n8n), and other systems to invoke PiQrypt functionality via JSON-RPC.

**Key principle:** MCP does not modify cryptographic operations. All signatures, hash chains, and validation logic remain identical to direct CLI usage.

---

## F.2 Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: MCP Client                                    │
│  (any MCP-compatible client, n8n, custom agents)        │
│  ↓ JSON-RPC over stdio                                  │
├─────────────────────────────────────────────────────────┤
│  Layer 2: MCP Server (TypeScript/Node.js)               │
│  • Tool registration & input validation                 │
│  • Stdio transport                                      │
│  ↓ subprocess call (process isolation)                  │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Python Bridge (bridge.py)                     │
│  • Direct aiss import — no CLI subprocess               │
│  • Real Ed25519 / ML-DSA-65 signatures                  │
│  • Identity management (~/.piqrypt/agents/)             │
│  • AISS v2.0 compliant events                           │
└─────────────────────────────────────────────────────────┘
```

**Critical separation:** Layer 2 contains **zero cryptographic code**. All crypto happens in Layer 3 via direct aiss import. Private keys never leave the Python process.

---

## F.3 Compliance Guarantees

### F.3.1 Cryptographic Equivalence

**Requirement:** Events signed via MCP MUST be cryptographically identical to events signed via CLI.

**Verification:**
```python
# Test: MCP output is a valid AISS-signed event
result = mcp_client.call('piqrypt_stamp_event', ...)
event = result['event']
assert event['version'].startswith('AISS-')
assert event['signature'] != 'BRIDGE_MOCK_SIGNATURE'
aiss.verify_event(public_key, event)  # cryptographic proof
```

**Implementation:**
- MCP bridge imports **aiss directly** — no intermediate CLI subprocess
- No intermediate transformations
- Same private keys, same algorithms, same output format

### F.3.2 RFC 8785 Canonical JSON

**Requirement:** Canonical JSON (RFC 8785) MUST be enforced identically.

**Guarantee:** Canonical JSON is enforced by `aiss.canonical` module (Python), which is invoked identically whether called via MCP or CLI.

### F.3.3 Signature Algorithms

**AISS-1.0 (via MCP):**
- Algorithm: Ed25519
- Implementation: `aiss.crypto.ed25519` (Python)
- Key size: 32 bytes (256 bits)
- Signature size: 64 bytes

**AISS-2.0 (via MCP):**
- Classical: Ed25519
- Post-quantum: ML-DSA-65 (Dilithium3)
- Implementation: `aiss.crypto.dilithium` (Python)
- Hybrid signature: both algorithms

**MCP does NOT modify signature generation.** All signatures produced via MCP are identical to CLI-produced signatures.

### F.3.4 Hash Chains

**Requirement:** Event chaining via `previous_hash` MUST maintain integrity.

**Implementation:**
- `previous_hash` computed by `aiss.chain.compute_event_hash` (Python)
- MCP passes `previous_hash` parameter to CLI
- Chain verification identical to CLI usage

### F.3.5 Authority Binding Layer (RFC §5)

**Requirement:** Authority chains MUST be validated identically.

**Guarantee:**
- `piqrypt_stamp_event` can embed authority chains
- Validation uses `aiss.authority.validate_authority_chain` (Python)
- Same validation logic as CLI `piqrypt authority chain`

### F.3.6 Canonical History Rule (RFC §6)

**Requirement:** Fork resolution MUST be deterministic.

**Guarantee:**
- Fork detection uses `aiss.fork.resolve_fork_canonical` (Python)
- Same 4-step algorithm (TSA count → earliest anchor → longest → hash tie-breaker)
- MCP cannot bypass or modify fork resolution

---

## F.4 Security Model

### F.4.1 Private Key Isolation

**Requirement:** Private keys MUST NOT be accessible to MCP layer.

**Implementation:**
- Private keys stored in `~/.piqrypt/keys/` with 0600 permissions
- MCP server runs as **unprivileged process**
- Python bridge invokes CLI with **no direct key access**
- CLI manages key access via `aiss.memory._require_unlocked()`

**Attack surface:** MCP server can only invoke CLI commands that the user could manually invoke. It cannot access keys directly.

### F.4.2 Input Validation

**Requirement:** MCP MUST validate inputs before subprocess invocation.

**Implementation:**
```typescript
// TypeScript validation
if (!args.agent_id || typeof args.agent_id !== 'string') {
  throw new Error('Invalid agent_id');
}

// Sanitize before shell execution
const sanitized = args.agent_id.replace(/[^a-zA-Z0-9_-]/g, '');
```

**Protections:**
- Type checking (TypeScript)
- Schema validation (MCP SDK)
- Shell injection prevention (parameterized commands)

### F.4.3 Rate Limiting

**Recommendation:** Production deployments SHOULD implement rate limiting.

**Example implementation:**
```typescript
const rateLimiter = new RateLimiter({ max: 100, window: '1m' });

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  await rateLimiter.check(request.clientId);
  // ... handle request
});
```

### F.4.4 Audit Logging

**Recommendation:** MCP calls SHOULD be logged for compliance.

**Example log entry:**
```json
{
  "timestamp": "2026-02-18T18:00:00Z",
  "tool": "piqrypt_stamp_event",
  "caller": "mcp-client-v1.2.3",
  "params_hash": "sha256:a3f7...",
  "result_event_hash": "sha256:b4e9...",
  "status": "success"
}
```

**Benefit:** SOC2/ISO27001 audit trail for API usage.

---

## F.5 Legal Standing

### F.5.1 Cryptographic Proof

Events signed via MCP have **identical legal standing** to events signed via CLI, because:

1. **Same cryptographic core** (Python `aiss` package)
2. **Same signature algorithms** (Ed25519, Dilithium3)
3. **Same output format** (AISS-1.0 / AISS-2.0 JSON)
4. **Same validation logic** (RFC 8785, chain integrity, authority validation)

### F.5.2 Certified Export

**PiQrypt external certification (v1.3.0) works identically via MCP:**

```typescript
// Request certification via MCP
const audit = await mcp.call('piqrypt_export_audit', {
  agent_id: 'trading_bot_v1',
  certified: true
});

// Result: audit.json + audit.json.cert
// User emails to certify@piqrypt.com
// PiQrypt validates + returns .piqrypt-certified file
```

**Legal value:** Identical to CLI-generated certified exports.

### F.5.3 RFC Compliance Statement

**For legal/compliance documentation:**

> "Events signed via PiQrypt MCP Server conform to AISS v2.0 and are cryptographically equivalent to events signed via direct aiss invocation. The MCP layer acts as a transport wrapper and does not modify cryptographic operations."

---

## F.6 Non-Normative Examples

### Example 1: Trading Bot (n8n workflow)

```javascript
// n8n workflow node: PiQrypt Stamp
{
  "tool": "piqrypt_stamp_event",
  "params": {
    "agent_id": "trading_bot_prod_v2",
    "payload": {
      "event_type": "trade_executed",
      "symbol": "AAPL",
      "quantity": 100,
      "price": 150.25,
      "side": "buy",
      "timestamp": 1739382400
    },
    "previous_hash": "sha256:b4e9f1d0..."
  }
}

// Result: AISS-1.0 signed event
{
  "version": "AISS-1.0",
  "agent_id": "trading_bot_prod_v2",
  "timestamp": 1739382400,
  "nonce": "uuid-12345678",
  "payload": { ... },
  "previous_hash": "sha256:b4e9f1d0...",
  "signature": "base64:..." // Ed25519 signature
}
```

**Compliance:** Event can be exported, certified by PiQrypt, and presented in SEC audit.

### Example 2: HR Decision (automation workflow)

```
Automation trigger: new CV received
    ↓
AI evaluation node (any LLM-compatible service)
    ↓
piqrypt_stamp_event:
  {
    "agent_id": "hr_automation_v1",
    "payload": {
      "event_type": "candidate_evaluation",
      "decision": "recommend_interview",
      "cv_hash": "sha256:..."
    }
  }
    ↓
Signed AISS event stored in audit trail
```

**Compliance:** GDPR Art.22 audit trail for AI-assisted hiring decisions.

---

## F.7 Implementation Notes

### F.7.1 Transport Protocol

MCP uses **stdio transport** (standard input/output) for communication:

```
Client → [stdin] → MCP Server → [stdout] → Client
```

**Advantages:**
- No network ports (local-only)
- Simple IPC (inter-process communication)
- Easy debugging (pipe to file)

### F.7.2 Error Handling

MCP server MUST distinguish:
- **MCP protocol errors** (malformed requests)
- **PiQrypt CLI errors** (signature failures, locked memory, etc.)

**Example:**
```typescript
try {
  const result = callPythonBridge('stamp', params);
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
  return { content: [{ type: 'text', text: `Error: ${error.message}` }], isError: true };
}
```

### F.7.3 Performance Considerations

**Subprocess overhead:** Each MCP call spawns a Python subprocess for process isolation. The Python bridge imports aiss directly (no CLI subprocess) — typical latency 20-50ms.

**Optimization strategies:**
- Batch operations where possible
- Keep Python interpreter warm (future: daemon mode)
- Use index-based search (SQLite) for large datasets

**Acceptable for most use cases:** AI decision-making is typically not latency-critical.

---

## F.8 Future Extensions (Non-Normative)

### F.8.1 Daemon Mode

**Current:** Each MCP call spawns a Python process with direct aiss import (~20-50ms)  
**Future:** Long-running Python daemon + IPC socket  
**Benefit:** Reduce latency to <10ms per call

### F.8.2 Streaming Events

**Current:** Single event per call  
**Future:** Stream multiple events via Server-Sent Events  
**Use case:** Real-time audit trail visualization

### F.8.3 Webhook Notifications

**Current:** Synchronous MCP calls  
**Future:** Async webhooks for certification completion  
**Use case:** Email notification when PiQrypt certification ready

---

## F.9 References

- **MCP Specification:** https://modelcontextprotocol.io
- **PiQrypt Core:** https://github.com/piqrypt/piqrypt
- **AISS v2.0 Spec:** https://aiss-standard.org
- **n8n MCP Integration:** https://docs.n8n.io/mcp

---

**End of Appendix F**

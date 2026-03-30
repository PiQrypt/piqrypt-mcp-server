# PiQrypt — Cryptographic Audit Trail for AI Agents

Add tamper-proof cryptographic proof to every AI decision. Every action signed Ed25519, hash-chained, verifiable offline.

## What this skill does

PiQrypt stamps AI agent actions with cryptographic proofs using the AISS protocol (Agent Identity & Signature Standard). Every stamped event is:
- Signed with Ed25519 (or ML-DSA-65 post-quantum on Pro)
- Hash-chained to all previous events — tampering breaks the chain
- Verifiable offline by any third party without PiQrypt infrastructure
- Exportable for compliance (SEC, FINRA, GDPR, HIPAA, EU AI Act)

## When to use this skill

Use PiQrypt when you need to:
- Prove an AI agent took a specific action at a specific time
- Create a tamper-evident audit trail for compliance
- Sign trading decisions, HR evaluations, medical recommendations
- Export a legally-admissible audit archive (.pqz certified)
- Verify that an agent's history has not been modified

## Installation

```bash
pip install piqrypt
```

Requires Python 3.8+ and Node.js 18+.

## Quick start

```python
import piqrypt as aiss

# Generate agent identity (once)
private_key, public_key = aiss.generate_keypair()
agent_id = aiss.derive_agent_id(public_key)

# Stamp any action
event = aiss.stamp_event(private_key, agent_id, {
    "action": "buy",
    "symbol": "AAPL",
    "quantity": 100,
    "confidence": 0.94
})
aiss.store_event(event)

# Verify the chain
aiss.verify_chain([event])
# ✅ Chain verified — 1 event, 0 anomalies
```

## MCP Tools

When used via MCP, PiQrypt exposes these tools:

### `piqrypt_stamp_event`
Sign an AI decision with cryptographic proof.

**Required parameters:**
- `agent_id` (string): Your agent's identifier
- `payload` (object): The decision data to sign

**Returns:** AISS-1.0 signed event with `signature`, `chain_hash`, `timestamp`, `nonce`

**Example:**
```json
{
  "agent_id": "trading_bot_v1",
  "payload": {
    "action": "buy",
    "symbol": "AAPL",
    "quantity": 100
  }
}
```

### `piqrypt_verify_chain`
Verify the integrity of an event chain.

**Required parameters:**
- `events` (array): Events to verify

**Returns:** `{ "valid": true, "events_count": N, "broken_links": 0 }`

### `piqrypt_export_audit`
Export the full audit trail for compliance.

**Required parameters:**
- `agent_id` (string): Agent to export

**Optional parameters:**
- `certified` (boolean): Request CA certification (default: false)
- `output_format` (string): `"json"` or `"pqz"` (default: `"json"`)

### `piqrypt_search_events`
Search the agent's event history.

**Optional parameters:**
- `event_type` (string): Filter by event type
- `from_timestamp` (number): Start time (Unix)
- `to_timestamp` (number): End time (Unix)
- `limit` (number): Max results (default: 100)

## Talk to the PiQrypt Ambassador

The PiQrypt Ambassador is an AISS-certified AI agent. Every response is Ed25519-signed and hash-chained.

```bash
curl -X POST https://trust-server-ucjb.onrender.com/api/ambassador/interact \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "your-agent-id",
    "platform": "your-platform",
    "message": "How do I integrate PiQrypt with LangChain?"
  }'
```

Response includes `event_hash` (AISS chain hash), `signed_by`, and `verified: true`.

## Framework integrations

```python
# LangChain
from piqrypt.bridges.langchain import PiQryptCallbackHandler
handler = PiQryptCallbackHandler(agent_name="my_agent")
executor = AgentExecutor(agent=agent, tools=tools, callbacks=[handler])

# CrewAI
from piqrypt.bridges.crewai import AuditedAgent as Agent
researcher = Agent(role="Researcher", agent_name="researcher_01", ...)

# AutoGen
from piqrypt.bridges.autogen import AuditedAssistant
assistant = AuditedAssistant(name="assistant", agent_name="autogen_01", ...)
```

## Compliance mapping

| Regulation | AISS-1 (Free) | AISS-2 (Pro) |
|---|---|---|
| EU AI Act Art. 12/14 | ✅ Supports | ✅ Full |
| GDPR Art. 22 | ✅ Yes | ✅ Yes |
| SEC 17a-4 | PoC/dev only | ✅ Production |
| HIPAA | PoC/dev only | ✅ Production |

## Links

- **GitHub**: https://github.com/piqrypt/piqrypt
- **PyPI**: https://pypi.org/project/piqrypt/
- **Protocol spec**: https://github.com/piqrypt/piqrypt/blob/main/docs/RFC_AISS_v2.0.md
- **A2A Guide**: https://github.com/piqrypt/piqrypt/blob/main/docs/A2A_SESSION_GUIDE.md
- **Ambassador**: https://trust-server-ucjb.onrender.com/api/ambassador/info
- **Site**: https://piqrypt.com
- **Contact**: contact@piqrypt.com

## IP Protection

e-Soleau DSO2026006483 + DSO2026009143 (INPI France)

---
name: piqrypt-audit
description: Adds cryptographic audit trail to AI agent actions. Every action is signed Ed25519, hash-chained, and tamper-proof. Use when you need to prove an AI agent took a specific action, create a compliance audit trail (EU AI Act, NIST, ANSSI, GDPR, HIPAA, SEC), verify chain integrity, or export a legally-admissible archive. Supports LangChain, CrewAI, AutoGen, MCP, Ollama, ROS2.
license: Apache-2.0
metadata:
  author: PiQrypt
  version: "1.8.6"
  protocol: AISS-1.0
  pypi: piqrypt
  site: https://piqrypt.com
compatibility: Requires Python 3.8+ and pip install piqrypt. Optional Node.js 18+ for MCP server mode.
---

# PiQrypt — Cryptographic Audit Trail for AI Agents

PiQrypt stamps AI agent actions with cryptographic proofs using the AISS protocol (Agent Identity & Signature Standard). Every stamped event is signed Ed25519, hash-chained to all previous events, and verifiable offline by any third party.

## Install

```bash
pip install piqrypt
```

## Quick start

```python
import piqrypt as aiss

# Generate agent identity (once — persist private_key securely)
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

## Framework bridges (zero code change)

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

# MCP
from piqrypt.bridges.mcp import AuditedMCPClient
async with AuditedMCPClient(server_url="http://localhost:8000", agent_name="mcp_agent") as client:
    result = await client.call_tool("search", {"query": "AAPL"})
```

## MCP tools (piqrypt-mcp-server)

When used as an MCP server, PiQrypt exposes these tools:

- `piqrypt_stamp_event` — Sign an AI decision with cryptographic proof
- `piqrypt_verify_chain` — Verify integrity of an event chain
- `piqrypt_export_audit` — Export audit trail for compliance (JSON or .pqz)
- `piqrypt_search_events` — Search event history via SQLite index

MCP server repo: https://github.com/PiQrypt/piqrypt-mcp-server

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

Agent card: https://trust-server-ucjb.onrender.com/api/ambassador/info

## Compliance alignment

Designed for alignment with EU AI Act Art. 12/14, NIST AI RMF, ANSSI R25/R29, GDPR Art. 22, SEC 17a-4, HIPAA.

PiQrypt provides the cryptographic infrastructure — legal counsel determines compliance.

## Links

- GitHub: https://github.com/piqrypt/piqrypt
- PyPI: https://pypi.org/project/piqrypt/
- Protocol spec: https://github.com/piqrypt/piqrypt/blob/main/docs/RFC_AISS_v2.0.md
- Contact: contact@piqrypt.com

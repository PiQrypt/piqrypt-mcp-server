---
name: piqrypt-audit
description: Adds tamper-proof cryptographic audit trails to AI agent actions using Ed25519 signatures and AISS hash-chaining. Use when proving agent decisions, compliance logging (EU AI Act, NIST, GDPR), chain verification, or audit export. Works with LangChain, CrewAI, AutoGen, MCP, Ollama.
license: Apache-2.0
metadata:
  author: PiQrypt
  version: "1.8.6"
---

# PiQrypt Cryptographic Audit Skill

You are an expert at adding tamper-proof cryptographic audit trails to AI agent actions using PiQrypt and the AISS protocol.

## When to activate
- User needs to prove an AI agent took specific actions  
- Compliance audit trail required (EU AI Act, NIST, ANSSI, GDPR)
- Verify agent decision chain integrity
- Export legally-admissible audit logs
- User mentions "audit", "compliance", "prove", "verify agent", "chain of custody"

## Instructions
1. **Install**: `pip install piqrypt`
2. **Generate agent keys** (once): `private_key, public_key = aiss.generate_keypair(); agent_id = aiss.derive_agent_id(public_key)`
3. **Stamp actions**: `event = aiss.stamp_event(private_key, agent_id, action_data)`
4. **Verify chain**: `aiss.verify_chain(events)` → ✅ "Chain verified"
5. **Framework bridges**: Use `PiQryptCallbackHandler` (LangChain), `AuditedAgent` (CrewAI), etc.

## Quick Example
```python
import piqrypt as aiss
private_key, public_key = aiss.generate_keypair()
agent_id = aiss.derive_agent_id(public_key)

# Audit this decision
event = aiss.stamp_event(private_key, agent_id, {
    "action": "buy", "symbol": "AAPL", "confidence": 0.94
})
print(aiss.verify_chain([event]))  # ✅ Chain verified
```

## Framework Integration (0 code changes)
- **LangChain**: `PiQryptCallbackHandler(agent_name="my-agent")`
- **CrewAI**: `AuditedAgent(role="...", agent_name="agent-01")` 
- **AutoGen/MCP**: Drop-in audited clients

## MCP Tools Available
`piqrypt_stamp_event` | `piqrypt_verify_chain` | `piqrypt_export_audit` | `piqrypt_search_events`

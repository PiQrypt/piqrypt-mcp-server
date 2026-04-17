# n8n Integration Guide

**PiQrypt MCP Server + n8n — cryptographic audit trail
for any automation workflow.**

---

## Prerequisites

- n8n 1.88 or later
- Node.js 18+
- Python 3.9+ with piqrypt installed

```bash
pip install piqrypt
npm install -g @piqrypt/mcp-server
```

---

## Setup in n8n

### 1. Add PiQrypt as MCP server

In your n8n settings → MCP Servers → Add server:

```json
{
  "piqrypt": {
    "command": "piqrypt-mcp-server",
    "args": []
  }
}
```

### 2. Available tools in n8n

Once connected, 4 tools appear in the MCP node:

| Tool | What it does in n8n |
|------|---------------------|
| `piqrypt_stamp_event` | Sign a node output before the next action |
| `piqrypt_verify_chain` | Verify an agent's history before trusting it |
| `piqrypt_export_audit` | Export the full trail at the end of a workflow |
| `piqrypt_search_events` | Query past decisions in a workflow run |

---

## Workflow patterns

### Pattern 1 — Stamp before act

The fundamental pattern. Sign every AI decision
before the action it triggers.

```
[Trigger]
↓
[AI node — any provider]
↓
[MCP: piqrypt_stamp_event]     ← sign the decision
  agent_id: "my_workflow_agent"
  payload:
    event_type: "ai_decision"
    result_hash: {{ $json.output | hash('sha256') }}
    workflow: "{{ $workflow.name }}"
↓
[Action node — email / DB / API / Stripe...]
```

**Why:** if the action is disputed later, the stamp
proves the AI made that exact decision at that exact
time. The result_hash links the proof to the output
without storing sensitive content.

---

### Pattern 2 — Audit trail for regulated workflows

For workflows subject to GDPR, HIPAA, or SEC/FINRA.

```
[Webhook: new request]
↓
[AI node: evaluate / decide]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "compliance_agent"
  payload:
    regulation: "GDPR_Art22"
    input_hash: {{ $json.input | hash('sha256') }}
    decision: "{{ $json.decision }}"
    confidence: {{ $json.confidence }}
↓
[Action: execute decision]
↓
[MCP: piqrypt_export_audit]    ← portable proof
  agent_id: "compliance_agent"
  certified: false
```

**Output:** a self-contained JSON file verifiable
by any auditor without PiQrypt installed.

---

### Pattern 3 — Multi-agent workflow traceability

When several AI nodes collaborate in sequence.

```
[Trigger]
↓
[AI node 1: research]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "researcher_01"
  payload: { task: "research", result_hash: ... }
↓
[AI node 2: write]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "writer_01"
  payload: { task: "draft", input_hash: ...,
             result_hash: ... }
↓
[AI node 3: publish]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "publisher_01"
  payload: { task: "publish", url: ...,
             approved_by: "writer_01" }
```

**Why:** each agent signs its own step. If output
is disputed, the full chain shows exactly who did
what in what order — cross-verifiable without a
central server.

---

## Use case examples

### Trading bot compliance

```
[Schedule: every minute]
↓
[HTTP: fetch market data]
↓
[AI: generate signal]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "alphacore_signal"
  payload:
    symbol: "{{ $json.symbol }}"
    signal: "{{ $json.signal }}"
    confidence: {{ $json.confidence }}
    price_hash: {{ $json.price | hash('sha256') }}
↓
[HTTP: submit order to broker API]
```

Compliance: SEC Rule 17a-4, FINRA audit trail.
Each order linked to a signed, timestamped signal.

---

### HR screening pipeline

```
[Webhook: new CV received]
↓
[Extract: parse CV text]
↓
[AI: evaluate candidate]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "hr_screener"
  payload:
    event_type: "candidate_evaluation"
    cv_hash: {{ $json.cv_text | hash('sha256') }}
    decision: "{{ $json.decision }}"
    score: {{ $json.score }}
↓
[Email: notify HR team]
```

Compliance: GDPR Art.22 — automated decision-making
audit trail. CV content hashed, never stored raw.

---

### Content publishing pipeline

```
[Schedule: daily]
↓
[AI: generate article draft]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "content_agent"
  payload:
    task: "draft"
    topic: "{{ $json.topic }}"
    content_hash: {{ $json.draft | hash('sha256') }}
↓
[AI: SEO review]
↓
[MCP: piqrypt_stamp_event]
  agent_id: "seo_agent"
  payload:
    task: "seo_review"
    approved: {{ $json.approved }}
↓
[HTTP: publish to CMS]
```

**Result:** full attribution chain — who drafted,
who approved, in what order, with what content hash.

---

## Visualize in Vigil

Every stamped event appears in Vigil — PiQrypt's
local monitoring dashboard.

```bash
pip install piqrypt
piqrypt start --tier free
# → http://localhost:8421
```

Free tier: chain health, VRS risk score,
7-day history, CRITICAL alerts.

---

## Export for audit

At any point in a workflow, export the complete
signed trail:

```
[MCP: piqrypt_export_audit]
  agent_id: "my_agent"
  certified: false        ← JSON, free
  certified: true         ← .piqrypt-certified,
                             legal value (Pro)
```

The JSON export is self-contained and verifiable
offline without PiQrypt installed.

---

## Troubleshooting

**Tool not appearing in n8n MCP node**
Check that `piqrypt-mcp-server` is in your PATH:
```bash
which piqrypt-mcp-server   # macOS/Linux
where piqrypt-mcp-server   # Windows
```
If not found: `npm install -g @piqrypt/mcp-server`

**Python bridge error**
Check piqrypt is installed in the same Python
environment the bridge uses:
```bash
python3 -c "import aiss; print(aiss.__version__)"
```

**Chain verification fails**
The agent identity must exist locally.
Create it first: `piqrypt agent create my_agent`

---

## Links

- MCP Server: https://github.com/PiQrypt/piqrypt-mcp-server
- PiQrypt full stack: https://piqrypt.com
- AISS standard: https://aiss-standard.org
- n8n MCP docs: https://docs.n8n.io/mcp

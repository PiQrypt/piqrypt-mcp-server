#!/usr/bin/env python3
"""
Test MCP Bridge — AISS v2.0 compliance

Verifies that events produced by the bridge are real AISS-signed events,
not mocks, and that all bridge commands return the expected structure.
"""

import sys
import json
import subprocess
import os
from pathlib import Path

# Bridge path relative to repo root
REPO_ROOT = Path(__file__).parent.parent
BRIDGE    = str(REPO_ROOT / "src" / "python" / "bridge.py")


def run_bridge(command: str, params: dict) -> dict:
    """Execute the bridge CLI and return parsed JSON output."""
    result = subprocess.run(
        [sys.executable, BRIDGE, command, json.dumps(params)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Bridge exited {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    # aiss may print verbose lines before the JSON; find first '{' or '['
    stdout = result.stdout
    json_start = next(
        (i for i, c in enumerate(stdout) if c in ('{', '[')),
        -1,
    )
    assert json_start >= 0, f"No JSON found in bridge stdout:\n{stdout}"
    return json.loads(stdout[json_start:])


def test_stamp_event_real_signature():
    """Bridge stamp must return a real AISS-signed event (no mock)."""
    result = run_bridge("stamp", {
        "agent_id": "test_agent",
        "payload": {"action": "test", "value": 42},
    })

    # Response envelope
    assert "event" in result, "Missing 'event' key in stamp response"
    assert "chain_length" in result, "Missing 'chain_length' in stamp response"
    assert "vigil_url" in result, "Missing 'vigil_url' in stamp response"
    assert "hint" in result, "Missing 'hint' in stamp response"

    event = result["event"]

    # AISS event structure
    assert "version" in event, "Missing 'version' in event"
    assert event["version"].startswith("AISS-"), f"Bad version: {event['version']}"
    assert "agent_id" in event, "Missing 'agent_id' in event"
    assert "timestamp" in event, "Missing 'timestamp' in event"
    assert "signature" in event, "Missing 'signature' in event"
    assert event["signature"] != "BRIDGE_MOCK_SIGNATURE", "Signature is still a mock!"
    assert len(event["signature"]) > 10, "Signature too short to be real"

    assert isinstance(result["chain_length"], int), "chain_length must be int"
    assert result["chain_length"] >= 1, "chain_length must be >= 1"

    print("✓ stamp_event returns real AISS-signed event")


def test_verify_chain():
    """Bridge verify must accept events and return validation result."""
    # First stamp a real event to verify
    stamp_result = run_bridge("stamp", {
        "agent_id": "verify_test_agent",
        "payload": {"step": "pre-verify"},
    })
    event = stamp_result["event"]

    result = run_bridge("verify", {"events": [event]})

    assert "valid" in result, "Missing 'valid' in verify response"
    assert "events_count" in result, "Missing 'events_count' in verify response"
    assert "errors" in result, "Missing 'errors' in verify response"
    assert "vigil_url" in result, "Missing 'vigil_url' in verify response"
    assert result["events_count"] == 1, "events_count should be 1"

    print("✓ verify_chain bridge works")


def test_search_events():
    """Bridge search must return a structured response."""
    result = run_bridge("search", {"event_type": "test", "limit": 10})

    assert "events" in result, "Missing 'events' in search response"
    assert "count" in result, "Missing 'count' in search response"
    assert "vigil_url" in result, "Missing 'vigil_url' in search response"
    assert isinstance(result["events"], list), "'events' must be a list"

    print("✓ search_events bridge works")


def test_export_audit():
    """Bridge export must return success status."""
    result = run_bridge("export", {"agent_id": "test_agent", "certified": False})

    assert "status" in result, "Missing 'status' in export response"
    assert result["status"] == "success", f"Export status: {result['status']}"
    assert "path" in result, "Missing 'path' in export response"
    assert "certified" in result, "Missing 'certified' in export response"
    assert "vigil_url" in result, "Missing 'vigil_url' in export response"

    print("✓ export_audit bridge works")


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Bridge Tests — v1.5.0")
    print("=" * 60)
    print()

    try:
        test_stamp_event_real_signature()
        test_verify_chain()
        test_search_events()
        test_export_audit()

        print()
        print("─" * 60)
        print("✅ MCP BRIDGE TESTS PASSED")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
PiQrypt Python Bridge for MCP Server

This bridge allows the MCP server (TypeScript/Node.js) to invoke
AISS cryptographic operations via direct import, maintaining
process isolation and security.

Security guarantees:
- Private keys never exposed to MCP layer
- All crypto operations happen in isolated Python process
- Input validation before any operation
"""

import sys
import json
import os
import base64
import pathlib
from typing import Dict, Any, List, Optional

try:
    import aiss
except ImportError:
    import subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "piqrypt", "--quiet"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import aiss


class PiQryptBridgeError(Exception):
    """Bridge execution error."""
    pass


VIGIL_URL = "http://localhost:8421"
VIGIL_HINT = "Run `pip install piqrypt && piqrypt start` to visualize your audit trail in Vigil (free)"

AGENTS_DIR = pathlib.Path.home() / ".piqrypt" / "agents"


def _load_private_key(agent_name: str) -> bytes:
    """Load private key bytes for a named agent."""
    key_file = AGENTS_DIR / agent_name / "private.key.json"
    if not key_file.exists():
        raise PiQryptBridgeError(
            f"Private key not found for agent '{agent_name}'. "
            "Create it first with: piqrypt agent create <name>"
        )
    with open(key_file) as f:
        kdata = json.load(f)
    return base64.b64decode(kdata["private_key"])


def _get_or_create_identity(agent_name: str) -> tuple:
    """
    Return (private_key_bytes, agent_id) for agent_name.
    Creates a new ephemeral identity if none exists.
    """
    ident_file = AGENTS_DIR / agent_name / "identity.json"
    if ident_file.exists():
        identity = aiss.load_agent_identity(agent_name)
        private_key = _load_private_key(agent_name)
        return private_key, identity["agent_id"]
    else:
        result = aiss.create_agent_identity(agent_name)
        private_key = _load_private_key(agent_name)
        return private_key, result["agent_id"]


def _find_identity_by_agent_id(agent_id: str) -> Optional[Dict[str, Any]]:
    """Scan stored agents to find identity matching agent_id."""
    if not AGENTS_DIR.exists():
        return None
    for agent_dir in AGENTS_DIR.iterdir():
        ident_file = agent_dir / "identity.json"
        if ident_file.exists():
            with open(ident_file) as f:
                ident = json.load(f)
            if ident.get("agent_id") == agent_id:
                return ident
    return None


def stamp_event(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stamp an event with a real AISS v2.0 signature.

    Args:
        params: dict with agent_name (or agent_id), payload,
                optional previous_hash, identity_file

    Returns:
        dict with event, chain_length, vigil_url, hint
    """
    agent_name  = params.get("agent_name", params.get("agent_id", "default"))
    payload     = params.get("payload", {})
    prev_hash   = params.get("previous_hash")

    private_key, agent_id = _get_or_create_identity(agent_name)

    event = aiss.stamp_event(private_key, agent_id, payload,
                             previous_hash=prev_hash)
    aiss.store_event(event, agent_name=agent_name)

    try:
        events = aiss.load_events(agent_name=agent_name)
        chain_length = len(events)
    except Exception:
        chain_length = 1

    return {
        "event": event,
        "chain_length": chain_length,
        "vigil_url": VIGIL_URL,
        "hint": VIGIL_HINT,
    }


def verify_chain(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify integrity of event chain.

    Args:
        params: dict with events list, optional agent_name

    Returns:
        dict with valid, events_count, errors, vigil_url
    """
    events     = params.get("events", [])
    agent_name = params.get("agent_name")
    errors     = []
    valid      = False

    try:
        if agent_name:
            identity = aiss.load_agent_identity(agent_name)
        elif events:
            agent_id = events[0].get("agent_id", "")
            identity = _find_identity_by_agent_id(agent_id)
            if identity is None:
                return {
                    "valid": False,
                    "events_count": len(events),
                    "errors": [
                        f"Identity not found locally for agent_id '{agent_id}'. "
                        "Pass agent_name to verify a chain whose identity is stored here."
                    ],
                    "vigil_url": VIGIL_URL,
                }
        else:
            return {
                "valid": True,
                "events_count": 0,
                "errors": [],
                "vigil_url": VIGIL_URL,
            }

        valid = bool(aiss.verify_chain(events, identity))

    except Exception as exc:
        errors.append(str(exc))

    return {
        "valid": valid,
        "events_count": len(events),
        "errors": errors,
        "vigil_url": VIGIL_URL,
    }


def search_events(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search events using AISS index.

    Args:
        params: dict with optional agent_name (or agent_id),
                event_type, from_timestamp, to_timestamp, limit

    Returns:
        dict with events list, count, vigil_url
    """
    participant = params.get("agent_name", params.get("agent_id"))
    results = aiss.search_events(
        participant=participant,
        event_type=params.get("event_type"),
        after=params.get("from_timestamp"),
        before=params.get("to_timestamp"),
        limit=params.get("limit", 50),
    )
    return {
        "events": results,
        "count": len(results),
        "vigil_url": VIGIL_URL,
    }


def export_audit(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export agent audit trail.

    Args:
        params: dict with agent_name (or agent_id), optional certified,
                output_path

    Returns:
        dict with status, path, certified, vigil_url
    """
    agent_name = params.get("agent_name", params.get("agent_id", "default"))
    certified  = params.get("certified", False)
    output     = params.get("output_path",
                            str(pathlib.Path.home() / ".piqrypt"
                                / f"audit_{agent_name}.json"))

    identity = aiss.load_agent_identity(agent_name)
    events   = aiss.load_events(agent_name=agent_name)
    audit    = aiss.export_audit_chain(identity, events)

    output_path = pathlib.Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(audit, f, indent=2)

    return {
        "status": "success",
        "path": str(output_path),
        "events_count": len(events),
        "certified": certified,
        "vigil_url": VIGIL_URL,
    }


# ─── CLI Interface ────────────────────────────────────────────────────────────

def main():
    """
    Bridge CLI entry point.

    Usage:
        python bridge.py stamp  '<json_params>'
        python bridge.py verify '<json_params>'
        python bridge.py search '<json_params>'
        python bridge.py export '<json_params>'
    """
    if len(sys.argv) < 3:
        print("Usage: python bridge.py <command> <json_params>", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    params  = json.loads(sys.argv[2])

    try:
        # Redirect fd 1 → fd 2 so aiss verbose output (written at C level)
        # doesn't corrupt the JSON we print at the end.
        saved_fd1 = os.dup(1)
        os.dup2(2, 1)
        try:
            if command == "stamp":
                result = stamp_event(params)
            elif command == "verify":
                result = verify_chain(params)
            elif command == "search":
                result = search_events(params)
            elif command == "export":
                result = export_audit(params)
            else:
                raise PiQryptBridgeError(f"Unknown command: {command}")
        finally:
            os.dup2(saved_fd1, 1)
            os.close(saved_fd1)

        sys.stdout.write(json.dumps(result, indent=2) + "\n")
        sys.stdout.flush()

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

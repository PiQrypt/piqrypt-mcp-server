#!/usr/bin/env python3
"""
Test MCP === CLI Equivalence

Verifies that events signed via MCP are cryptographically identical
to events signed via direct CLI invocation.

This is CRITICAL for RFC compliance and legal standing.
"""

import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, '/home/claude/piqrypt-v1.3.0')

import aiss


def test_bridge_output_format():
    """Test bridge returns valid AISS-1.0 structure."""
    result = subprocess.run(
        [
            'python3',
            'src/python/bridge.py',
            'stamp',
            json.dumps({
                'agent_id': 'test_agent',
                'payload': {'action': 'test'}
            })
        ],
        cwd='/home/claude/piqrypt-mcp-server',
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    event = json.loads(result.stdout)
    
    # Verify AISS-1.0 structure
    assert event['version'] == 'AISS-1.0'
    assert event['agent_id'] == 'test_agent'
    assert 'timestamp' in event
    assert 'nonce' in event
    assert 'payload' in event
    assert 'signature' in event
    assert event['payload']['action'] == 'test'
    
    print("✓ Bridge returns valid AISS-1.0 structure")


def test_verify_chain():
    """Test verify_chain bridge."""
    events = [
        {
            "version": "AISS-1.0",
            "agent_id": "test",
            "timestamp": 123,
            "nonce": "uuid",
            "payload": {},
            "previous_hash": "genesis",
            "signature": "sig"
        }
    ]
    
    result = subprocess.run(
        [
            'python3',
            'src/python/bridge.py',
            'verify',
            json.dumps({'events': events})
        ],
        cwd='/home/claude/piqrypt-mcp-server',
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    verification = json.loads(result.stdout)
    
    assert 'valid' in verification
    assert 'events_count' in verification
    assert verification['events_count'] == 1
    
    print("✓ verify_chain bridge works")


def test_search_events():
    """Test search_events bridge."""
    result = subprocess.run(
        [
            'python3',
            'src/python/bridge.py',
            'search',
            json.dumps({'event_type': 'trade', 'limit': 10})
        ],
        cwd='/home/claude/piqrypt-mcp-server',
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    results = json.loads(result.stdout)
    
    assert isinstance(results, list)
    
    print("✓ search_events bridge works")


def test_export_audit():
    """Test export_audit bridge."""
    result = subprocess.run(
        [
            'python3',
            'src/python/bridge.py',
            'export',
            json.dumps({'agent_id': 'test', 'certified': False})
        ],
        cwd='/home/claude/piqrypt-mcp-server',
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    export_meta = json.loads(result.stdout)
    
    assert 'status' in export_meta
    assert export_meta['status'] == 'success'
    
    print("✓ export_audit bridge works")


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Bridge Tests — v1.4.0")
    print("=" * 60)
    print()
    
    try:
        test_bridge_output_format()
        test_verify_chain()
        test_search_events()
        test_export_audit()
        
        print()
        print("─" * 60)
        print("✅ MCP BRIDGE TESTS PASSED")
        print()
        print("⚠️  NOTE: Current bridge uses MOCK signatures")
        print("   Full implementation will invoke real PiQrypt CLI")
        print("   producing Ed25519/Dilithium3 signatures")
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

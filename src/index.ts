#!/usr/bin/env node
/**
 * PiQrypt MCP Server
 * 
 * Provides Model Context Protocol access to PiQrypt cryptographic audit trail.
 * 
 * Security model:
 * - All cryptographic operations delegated to Python CLI
 * - No private keys accessed by this server
 * - Process isolation via subprocess
 * 
 * Usage:
 *   node dist/index.js
 * 
 * MCP Client configuration:
 *   {
 *     "mcpServers": {
 *       "piqrypt": {
 *         "command": "node",
 *         "args": ["/path/to/piqrypt-mcp-server/dist/index.js"]
 *       }
 *     }
 *   }
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to Python bridge
const PYTHON_BRIDGE = join(__dirname, '../src/python/bridge.py');

/**
 * Execute Python bridge command
 */
function callPythonBridge(command: string, params: any): any {
  try {
    const paramsJson = JSON.stringify(params);
    const result = execSync(
      `python3 ${PYTHON_BRIDGE} ${command} '${paramsJson}'`,
      { encoding: 'utf-8', timeout: 30000 }
    );
    return JSON.parse(result);
  } catch (error: any) {
    throw new Error(`PiQrypt bridge error: ${error.message}`);
  }
}

/**
 * Tool definitions
 */
const tools: Tool[] = [
  {
    name: 'piqrypt_stamp_event',
    description: 'Create a tamper-proof cryptographic record of an agent decision. Signs the event with Ed25519, links it to the previous event in a hash chain (AISS v2.0). Call this after every significant agent action. Required for GDPR Art.22, EU AI Act Art.13, HIPAA audit trail, SEC/FINRA trading compliance.',
    inputSchema: {
      type: 'object',
      properties: {
        agent_id: {
          type: 'string',
          description: 'Agent identifier (e.g., "trading_bot_v1", "hr_decision_engine")',
        },
        payload: {
          type: 'object',
          description: 'Event payload containing decision data (JSON object)',
        },
        previous_hash: {
          type: 'string',
          description: 'Optional hash of previous event for chain integrity',
        },
      },
      required: ['agent_id', 'payload'],
    },
  },
  {
    name: 'piqrypt_verify_chain',
    description: 'Verify that an agent\'s decision history is intact and untampered. Detects modified events, missing events, hash chain breaks, and forks. Call before trusting any historical agent output.',
    inputSchema: {
      type: 'object',
      properties: {
        events: {
          type: 'array',
          description: 'Array of PiQrypt events to verify',
          items: { type: 'object' },
        },
      },
      required: ['events'],
    },
  },
  {
    name: 'piqrypt_export_audit',
    description: 'Export the complete agent audit trail to a portable JSON archive. Set certified=true to request a PiQrypt CA signature for legal admissibility (eIDAS Art.26). The export is self-contained and verifiable without PiQrypt installed.',
    inputSchema: {
      type: 'object',
      properties: {
        agent_id: {
          type: 'string',
          description: 'Agent ID to export',
        },
        certified: {
          type: 'boolean',
          description: 'Create certified export (requires Pro license)',
          default: false,
        },
        output_format: {
          type: 'string',
          enum: ['json', 'pqz'],
          description: 'Output format (json or encrypted pqz archive)',
          default: 'json',
        },
      },
      required: ['agent_id'],
    },
  },
  {
    name: 'piqrypt_search_events',
    description: 'Search the agent\'s cryptographic event history by type, time range, or session. Returns signed events with chain metadata. Use to reconstruct what an agent did during a specific period.',
    inputSchema: {
      type: 'object',
      properties: {
        event_type: {
          type: 'string',
          description: 'Filter by event type (e.g., "trade_executed", "decision_made")',
        },
        from_timestamp: {
          type: 'number',
          description: 'Start timestamp (Unix UTC seconds)',
        },
        to_timestamp: {
          type: 'number',
          description: 'End timestamp (Unix UTC seconds)',
        },
        limit: {
          type: 'number',
          description: 'Maximum number of results',
          default: 100,
        },
      },
    },
  },
];

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'piqrypt-mcp-server',
    version: '1.5.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: any;

    switch (name) {
      case 'piqrypt_stamp_event':
        result = callPythonBridge('stamp', {
          agent_id: args.agent_id,
          payload: args.payload,
          previous_hash: args.previous_hash,
        });
        break;

      case 'piqrypt_verify_chain':
        result = callPythonBridge('verify', {
          events: args.events,
        });
        break;

      case 'piqrypt_export_audit':
        result = callPythonBridge('export', {
          agent_id: args.agent_id,
          certified: args.certified || false,
          output_format: args.output_format || 'json',
        });
        break;

      case 'piqrypt_search_events':
        result = callPythonBridge('search', {
          event_type: args.event_type,
          from_timestamp: args.from_timestamp,
          to_timestamp: args.to_timestamp,
          limit: args.limit || 100,
        });
        break;

      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error: any) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Start server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('PiQrypt MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});

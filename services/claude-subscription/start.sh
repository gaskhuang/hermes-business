#!/bin/bash
cd "/Users/gask/Documents/claude-code/hermes-business/services/claude-subscription"
source .venv/bin/activate
exec python3 claude_oauth_server.py

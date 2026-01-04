#!/bin/bash
echo "Cleaning up previous network state..."
rm -f network.db

echo "Starting OpenAgents Network..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi
openagents network start network.yaml

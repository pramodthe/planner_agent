#!/bin/bash
echo "Cleaning up previous network state..."
rm -f network.db

echo "Starting OpenAgents Network..."
openagents network start network.yaml

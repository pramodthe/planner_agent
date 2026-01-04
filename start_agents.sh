#!/bin/bash

# Function to start agent in new terminal tab (macOS)
start_agent() {
    title="$1"
    cmd="$2"
    # Get absolute path to current directory
    cwd="$(pwd)"
    
    # Check for virtual environment and activate it
    if [ -f ".venv/bin/activate" ]; then
        # We use a single string for activation to keep it simple in the AppleScript
        activation="source .venv/bin/activate"
    else
        activation="echo 'No .venv found'"
    fi

    # Load .env file if it exists
    if [ -f ".env" ]; then
        activation="$activation && export \$(grep -v '^#' .env | xargs)"
    fi
    
    # Add current directory to PYTHONPATH so tools module can be imported
    activation="$activation && export PYTHONPATH=\$PYTHONPATH:$(pwd)"
    
    # Simple and robust AppleScript command
    # We use separate -e flags to avoid complex quoting issues with multiple commands
    osascript -e "tell application \"Terminal\" to activate" -e "tell application \"Terminal\" to do script \"cd '$cwd' && $activation && echo 'Starting $title...' && $cmd\""
}

echo "Starting agents in separate terminals..."

start_agent "Travel Coordinator" "openagents agent start agents/travel_coordinator.yaml"
start_agent "Flight Agent" "openagents agent start agents/flight_agent.yaml"
start_agent "Hotel Agent" "openagents agent start agents/hotel_agent.yaml"
start_agent "Travel Planner" "openagents agent start agents/travel_planner.yaml"

echo "All agents launched!"

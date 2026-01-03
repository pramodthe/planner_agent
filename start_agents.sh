#!/bin/bash

# Function to start agent in new terminal tab (macOS)
start_agent() {
    title="$1"
    cmd="$2"
    # Check for virtual environment and activate it
    if [ -f ".venv/bin/activate" ]; then
        activation="source .venv/bin/activate"
    else
        activation="echo 'No .venv found'"
    fi
    
    osascript -e "tell application \"Terminal\" to do script \"cd $(pwd); $activation; echo 'Starting $title...'; $cmd\""
}

echo "Starting agents in separate terminals..."

start_agent "Travel Coordinator" "openagents agent start agents/travel_coordinator.yaml"
start_agent "Flight Agent" "openagents agent start agents/flight_agent.yaml"
start_agent "Hotel Agent" "openagents agent start agents/hotel_agent.yaml"
start_agent "Travel Planner" "openagents agent start agents/travel_planner.yaml"

echo "All agents launched!"

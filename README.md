# Travel Planning Team

A multi-agent system built with [OpenAgents](https://openagents.org) to orchestrate travel planning. This system coordinates flights, hotels, and itineraries to create a complete trip brief for the user.

## Architecture

The project is structured as a centralized agent network (`network.yaml`) managing a team of specialized agents.

### Core Components

*   **Network**: A centralized gRPC/HTTP server that manages agent discovery, message routing, and shared state.
*   **Agents**:
    *   **Travel Coordinator (`travel-coordinator`)**: The main interface for the user. It clarifies requirements, delegates tasks to other agents, and compiles the final proposal.
    *   **Flight Agent (`flight-agent`)**: Specializes in finding flights. Uses `SerpApi` (Google Flights) to fetch real-time flight data.
    *   **Hotel Agent (`hotel-agent`)**: Specializes in finding accommodation. Uses `SerpApi` (Google Hotels) to fetch real-time hotel data.
    *   **Travel Planner (`travel-planner`)**: Uses an LLM to generate a day-by-day itinerary based on the destination and user preferences.

### Directory Structure

```text
planner_agent/
├── agents/                 # Agent configuration definitions (YAML)
│   ├── travel_coordinator.yaml
│   ├── flight_agent.yaml
│   ├── hotel_agent.yaml
│   └── travel_planner.yaml
├── tools/                  # Python implementations of agent tools
│   ├── flight_search.py    # SerpApi integration for flights
│   └── hotel_search.py     # SerpApi integration for hotels
├── mods/                   # OpenAgents workspace modules (persistence, messaging)
├── network.yaml            # Main network configuration
└── start_system.sh         # Startup script
```

## Prerequisites

*   **Python 3.10+**
*   **OpenAgents**: Installed via `pip install openagents`
*   **API Keys**:
    *   `OPENAI_API_KEY`: For the LLM agents (GPT-4o/mini).
    *   `SERPAPI_API_KEY`: For real-time flight and hotel data.

## Setup

1.  **Environment Variables**:
    Create a `.env` file in the root directory (copy from `.env.example` if available) and add your keys:
    ```bash
    OPENAI_API_KEY=sk-...
    SERPAPI_API_KEY=...
    ```

2.  **Install Dependencies**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install openagents google-search-results
    ```

## Usage

1.  **Start the System**:
    Run the startup script to launch the network and all agents:
    ```bash
    ./start_system.sh
    ```

2.  **Connect**:
    *   The OpenAgents Studio is served at `http://localhost:8700`.
    *   Open your browser and navigate to the Studio.
    *   **Login**: Use the password `travel123` to connect to the network.

3.  **Interact**:
    *   Start a new chat with the **Travel Planning Team**.
    *   Example prompt: *"Plan a 5-day trip to Tokyo for 2 people in March. Budget is flexible."*

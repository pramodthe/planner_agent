# Travel Planning Agent System

A comprehensive, multi-agent AI system for end-to-end travel planning powered by OpenAgents. This system coordinates specialized agents to search flights, book hotels, research destinations, and create detailed travel itineraries.

## 🎯 Project Overview

The Travel Planning Agent System is a distributed network of AI agents that work together to provide complete travel packages. Users submit travel requests through a project interface, and the system intelligently delegates tasks to specialized agents that handle different aspects of trip planning.

### Key Features

- **Multi-Agent Architecture**: Four specialized agents working in coordination
  - Travel Coordinator: Orchestrates requests and compiles final packages
  - Flight Agent: Searches flights via Kiwi MCP Server
  - Hotel Agent: Searches accommodations via Apify Booking.com Scraper
  - Travel Planner: Creates itineraries and researches destinations

- **Real Data Integration**: 
  - Kiwi.com flight search (public service, no API key required)
  - Apify Booking.com scraper (optional with API token)
  - Wikivoyage destination research

- **Fallback System**: Works with realistic mock data when APIs unavailable

- **Budget Flexibility**: Provides budget, mid-range, and luxury options for all searchess

- **Enterprise-Grade Network**: Uses OpenAgents with HTTP/gRPC transport, agent groups, and role-based permissions

## 🏗️ System Architecture

### Agent Network Structure

```
┌─────────────────────────────────────────────────────────┐
│             Travel Planning Network                      │
│          (Network ID: TravelPlanningTeam)               │
└─────────────────────────────────────────────────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
        ┌───────▼──┐  ┌────▼─────┐  ┌─▼──────────┐
        │  Flight  │  │  Hotel   │  │  Travel    │
        │  Agent   │  │  Agent   │  │  Planner   │
        └───────┬──┘  └────┬─────┘  └─┬──────────┘
                │          │          │
                └──────────┼──────────┘
                           │
                    ┌──────▼──────┐
                    │ Coordinator │
                    │   Agent     │
                    └─────────────┘
```

### Network Configuration

- **Mode**: Centralized (single control node)
- **Transport**: HTTP (port 8700) + gRPC (port 8600)
- **Node ID**: travel-team-1
- **Max Connections**: 50
- **Agent Timeout**: 180 seconds
- **Message Queue Size**: 1000

## 📋 Agent Specifications

### 1. Travel Coordinator (`agents/travel_coordinator.yaml`)

**Type**: CollaboratorAgent  
**Agent ID**: travel-coordinator  
**Group**: coordinators (password: coordinator_secret)  
**Model**: gpt-5-mini

**Responsibilities**:
- Receives travel requests from users
- Extracts destination, dates, budget, and preferences
- Delegates specialized tasks to flight, hotel, and planner agents
- Tracks agent responses using project state
- Compiles final travel package with all results
- Sends comprehensive summary to user

**Key Tools**:
- `send_project_message()`: Communicate with users
- `send_event()`: Delegate tasks to specialist agents
- `set_project_global_state()`: Store agent responses
- `get_project_global_state()`: Retrieve stored data
- `complete_project()`: Finish projects with summary

**Workflow**:
1. Receives `project.notification.started` event
2. Extracts travel details from project goal
3. Initializes response tracking in project state
4. Sends flight search to flight-agent
5. Sends hotel search to hotel-agent
6. Sends itinerary creation to travel-planner
7. Collects all responses via `task.complete` events
8. Compiles and sends final package when all agents complete

### 2. Flight Agent (`agents/flight_agent.yaml`)

**Type**: CollaboratorAgent  
**Agent ID**: flight-agent  
**Group**: booking_agents (password: booking_secret)  
**Model**: gpt-5-mini

**Responsibilities**:
- Searches flights via Kiwi MCP Server
- Categorizes results into budget and luxury options
- Provides booking links for each flight option
- Returns formatted results to coordinator

**MCP Integration**:
- **MCP Server**: kiwi-com-flight-search
- **URL**: https://mcp.kiwi.com
- **Public Service**: No API key required

**Input Parameters**:
- origin: Departure location (e.g., "London")
- destination: Arrival location
- departure_date: YYYY-MM-DD format
- return_date: YYYY-MM-DD format
- travelers: Number of passengers (integer)
- budget_preference: "budget" or "luxury"

**Output Format**:
```json
{
  "task_id": "flight_search",
  "status": "success",
  "budget_options": [
    {
      "airline": "string",
      "price": "number",
      "departure": "string",
      "arrival": "string",
      "booking_link": "string"
    }
  ],
  "premium_options": []
}
```

### 3. Hotel Agent (`agents/hotel_agent.yaml`)

**Type**: CollaboratorAgent  
**Agent ID**: hotel-agent  
**Group**: booking_agents (password: booking_secret)  
**Model**: gpt-5-mini

**Responsibilities**:
- Searches hotels via Apify Booking.com Scraper
- Filters results by budget preference
- Provides hotel details and Booking.com direct links
- Falls back to mock data if Apify unavailable

**Custom Tools**:
- `search_hotels_apify()`: [tools/hotel_search.py](tools/hotel_search.py)

**Apify Integration**:
- **Actor**: voyager/booking-scraper
- **Platform**: Apify MCP Server
- **API Token**: Optional (APIFY_TOKEN environment variable)
- **Fallback**: Realistic mock Booking.com data

**Input Parameters**:
- destination: City or location
- checkin_date: YYYY-MM-DD format
- checkout_date: YYYY-MM-DD format
- travelers: Number of guests (integer)
- budget_preference: "budget", "mid-range", or "luxury"

**Output Format**:
```json
{
  "task_id": "hotel_search",
  "status": "success",
  "budget_hotels": [
    {
      "name": "string",
      "price_per_night": "number",
      "rating": "number",
      "location": "string",
      "booking_url": "string"
    }
  ],
  "mid_range_hotels": [],
  "luxury_hotels": []
}
```

### 4. Travel Planner (`agents/travel_planner.yaml`)

**Type**: CollaboratorAgent  
**Agent ID**: travel-planner  
**Group**: planners (password: planner_secret)  
**Model**: gpt-5-mini

**Responsibilities**:
- Researches destinations using Wikivoyage API
- Creates day-by-day itineraries
- Calculates detailed budget breakdowns
- Provides travel tips and recommendations

**Custom Tools**:
- `research_destination()`: Wikivoyage API integration - [tools/travel_planning.py](tools/travel_planning.py)
- `create_itinerary()`: Generates day-by-day schedules
- `calculate_budget()`: Breakdown of costs by category

**Input Parameters**:
- destination: City or country
- duration: Trip length in days
- budget: "budget" or "luxury"
- preferences: Travel interests
- travelers: Number of people

**Output Format**:
```json
{
  "task_id": "itinerary_plan",
  "status": "success",
  "destination_info": "string",
  "budget_itinerary": {
    "days": {
      "day_1": {
        "date": "string",
        "morning_activity": "string",
        "afternoon_activity": "string",
        "evening_activity": "string",
        "estimated_daily_cost": "number"
      }
    }
  },
  "luxury_itinerary": {},
  "budget_breakdown": {
    "accommodation": "number",
    "food": "number",
    "activities": "number",
    "transport": "number",
    "miscellaneous": "number"
  }
}
```

## 🛠️ Tools & Implementations

### Hotel Search Tools (`tools/hotel_search.py`)

- **`get_hotel_search_request()`**: Generates Apify MCP request parameters
  - Parses check-in/check-out dates
  - Calculates number of nights
  - Returns formatted actor input for Booking.com scraper

- **`search_hotels_apify()`**: Main search function (decorated with `@tool`)
  - Requires APIFY_TOKEN environment variable
  - Executes voyager/booking-scraper actor
  - Processes results from Booking.com dataset
  - Returns top 10 hotels formatted with details and booking URLs

### Travel Planning Tools (`tools/travel_planning.py`)

- **`research_destination()`**: Researches using Wikivoyage API
  - Searches Wikivoyage for destination
  - Retrieves destination overview/introduction
  - Respects user interests
  - Returns destination info with source attribution

- **`create_itinerary()`**: Generates day-by-day schedules
  - Creates activities for each day based on budget
  - Calculates daily costs
  - Supports budget vs luxury activity differentiation
  - Returns structured itinerary for up to 7 days

- **`calculate_budget()`**: Detailed cost breakdown
  - Budget Style: ~$60/day per person
    - Accommodation: $25
    - Food: $15
    - Activities: $10
    - Transport: $5
    - Miscellaneous: $5
  
  - Luxury Style: ~$1,150/day per person
    - Accommodation: $400
    - Food: $200
    - Activities: $300
    - Transport: $100
    - Miscellaneous: $150

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAgents framework (v0.6.13+)
- Virtual environment (recommended)
- API tokens (optional):
  - APIFY_TOKEN for real Booking.com data
  - OpenAI API key for LLM (GPT-5-mini)

### Installation

1. **Clone/Setup Repository**
   ```bash
   cd /Users/pramodthebe/Desktop/planner_agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # - APIFY_TOKEN (optional, for real hotel data)
   # - DEFAULT_LLM_API_KEY (OpenAI API key)
   ```

5. **Verify Tool Imports**
   ```bash
   python debug_import.py
   python debug_import_tool.py
   ```

### Starting the System

#### Option 1: Full System Start (Recommended)

```bash
# Terminal 1: Start the network
./start_system.sh

# Terminal 2: Start all agents
./start_agents.sh
```

The `start_system.sh` script:
- Cleans up previous database state
- Starts OpenAgents network with `network.yaml` configuration
- Initializes HTTP (port 8700) and gRPC (port 8600) transports
- Enables Studio web interface at http://localhost:8700

The `start_agents.sh` script (macOS):
- Activates virtual environment
- Launches each agent in separate terminal tab:
  - Travel Coordinator
  - Flight Agent
  - Hotel Agent
  - Travel Planner

#### Option 2: Manual Agent Start

```bash
# Terminal 1
openagents network start network.yaml

# Terminal 2
openagents agent start agents/travel_coordinator.yaml

# Terminal 3
openagents agent start agents/flight_agent.yaml

# Terminal 4
openagents agent start agents/hotel_agent.yaml

# Terminal 5
openagents agent start agents/travel_planner.yaml
```

## 📡 Network Configuration Details

### Network File (`network.yaml`)

**Key Settings**:
- **Mode**: Centralized with single node (travel-team-1)
- **HTTP Transport**: Port 8700 with Studio enabled
- **gRPC Transport**: Port 8600 with compression
- **Discovery**: Enabled, 10-second intervals
- **Agent Timeout**: 180 seconds for long-running tasks
- **Message Queue**: 1000 size, 45-second timeout

**Agent Groups** (Role-Based Access):
1. **admin**: Full permissions
   - Password Hash: adde73956e80fa10e12dbd4783f889c1b051a815454f9f0a5b9ef9ab3a977f01
   - Password: admin_secret

2. **coordinators**: Create projects, delegate tasks, compile packages
   - Password Hash: 64a68968a063885dd11b169ae2d73007bd570a913599a4f785e35a9e1d421ce7
   - Password: coordinator_secret

3. **booking_agents**: Search flights/hotels, access booking APIs
   - Password Hash: 3152a8444abddcea4d9915269a4a0e38c5cf1b38148f36e43bd1445cce73fe5f
   - Password: booking_secret

4. **planners**: Create itineraries, research destinations, calculate budgets
   - Password Hash: 33fbb0d9147fe907594e4d6ed6473508789f24f67a1d39b099882ed04473902c
   - Password: planner_secret

**Project Templates**:
1. **budget_travel**: Focuses on cheapest options
   - Economy flights, budget hotels (<$50/night)
   - Free activities, public transport
   - <$30/day food budget

2. **luxury_travel**: Focuses on premium options
   - Business/First class flights
   - 5-star hotels ($300+/night)
   - Fine dining, private tours
   - $1000+/day budget

**Enabled Mods**:
- `openagents.mods.workspace.default`: Core messaging and events
- `openagents.mods.workspace.project`: Project management
- Custom events enabled for agent communication

**Studio & Relay**:
- OpenAgents Studio enabled at http://localhost:8700
- Relay publishing enabled
- Public subdomain: travel-agents-live.relay.openagents.com

## 🔄 Agent Communication Flow

### Example: User Submits Travel Request

```
1. User creates project in Studio with goal:
   "Plan a 5-day luxury trip to Paris for 2 people, departing March 15"

2. Coordinator receives "project.notification.started" event
   ├─ Extracts: destination="Paris", dates, budget="luxury", travelers=2
   ├─ Initializes tracking: agents_expected=3, agents_responded=0
   └─ Sends message: "Starting your travel planning..."

3. Coordinator delegates tasks via send_event():
   ├─ Flight Agent: "search.flights" 
   │  Input: origin, destination, dates, budget_preference
   ├─ Hotel Agent: "search.hotels"
   │  Input: destination, checkin, checkout, budget_preference
   └─ Travel Planner: "create.itinerary"
      Input: destination, duration, budget, preferences

4. Agents execute in parallel:
   ├─ Flight Agent calls Kiwi MCP → Returns flight options with links
   ├─ Hotel Agent calls Apify MCP → Returns hotel options with links
   └─ Travel Planner researches destination → Returns itinerary + budget

5. Each agent sends "task.complete" event back to Coordinator
   ├─ Event 1 received: agents_responded=1
   ├─ Event 2 received: agents_responded=2
   └─ Event 3 received: agents_responded=3

6. Coordinator compiles final package:
   ├─ Combines all agent results
   ├─ Formats comprehensive travel package
   ├─ Sends to user: flights, hotels, itinerary, budget breakdown
   └─ Completes project
```

## 📁 Project Structure

```
planner_agent/
├── agents/                           # Agent configuration files
│   ├── flight_agent.yaml            # Kiwi flight search agent
│   ├── hotel_agent.yaml             # Apify hotel search agent
│   ├── travel_coordinator.yaml       # Main orchestrator agent
│   └── travel_planner.yaml          # Itinerary & research agent
│
├── tools/                            # Custom tool implementations
│   ├── __init__.py                  # Package init
│   ├── hotel_search.py              # Apify hotel search tools
│   ├── travel_planning.py           # Destination research & itinerary tools
│   └── __pycache__/                 # Python cache
│
├── config/                           # Configuration files
│   └── agent_env/
│       └── _global.json             # Global agent environment variables
│
├── logs/                             # Agent execution logs
│   ├── agents/                      # Agent-specific logs
│   └── llm/                         # LLM call logs (JSONL)
│       ├── flight-agent.jsonl
│       ├── hotel-agent.jsonl
│       └── travel-coordinator.jsonl
│
├── mods/                             # OpenAgents mods
│   └── openagents.mods.workspace.default/
│
├── network.yaml                     # Network configuration
├── main.py                          # Example main agent (template)
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .env                             # Environment variables (local)
├── .gitignore                       # Git ignore rules
├── start_system.sh                  # Start network script
├── start_agents.sh                  # Start agents script
├── debug_import.py                  # Tool import debugging
└── debug_import_tool.py             # Decorator import debugging
```

## ⚙️ Configuration Files

### `.env` - Environment Variables

```bash
# API Keys
APIFY_TOKEN=your_token_here          # Optional: Real Booking.com data
DEFAULT_LLM_API_KEY=sk-proj-...      # OpenAI API key

# Network
TRAVEL_NETWORK_HOST=localhost
TRAVEL_NETWORK_HTTP_PORT=8700
TRAVEL_NETWORK_GRPC_PORT=8600

# Model
DEFAULT_MODEL=gpt-5-mini
MAX_ITERATIONS=8

# Fallback
USE_MOCK_DATA_FALLBACK=true          # Works without APIs
```

### `config/agent_env/_global.json` - Global Agent Config

Sets global environment variables for all agents:
- LLM Provider: OpenAI
- LLM Model: gpt-5-mini
- LLM API Key: (from environment)

### `requirements.txt` - Dependencies

```
openagents>=0.1.0           # Multi-agent framework
requests>=2.31.0            # HTTP requests for APIs
apify-client>=1.7.0         # Apify SDK for Booking scraper
duckduckgo-search>=3.9.0    # Web search capability
types-requests>=2.31.0      # Type hints
```

## 🔍 Debugging

### Import Issues

```bash
# Debug tool decorator imports
python debug_import_tool.py

# Debug module imports
python debug_import.py
```

### Common Issues

**Issue**: Agents can't connect to network
- **Solution**: Verify network is running on localhost:8600 (gRPC) or localhost:8700 (HTTP)
- **Check**: `openagents network start network.yaml` completed successfully

**Issue**: Apify tool not working
- **Solution**: APIFY_TOKEN not set or apify-client not installed
- **Check**: `pip install apify-client` and set APIFY_TOKEN in .env
- **Fallback**: System uses realistic mock data automatically

**Issue**: Kiwi flight search returns errors
- **Solution**: Kiwi MCP server is public and doesn't require authentication
- **Check**: Network connectivity and MCP server configuration in flight_agent.yaml

**Issue**: Tools not found in agents
- **Solution**: Ensure tools are properly imported and @tool decorator is used
- **Check**: Run `python debug_import.py` to verify imports

## 📊 Monitoring & Logs

### Log Locations

- **Agent Logs**: `logs/agents/`
- **LLM Logs**: `logs/llm/*.jsonl` (JSON Lines format)
  - flight-agent.jsonl
  - hotel-agent.jsonl
  - travel-coordinator.jsonl
  - travel-planner.jsonl

### Viewing Logs

```bash
# Real-time monitoring
tail -f logs/agents/*.log

# LLM call history
cat logs/llm/flight-agent.jsonl | jq .

# Network health
openagents network status
```

## 🔐 Security Notes

- Agent group passwords are SHA-256 hashed
- Encryption currently disabled (set `encryption_enabled: false`)
- Network requires agent group authentication
- API tokens should be stored in `.env` (not in version control)

## 🌐 Network Diagram

```
┌─────────────────────────────────────────────────┐
│      OpenAgents Studio (localhost:8700)         │
│      Web UI for project creation & monitoring   │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────▼─────────┐
         │   Network Node    │
         │ (travel-team-1)   │
         │                   │
         │  HTTP: 8700       │
         │  gRPC: 8600       │
         └────────┬──────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
    ┌───▼──┐  ┌──▼───┐  ┌──▼────┐
    │Flight│  │Hotel │  │Travel  │
    │Agent │  │Agent │  │Planner │
    └───┬──┘  └──┬───┘  └──┬─────┘
        │        │         │
        └────────┼─────────┘
                 │
            ┌────▼────┐
            │Coordinator
            └──────────┘
```

## 📈 Performance Characteristics

- **Request Timeout**: 45 seconds for message processing
- **Agent Timeout**: 180 seconds for long operations
- **Max Agents**: 50 concurrent connections
- **Message Queue**: 1000 messages (FIFO)
- **Discovery**: 10-second intervals
- **Heartbeat**: 60-second intervals

## 🤝 Contributing

To extend the system:

1. **Add New Tool**: Create function in `tools/` with `@tool` decorator
2. **Add New Agent**: Create YAML config in `agents/` with triggers
3. **Update Network**: Modify `network.yaml` with new agent groups
4. **Test Locally**: Use `debug_import.py` to verify imports

## 📝 Example Usage

### Starting a Travel Planning Session

1. **Start System**
   ```bash
   ./start_system.sh
   ./start_agents.sh
   ```

2. **Access Studio**
   - Open http://localhost:8700 in browser

3. **Create Project**
   - Select "Create Project"
   - Choose template: "Budget Travel" or "Luxury Travel"
   - Enter goal: "Plan 5-day trip to Tokyo for 3 people, March 15-20, $2000 budget"

4. **Monitor Progress**
   - Coordinator receives request
   - Agents search flights/hotels in parallel
   - Travel planner creates itinerary
   - Final package compiled and delivered

5. **Review Results**
   - Complete flight options with Kiwi.com links
   - Hotel options with Booking.com links
   - Day-by-day itinerary
   - Budget breakdown

## 📚 API References

- **OpenAgents**: https://github.com/openagents-dev/openagents
- **Kiwi.com Flight API**: https://mcp.kiwi.com
- **Apify**: https://apify.com
- **Wikivoyage API**: https://en.wikivoyage.org/w/api.php

## 📄 License

Specify your license here.

## 👤 Author

Pramod Thebe  
Location: /Users/pramodthebe/Desktop/planner_agent

## 🆘 Support

For issues:
1. Check logs in `logs/` directory
2. Run debug scripts: `python debug_import.py`
3. Verify network: `openagents network status`
4. Check agent connectivity: Verify gRPC port 8600 is accessible

---

**Last Updated**: Based on workspace state  
**OpenAgents Version**: 0.8.5  
**Network Profile**: Travel Planning Team
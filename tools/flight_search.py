"""
Flight Search Tools using SerpApi (Google Flights)
"""

import logging
import os
from typing import Dict, List, Optional

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# Configure logging
logger = logging.getLogger(__name__)

def search_flights_serpapi(origin: str, destination: str, departure_date: str, 
                          return_date: str = None, travelers: int = 1, 
                          budget_preference: str = "mid-range") -> Dict:
    """
    Search flights using SerpApi (Google Flights).
    
    Args:
        origin: Origin airport code or city (e.g., "JFK", "New York")
        destination: Destination airport code or city (e.g., "LHR", "London")
        departure_date: Date (YYYY-MM-DD)
        return_date: Date (YYYY-MM-DD), optional
        travelers: Number of travelers
        budget_preference: budget/luxury/best_value
        
    Returns:
        Dictionary with flight options
    """
    
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        return {"status": "error", "message": "SERPAPI_KEY not found."}
        
    if not GoogleSearch:
         return {"status": "error", "message": "google-search-results not installed."}
    
    logger.info(f"Searching flights {origin} -> {destination} on {departure_date}...")

    # Basic params
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": departure_date,
        "adults": travelers,
        "currency": "USD",
        "hl": "en",
        "api_key": api_key
    }
    
    if return_date:
        params["return_date"] = return_date
        
    # Budget preference mapping to sort (Note: Google Flights engine params vary, 
    # usually 'sort_by' is price (1), duration (2), etc. 
    # SerpApi google_flights support 'sort_by': 1 (Price), 2 (Duration), 3 (Departure time), 4 (Arrival time)
    if budget_preference == "budget":
        params["sort_by"] = 1 # Price

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return {"status": "error", "message": results["error"]}

        # Parse flights
        # SerpApi Google Flights structure: 'best_flights', 'other_flights'
        
        flight_options = []
        
        # Combine best and other for processing
        all_raw_flights = results.get("best_flights", []) + results.get("other_flights", [])
        
        for flight in all_raw_flights:
            # Extract basic info
            # Format varies. Usually 'flights_cluster' or individual segments.
            # SerpApi simplified structure usually:
            # { "flights": [...segments...], "total_duration": 450, "price": 120, "airline_logo": ... }
            
            flight_flights = flight.get("flights", [])
            if not flight_flights:
                continue
                
            first_leg = flight_flights[0]
            airline = first_leg.get("airline", "Unknown Airline")
            flight_number = first_leg.get("flight_number", "")
            
            price = flight.get("price", "N/A")
            duration = flight.get("total_duration", 0) # minutes
            
            flight_options.append({
                "airline": airline,
                "flight_number": flight_number,
                "price_total": price,
                "duration_mins": duration,
                "depart_time": first_leg.get("departure_airport", {}).get("time", ""),
                "arrive_time": flight_flights[-1].get("arrival_airport", {}).get("time", ""),
                "stops": len(flight_flights) - 1,
                "booking_link": results.get("search_metadata", {}).get("google_flights_url", "https://www.google.com/travel/flights"),
                "source": "SerpApi"
            })
            
        return {
            "status": "success",
            "source": "SerpApi Google Flights",
            "options": flight_options[:10], # Top 10
            "metadata": {
                "count": len(flight_options)
            }
        }

    except Exception as e:
        logger.error(f"Flight search failed: {e}")
        return {"status": "error", "message": str(e)}

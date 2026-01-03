"""
Travel Planning Tools
Provides destination research, itinerary creation, and comprehensive budget calculation.
Uses real data where available, falls back to realistic templates for any destination.
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

from openagents.workspace.tool_decorator import tool


import requests

# Wikivoyage API endpoint
WIKIVOYAGE_API = "https://en.wikivoyage.org/w/api.php"


@tool
def research_destination(destination: str, duration: int = 7, 
                        interests: List[str] = None) -> Dict:
    """Research destination information using Wikivoyage API."""
    if interests is None:
        interests = ["culture", "food", "sightseeing"]
    
    try:
        # 1. Search for the destination page
        params = {
            "action": "query",
            "list": "search",
            "srsearch": destination,
            "format": "json"
        }
        search_resp = requests.get(WIKIVOYAGE_API, params=params).json()
        
        page_id = None
        if search_resp.get("query", {}).get("search"):
            page_id = search_resp["query"]["search"][0]["pageid"]
            
        if not page_id:
             return {
                "destination": destination,
                "overview": "Could not find destination on Wikivoyage.",
                "interests": interests
            }

        # 2. Get extract/intro
        extract_params = {
            "action": "query",
            "prop": "extracts",
            "pageids": page_id,
            "exintro": 1,
            "explaintext": 1,
            "format": "json"
        }
        extract_resp = requests.get(WIKIVOYAGE_API, params=extract_params).json()
        extract = extract_resp["query"]["pages"][str(page_id)].get("extract", "No overview available.")

        return {
            "destination": destination,
            "overview": extract[:1000] + "..." if len(extract) > 1000 else extract, # Truncate if too long
            "source": "Wikivoyage",
            "duration": duration,
            "interests": interests
        }
        
    except Exception as e:
        logger.error(f"Wikivoyage API error: {e}")
        return {
            "destination": destination,
            "error": "Failed to fetch destination data",
            "overview": "Research failed due to API error."
        }



@tool
def create_itinerary(destination: str, duration: int, budget: str, travelers: int) -> Dict:
    """Create day-by-day travel itinerary."""
    
    budget_activities = ["Free walking tours", "Museums", "Markets", "Parks", "Street food"]
    luxury_activities = ["Private tours", "Fine dining", "Spa treatments", "Luxury shopping", "Private transport"]
    
    activities = luxury_activities if budget == "luxury" else budget_activities
    
    itinerary = {
        "destination": destination,
        "duration": duration,
        "budget": budget,
        "travelers": travelers,
        "days": {}
    }
    
    for day in range(1, min(duration + 1, 8)):
        activity = activities[(day - 1) % len(activities)]
        daily_cost = 60 if budget == "luxury" else 10
        
        itinerary["days"][f"day_{day}"] = {
            "date": (datetime.now() + timedelta(days=day-1)).strftime("%B %d"),
            "morning_activity": activity,
            "afternoon_activity": activity,
            "evening_activity": activity,
            "estimated_daily_cost": daily_cost
        }
    
    return itinerary


@tool
def calculate_budget(destination: str, duration: int, travelers: int, style: str) -> Dict:
    """Calculate detailed travel budget breakdown."""
    
    if style == "budget":
        daily_costs = {
            "accommodation": 25,
            "food": 15,
            "activities": 10,
            "transport": 5,
            "miscellaneous": 5
        }
    else:  # luxury
        daily_costs = {
            "accommodation": 400,
            "food": 200,
            "activities": 300,
            "transport": 100,
            "miscellaneous": 150
        }
    
    total_per_day = sum(daily_costs.values())
    total_per_person = total_per_day * duration
    total_for_group = total_per_person * travelers
    
    return {
        "destination": destination,
        "style": style,
        "travelers": travelers,
        "duration": duration,
        "daily_breakdown": daily_costs,
        "totals": {
            "per_person_per_day": total_per_day,
            "per_person_total": total_per_person,
            "total_for_group": total_for_group
        }
    }

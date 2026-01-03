"""
Hotel Search Tools using Apify MCP Server and mock fallback
Provides hotel search and booking capabilities via Apify platform.

This module is designed to work with the Apify MCP server configured in agents.
When MCP server is available, uses real Booking.com data via Apify.
Falls back to realistic mock data when unavailable.

MCP Configuration:
- Server: apify (configured with uvx apify-mcp-server)
- Tools: run_actor, get_run_results
- Actor: voyager/booking-scraper for hotel searches

Usage by MCP-enabled agents:
1. Call get_hotel_search_request() to get parameters
2. Agent executes MCP call: run_actor with voyager/booking-scraper
3. Agent processes real Booking.com data and returns formatted results
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
from openagents.workspace.tool_decorator import tool

try:
    from apify_client import ApifyClient
except ImportError:
    ApifyClient = None

# Configure logging
logger = logging.getLogger(__name__)


def get_hotel_search_request(destination: str, checkin_date: str, checkout_date: str, 
                            travelers: int = 2, budget_preference: str = "mid-range") -> Dict:
    """
    Generate hotel search request parameters for Apify MCP server.
    
    Args:
        destination: Destination city or location
        checkin_date: Check-in date (YYYY-MM-DD)
        checkout_date: Check-out date (YYYY-MM-DD)
        travelers: Number of travelers
        budget_preference: Budget preference (budget/mid-range/luxury)
    
    Returns:
        Dictionary with MCP request parameters for Apify Booking.com scraper
    """
    
    # Parse dates to calculate night count
    try:
        checkin = datetime.strptime(checkin_date, "%Y-%m-%d")
        checkout = datetime.strptime(checkout_date, "%Y-%m-%d")
        nights = (checkout - checkin).days
    except:
        nights = 3  # Default
    
    # Return request parameters for Apify MCP
    return {
        "actor_id": "voyager/booking-scraper",
        "input": {
            "search": destination,
            "checkIn": checkin_date,
            "checkOut": checkout_date,
            "rooms": (travelers + 1) // 2,  # Assume 2 per room
            "adults": travelers,
            "children": 0,
            "currency": "USD",
            "language": "en-gb",
            "sortBy": "price" if budget_preference == "budget" else "review_score_and_price",
            "maxPages": 1  # Limit for faster response
        },
        "metadata": {
            "destination": destination,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "nights": nights,
            "travelers": travelers,
            "budget_preference": budget_preference
        }
    }


@tool
def search_hotels_apify(destination: str, checkin_date: str, checkout_date: str, 
                       travelers: int = 2, budget_preference: str = "mid-range") -> Dict:
    """
    Search hotels using Apify Booking.com scraper.
    Unlikely deprecated mock version, this uses REAL data.
    
    Args:
        destination: Destination city or location
        checkin_date: Check-in date (YYYY-MM-DD)
        checkout_date: Check-out date (YYYY-MM-DD)
        travelers: Number of travelers
        budget_preference: Budget preference (budget/mid-range/luxury)
    
    Returns:
        Dictionary with hotel search results
    """
    
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        logger.error("APIFY_TOKEN not found in environment variables.")
        return {
            "status": "error",
            "message": "APIFY_TOKEN not provided. Cannot fetch real hotel data."
        }
        
    if not ApifyClient:
         logger.error("apify_client not installed.")
         return {
            "status": "error",
            "message": "apify-client library not installed."
        }
    
    client = ApifyClient(token)
    
    # Get request parameters
    request_params = get_hotel_search_request(destination, checkin_date, checkout_date, 
                                             travelers, budget_preference)
    
    logger.info(f"Hotel search request for {destination}: {request_params}")
    
    try:
        # Execute the actor
        run_input = request_params["input"]
        logger.info(f"Starting Apify actor execution for {destination}...")
        run = client.actor("voyager/booking-scraper").call(run_input=run_input)
        
        logger.info(f"Actor finished. Fetching results from dataset {run['defaultDatasetId']}...")
        # Get results
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        
        # Process items
        hotels = []
        for item in dataset_items:
            # Basic field extraction - robust to missing keys
            hotels.append({
                "name": item.get("name", "Unknown Hotel"),
                "price_per_night": item.get("price", "N/A"),
                "rating": item.get("rating", "N/A"),
                "location": item.get("address", "Unknown Location"),
                "amenities": [], # Booking scraper might not return amenities in simple list
                "booking_url": item.get("url", "https://booking.com")
            })
            
        # Filter/Bucket results (simple version)
        return {
            "status": "success",
            "source": "Apify Booking.com Scraper",
            "hotels": hotels[:10], # Return top 10
            "metadata": request_params["metadata"]
        }
        
    except Exception as e:
        logger.error(f"Apify execution failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch hotel data: {str(e)}"
        }


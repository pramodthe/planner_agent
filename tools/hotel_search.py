"""
Hotel Search Tools using SerpApi (Google Hotel Search)
Provides hotel search and booking capabilities via Google Hotels.

This module is designed to work with the SerpApi service.
Usage:
1. Agent calls search_hotels_serpapi()
2. Function queries SerpApi google_hotels engine
3. Returns normalized hotel data
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# Configure logging
logger = logging.getLogger(__name__)

def search_hotels_serpapi(destination: str, checkin_date: str, checkout_date: str, 
                         travelers: int = 2, budget_preference: str = "mid-range") -> Dict:
    """
    Search hotels using SerpApi (Google Hotel Search).
    
    Args:
        destination: Destination city or location
        checkin_date: Check-in date (YYYY-MM-DD)
        checkout_date: Check-out date (YYYY-MM-DD)
        travelers: Number of travelers
        budget_preference: Budget preference (budget/mid-range/luxury)
    
    Returns:
        Dictionary with hotel search results
    """
    
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        logger.error("SERPAPI_KEY not found in environment variables.")
        return {
            "status": "error",
            "message": "SERPAPI_KEY not provided. Cannot fetch hotel data."
        }
        
    if not GoogleSearch:
         logger.error("google-search-results not installed.")
         return {
            "status": "error",
            "message": "google-search-results library not installed."
        }
    
    logger.info(f"Searching hotels in {destination} via SerpApi...")
    
    # Map budget preference to sort order
    sort_by = 8 # Default: Best Choice
    if budget_preference == "budget":
        sort_by = 2 # Lowest price
    elif budget_preference == "luxury":
        sort_by = 3 # Highest rating (proxy for luxury)

    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": checkin_date,
        "check_out_date": checkout_date,
        "adults": travelers,
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "sort_by": sort_by,
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return {"status": "error", "message": results["error"]}

        hotel_results = results.get("properties", [])
        
        # Process items
        hotels = []
        for item in hotel_results:
            # Extract price safely
            price_val = "N/A"
            if item.get("rate_per_night") and item.get("rate_per_night").get("lowest"):
                 price_val = item.get("rate_per_night").get("lowest")
            
            hotels.append({
                "name": item.get("name", "Unknown Hotel"),
                "price_per_night": price_val,
                "total_price": item.get("total_rate", {}).get("lowest", "N/A"),
                "rating": item.get("overall_rating", "N/A"),
                "location": item.get("description", "Unknown Location"), # SerpApi puts location/desc here often
                "amenities": item.get("amenities", []),
                "booking_url": item.get("link", "https://www.google.com/travel/hotels")
            })
            
        # Return top 10
        return {
            "status": "success",
            "source": "SerpApi Google Hotels",
            "hotels": hotels[:10],
            "metadata": {
                "destination": destination,
                "checkin_date": checkin_date,
                "checkout_date": checkout_date,
                "count": len(hotels)
            }
        }
        
    except Exception as e:
        logger.error(f"SerpApi execution failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch hotel data: {str(e)}"
        }

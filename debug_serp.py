
import os
import logging
from tools.hotel_search import search_hotels_serpapi

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load env vars manually for the test script if needed, 
# but we assume the user runs this with `export $(grep -v '^#' .env | xargs)` or similar,
# or we can read .env here.
from dotenv import load_dotenv
load_dotenv()

print(f"SERPAPI_KEY present: {bool(os.environ.get('SERPAPI_KEY'))}")

try:
    print("Testing search_hotels_serpapi...")
    result = search_hotels_serpapi(
        destination="Tokyo",
        checkin_date="2026-03-15",
        checkout_date="2026-03-20",
        travelers=2,
        budget_preference="mid-range"
    )
    print("Result keys:", result.keys())
    if result.get("status") == "success":
        print(f"Found {len(result.get('hotels', []))} hotels.")
        if result.get('hotels'):
            print("First hotel:", result['hotels'][0])
    else:
        print("Search failed:", result)

except Exception as e:
    print(f"TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

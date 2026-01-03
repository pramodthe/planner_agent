import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")
print(f"Sys Path includes CWD: {os.getcwd() in sys.path}")

try:
    print("Attempting to import tools.travel_planning...")
    import tools.travel_planning
    print("Successfully imported tools.travel_planning")
except ImportError as e:
    print(f"Caught ImportError: {e}")
except ModuleNotFoundError as e:
    print(f"Caught ModuleNotFoundError: {e}")
except Exception as e:
    print(f"Caught Exception: {e}")

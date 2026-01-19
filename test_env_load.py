import os
from dotenv import load_dotenv
import asyncio

# Load the env first to make sure it's available (though agent.py also loads it now)
load_dotenv()

# Check if the var is in os.environ
print(f"COIN_API_URL in env: {os.getenv('COIN_API_URL')}")

# Import agent to trigger its load_dotenv and see if it breaks anything
try:
    from agent import get_crypto_data
    print("Imported get_crypto_data successfully.")
    
    # We can try to inspect the closure or just run it if we can
    # get_crypto_data is likely a Tool object now.
    # If the library `agents` makes the original function accessible, we can try.
    # But strictly speaking, we just want to know if the logic inside *will* work.
    
    # Let's try to run the tool function directly.
    # The @function_tool decorator turns it into a Tool instance usually, 
    # but often the tool instance is callable or has a 'run' method.
    # Alternatively, the original function might be available as `__wrapped__` or similar.
    
    # However, simply importing agent.py runs the code we modified (module level imports).
    # The function body runs when called.
    
    print("Test script finished.")

except Exception as e:
    print(f"Error importing agent: {e}")

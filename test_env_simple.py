import os
from dotenv import load_dotenv
import sys

# Load the env
load_dotenv()

# Check if the var is in os.environ
val = os.getenv('COIN_API_URL')
print(f"COIN_API_URL in env: {val}")
if val:
    print("SUCCESS: Environment variable found.")
else:
    print("FAILURE: Environment variable NOT found.")

sys.stdout.flush()

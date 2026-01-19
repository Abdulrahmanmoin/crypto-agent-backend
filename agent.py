import httpx
from typing import Optional
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
from agents import Agent, function_tool, ModelSettings
from guardrails import user_intent_guardrail

@function_tool
async def get_crypto_data(coin_ids: Optional[str] = None):
    """
    Fetches real-time price, market cap, and metadata for crypto coins from CoinGecko.
    
    Args:
        coin_ids (str, optional): Comma-separated list of coin IDs (e.g., 'bitcoin,ethereum'). 
                                  If not provided, returns top 10 coins.
    """
    KB_FILE = "KB.json"
    kb_path = os.path.join(os.path.dirname(__file__), KB_FILE)
    
    # Determine cache key
    if coin_ids:
        # Normalize: strip spaces and lowercase
        clean_ids = [c.strip().lower() for c in coin_ids.split(",") if c.strip()]
        cache_key = ",".join(clean_ids)
    else:
        cache_key = "top_10_coins"

    print(f"--- Fetching data for: {cache_key} ---")

    # Check Cache
    if os.path.exists(kb_path):
        try:
            with open(kb_path, "r") as f:
                kb_data = json.load(f)
            
            if cache_key in kb_data:
                entry = kb_data[cache_key]
                saved_time_str = entry.get("timestamp")
                if saved_time_str:
                    saved_time = datetime.fromisoformat(saved_time_str)
                    # Check if data is fresh (less than 2 hours old)
                    if datetime.now() - saved_time < timedelta(hours=2):
                        print(f"--- Returning cached data from {KB_FILE} (saved at {saved_time_str}) ---")
                        return entry["data"]
        except Exception as e:
            print(f"Warning: Error reading cache file: {e}")

    # If not in cache or stale, fetch from API
    url = os.getenv("COIN_API_URL")
    print("URL: ", url)
    if not url:
        return {"error": "Configuration Error: COIN_API_URL is missing in environment variables."}
    
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }
    
    if coin_ids:
        params["ids"] = cache_key
        print("params: ", params)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            print("data: ", data)

            # Format results for the agent
            formatted_data = []
            for coin in data:
                formatted_data.append({
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol", "").upper(),
                    "price": f"${coin.get('current_price'):,.2f}",
                    "market_cap": f"${coin.get('market_cap'):,.0f}",
                    "24h_change": f"{coin.get('price_change_percentage_24h', 0):.2f}%",
                    "id": coin.get("id")
                })
            
            # Save to Cache
            try:
                current_kb = {}
                if os.path.exists(kb_path):
                    with open(kb_path, "r") as f:
                        try:
                            current_kb = json.load(f)
                        except json.JSONDecodeError:
                            current_kb = {} # Start fresh if corrupt
                
                current_kb[cache_key] = {
                    "timestamp": datetime.now().isoformat(),
                    "data": formatted_data
                }

                with open(kb_path, "w") as f:
                    json.dump(current_kb, f, indent=4)
                print(f"--- Data saved to {KB_FILE} ---")

            except Exception as e:
                print(f"Warning: Error writing to cache file: {e}")

            return formatted_data
        except httpx.HTTPStatusError as e:
            return {"error": f"API Error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

# Define the Crypto Expert Agent


# Define the Crypto Expert Agent Factory
def create_crypto_agent():
    return Agent(
        name="CryptoExpert",
        instructions=(
            "You are a professional Cryptocurrency Expert. Your expertise covers: "
            "current prices, market capitalization, and coin metadata (names, symbols, etc.). "
            "Use the provided tool to get up-to-date information.\n\n"
            "STRICT POLICY - DO NOT PROVIDE:\n"
            "1. Price predictions or future price analysis.\n"
            "2. Investment or financial advice.\n"
            "3. Answers to hypothetical 'what if' scenarios regarding prices.\n\n"
            "If a user asks about predictions, advice, or hypotheticals, tell them: "
            "'I am an expert in current market data and metadata only. I cannot provide predictions, "
            "investment advice, or answer hypothetical questions.'"
        ),
        tools=[get_crypto_data],
        input_guardrails=[user_intent_guardrail],
        model_settings=ModelSettings(tool_choice="required")
    )

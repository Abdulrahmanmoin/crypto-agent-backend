import httpx
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
from agents import Agent, function_tool, ModelSettings
from guardrails import user_intent_guardrail
from kb_utils import load_kb_data, get_cached_coins, save_coins_to_kb

@function_tool
async def get_crypto_data(coin_ids: Optional[str] = None):
    """
    Fetches real-time price, market cap, and metadata for crypto coins from CoinGecko.
    
    Args:
        coin_ids (str, optional): Comma-separated list of coin IDs (e.g., 'bitcoin,ethereum'). 
                                  If not provided, returns top 10 coins.
    """
    # Normalize coin IDs
    if coin_ids:
        requested_ids = [c.strip().lower() for c in coin_ids.split(",") if c.strip()]
    else:
        requested_ids = None  # Will fetch top 10

    print(f"--- Fetching data for: {requested_ids or 'top 10 coins'} ---")

    # Load existing KB data
    kb_data = load_kb_data()

    # Check cache for each requested coin
    cached_results = []
    ids_to_fetch = []

    if requested_ids:
        cached_results, ids_to_fetch = get_cached_coins(requested_ids, kb_data)
    else:
        # For top 10, always fetch fresh data (can't reliably cache "top 10")
        ids_to_fetch = None

    # If all coins are cached, return cached results
    if requested_ids and not ids_to_fetch:
        print(f"--- All data retrieved from cache ---")
        return cached_results

    # Fetch from API for coins not in cache or stale
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
    
    if ids_to_fetch:
        params["ids"] = ",".join(ids_to_fetch)
        print("params: ", params)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            print("data: ", data)

            # Format and save coins to KB
            fetched_results = save_coins_to_kb(data, kb_data)

            # Combine cached and fetched results
            all_results = cached_results + fetched_results
            return all_results

        except httpx.HTTPStatusError as e:
            return {"error": f"API Error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

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

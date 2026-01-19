import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

# KB Configuration
KB_FILE = "KB.json"
CACHE_DURATION_HOURS = 2


def get_kb_path() -> str:
    """Returns the absolute path to the KB.json file."""
    return os.path.join(os.path.dirname(__file__), KB_FILE)


def load_kb_data() -> Dict[str, Any]:
    """
    Loads and returns the KB data from the JSON file.
    Returns an empty dict if file doesn't exist or is corrupted.
    """
    kb_path = get_kb_path()
    
    if os.path.exists(kb_path):
        try:
            with open(kb_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Error reading cache file: {e}")
    
    return {}


def save_kb_data(kb_data: Dict[str, Any]) -> bool:
    """
    Saves the KB data to the JSON file.
    Returns True if successful, False otherwise.
    """
    kb_path = get_kb_path()
    
    try:
        with open(kb_path, "w") as f:
            json.dump(kb_data, f, indent=4)
        print(f"--- Data saved to {KB_FILE} ---")
        return True
    except Exception as e:
        print(f"Warning: Error writing to cache file: {e}")
        return False


def is_cache_fresh(price_timestamp_str: str) -> bool:
    """
    Checks if a cached entry is still fresh (less than CACHE_DURATION_HOURS old).
    
    Args:
        price_timestamp_str: ISO format timestamp string (e.g., "2026-01-06T10:15:00Z")
    
    Returns:
        True if cache is fresh, False if stale or invalid
    """
    if not price_timestamp_str:
        return False
    
    try:
        saved_time = datetime.fromisoformat(price_timestamp_str.replace("Z", "+00:00"))
        current_time = datetime.now()
        
        # Make current_time offset-aware for comparison if needed
        if saved_time.tzinfo:
            time_diff = datetime.now(saved_time.tzinfo) - saved_time
        else:
            time_diff = current_time - saved_time
        
        return time_diff < timedelta(hours=CACHE_DURATION_HOURS)
    except Exception as e:
        print(f"Warning: Error parsing timestamp: {e}")
        return False


def get_cached_coins(coin_ids: List[str], kb_data: Dict[str, Any]) -> Tuple[List[Dict], List[str]]:
    """
    Checks the cache for requested coins and returns cached results and IDs to fetch.
    
    Args:
        coin_ids: List of coin IDs to check
        kb_data: The loaded KB data dictionary
    
    Returns:
        Tuple of (cached_results, ids_to_fetch)
    """
    cached_results = []
    ids_to_fetch = []
    
    for coin_id in coin_ids:
        if coin_id in kb_data:
            coin_entry = kb_data[coin_id]
            price_timestamp_str = coin_entry.get("price_timestamp")
            
            if is_cache_fresh(price_timestamp_str):
                print(f"--- Using cached data for {coin_id} (saved at {price_timestamp_str}) ---")
                cached_results.append(coin_entry)
                continue
        
        ids_to_fetch.append(coin_id)
    
    return cached_results, ids_to_fetch


def format_coin_entry(coin: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats a coin from API response to KB entry format.
    
    Args:
        coin: Raw coin data from CoinGecko API
    
    Returns:
        Formatted coin entry for KB storage
    """
    price_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    return {
        "coin": coin.get("name"),
        "symbol": coin.get("symbol", "").upper(),
        "last_price": coin.get("current_price"),
        "price_timestamp": price_timestamp,
        "id": coin.get("id")
    }


def save_coins_to_kb(coins: List[Dict[str, Any]], kb_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Formats and saves coins to KB, then persists to file.
    
    Args:
        coins: List of raw coin data from API
        kb_data: Existing KB data dictionary (will be modified)
    
    Returns:
        List of formatted coin entries
    """
    formatted_coins = []
    
    for coin in coins:
        coin_entry = format_coin_entry(coin)
        formatted_coins.append(coin_entry)
        
        # Save each coin to KB with its coin id as the key
        kb_data[coin.get("id")] = coin_entry
    
    # Persist to file
    save_kb_data(kb_data)
    
    return formatted_coins

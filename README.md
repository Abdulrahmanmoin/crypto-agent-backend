# Crypto Expert Agent

An AI agent built with the OpenAI Agent SDK that provides real-time cryptocurrency market data using the CoinGecko API.

## Features
- **Real-time Data**: Fetches prices, market cap, and 24h changes.
- **Strict Guidelines**: Expert in market data, but strictly refuses to provide investment advice or price predictions.
- **Tool Integration**: Uses a custom tool to fetch data from `api.coingecko.com`.

## Requirements
- Python 3.11+
- OpenAI API Key
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

1. **Clone the repository** (if you haven't already).
2. **Install dependencies**:
   ```bash
   pip install -r pyproject.toml
   # or using uv
   uv sync
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

Run the agent script:
```bash
python main.py | uv run main.py | uvicorn main:app --reload --port 8000
```

## How it Works
The agent is defined in `main.py` using the `openai-agents` SDK. It has access to the `get_crypto_data` function, which queries the CoinGecko `/coins/markets` endpoint. The agent's instructions ensure it maintains a professional tone and adheres to the safety boundaries regarding financial advice.

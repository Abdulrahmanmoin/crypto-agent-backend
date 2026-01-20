import asyncio
import os
from dotenv import load_dotenv
from typing import List
from summary_agent import update_summary

async def test_summarization():
    load_dotenv()
    print("Testing Summarizer Agent...")
    
    user_msg = "What is Bitcoin?"
    agent_msg = "Bitcoin is a decentralized digital currency."
    
    try:
        summary = await update_summary(None, user_msg, agent_msg)
        print("Summary Result:")
        print(summary)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_summarization())

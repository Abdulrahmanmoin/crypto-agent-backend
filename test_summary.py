import asyncio
import os
from dotenv import load_dotenv
from typing import List
from gemini_config import gemini_model

async def test_summarization():
    load_dotenv()
    print("Testing Generic Model Summarization...")
    
    history = [
        {"role": "user", "content": "What is Bitcoin?"},
        {"role": "assistant", "content": "Bitcoin is a decentralized digital currency."}
    ]
    
    prompt = (
        "You are a conversation summarizer. Update or create a concise summary of the "
        "conversation history between a user and a crypto expert agent.\n\n"
        "New messages to incorporate:\n"
        "user: What is Bitcoin?\nassistant: Bitcoin is a decentralized digital currency.\n\n"
        "Provide a single concise summary (under 3 sentences) that covers the main topics and coins discussed."
    )
    
    try:
        response = await gemini_model.openai_client.chat.completions.create(
            model=gemini_model.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        print("Summary Result:")
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_summarization())

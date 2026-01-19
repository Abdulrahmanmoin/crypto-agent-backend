from typing import List
from gemini_config import gemini_model

async def summarize_history(history: List[dict]) -> str:
    """
    Summarize the conversation history using the Gemini model.
    """
    if not history:
        return ""
    
    # Format history for summarization
    history_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in history])
    
    prompt = (
        "Summarize the following conversation history between a user and a crypto expert agent "
        "in a concise manner, focusing on the main topics and any specific coins mentioned. "
        "Keep the summary short (under 3 sentences).\n\n"
        f"{history_text}\n\n"
        "Summary:"
    )
    
    try:
        # Use the same gemini_model's client to generate summary
        response = await gemini_model.openai_client.chat.completions.create(
            model=gemini_model.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Previous conversation summary unavailable."

from typing import List
from gemini_config import gemini_model

async def summarize_history(history: List[dict], current_summary: str = None) -> str:
    """
    Summarize the conversation history using the Gemini model, incorporating any previous summary.
    """
    if not history and not current_summary:
        return ""
    
    # Format history for summarization
    history_text = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in history])
    
    summary_context = f"Previous summary: {current_summary}\n\n" if current_summary else ""
    
    prompt = (
        "You are a conversation summarizer. Update or create a concise summary of the "
        "conversation history between a user and a crypto expert agent.\n\n"
        f"{summary_context}"
        "New messages to incorporate:\n"
        f"{history_text}\n\n"
        "Provide a single concise summary (under 3 sentences) that covers the main topics and coins discussed."
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
        import traceback
        error_msg = f"Summarization Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        # Return the error message so we can see it in the frontend/logs clearly
        return error_msg

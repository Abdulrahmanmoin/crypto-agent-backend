from typing import List
from gemini_config import gemini_model
from agents import Agent, Runner, ModelSettings

# Define the Summarizer Agent
summarizer_agent = Agent(
    name="SummarizerAgent",
    model=gemini_model,
    instructions=(
        "You are a conversation summarizer. Update or create a concise summary of the "
        "conversation history between a user and a crypto expert agent.\n\n"
        "Provide a single concise summary (under 3 sentences) that covers the main topics and coins discussed."
    ),
    model_settings=ModelSettings(tool_choice="none")
)

async def update_summary(current_summary: str, user_message: str, agent_response: str) -> str:
    """
    Update the conversation summary with the latest exchange.
    """
    
    summary_context = f"Previous summary: {current_summary}\n\n" if current_summary else ""
    
    input_text = (
        f"{summary_context}"
        "New interaction to incorporate:\n"
        f"User: {user_message}\n"
        f"Agent: {agent_response}"
    )
    
    try:
        # Run the summarizer agent
        result = await Runner.run(summarizer_agent, input_text)
        return result.final_output.strip()
    except Exception as e:
        import traceback
        error_msg = f"Summarization Error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg

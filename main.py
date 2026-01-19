from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Runner, RunConfig, InputGuardrailTripwireTriggered
from gemini_config import gemini_model
from agent import create_crypto_agent
from summary_agent import summarize_history

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Crypto Agent API")

# Add CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    summary: Optional[str] = None

# Define response model
class ChatResponse(BaseModel):
    response: str
    summary: Optional[str] = None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to chat with the Crypto Expert Agent.
    """
    try:
        # Configure the run with Gemini
        run_config = RunConfig(
            model=gemini_model,
            tracing_disabled=True
        )
        
        # Instantiate the agent for this request
        crypto_agent = create_crypto_agent()
        
        # Prepare the input message with history/summary
        history = request.history
        current_message = request.message
        current_summary = request.summary
        
        # Determine context for the agent
        updated_summary = current_summary # Start with existing summary
        
        if len(history) == 1:
            # Only one message, no need for summary yet
            prev_msg = history[0]
            role = prev_msg.get('role', 'user')
            content = prev_msg.get('content', '')
            input_context = f"Previous conversation:\n{role}: {content}\n\nCurrent user query: {current_message}"
        elif current_summary or len(history) > 1:
            # Generate or update summary
            updated_summary = await summarize_history(history, current_summary)
            input_context = f"Summary of previous conversation:\n{updated_summary}\n\nCurrent user query: {current_message}"
        else:
            # No history
            input_context = current_message

        # Run the agent
        result = await Runner.run(crypto_agent, input_context, run_config=run_config)
        
        # If we didn't generate an updated summary yet (because history == 1), 
        # let's generate it now for the response if the history is growing
        if len(history) == 1:
             updated_summary = await summarize_history(history, current_summary)

        return ChatResponse(response=result.final_output, summary=updated_summary)
    
    except InputGuardrailTripwireTriggered as e:
        # Guardrail was triggered - return a friendly response
        guardrail_message = "I cannot provide predictions, investment advice, or answers to hypothetical questions. I can only help with current cryptocurrency market data and information."
        
        if e.guardrail_result and e.guardrail_result.output and e.guardrail_result.output.output_info:
            guardrail_message = str(e.guardrail_result.output.output_info)
        
        # Return existing summary so frontend keeps it
        return ChatResponse(response=guardrail_message, summary=request.summary)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Runner, RunConfig, InputGuardrailTripwireTriggered
from gemini_config import gemini_model
from agent import create_crypto_agent
from summary_agent import update_summary
import openai

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
        
        # Prepare the input message with summary
        current_message = request.message
        current_summary = request.summary
        
        # Determine context for the agent
        if current_summary:
            input_context = f"Summary of previous conversation:\n{current_summary}\n\nCurrent user query: {current_message}"
        else:
            input_context = current_message

        # Run the agent
        result = await Runner.run(crypto_agent, input_context, run_config=run_config)
        
        # Generate updated summary using the new exchange
        updated_summary = await update_summary(current_summary, current_message, result.final_output)

        return ChatResponse(response=result.final_output, summary=updated_summary)
    
    except InputGuardrailTripwireTriggered as e:
        # Guardrail was triggered - return a friendly response
        guardrail_message = "I cannot provide predictions, investment advice, or answers to hypothetical questions. I can only help with current cryptocurrency market data and information."
        
        if e.guardrail_result and e.guardrail_result.output and e.guardrail_result.output.output_info:
            guardrail_message = str(e.guardrail_result.output.output_info)
        
        # Return existing summary so frontend keeps it
        return ChatResponse(response=guardrail_message, summary=request.summary)
    
    except openai.RateLimitError as e:
        # Specifically handle rate limits and extract only the 'message' part for a cleaner UI
        error_detail = "API rate limit exceeded. Please wait a moment before trying again."
        
        try:
            # OpenAI/Gemini errors often have a body with the structured error
            if hasattr(e, "body") and isinstance(e.body, dict):
                error_obj = e.body.get("error", {})
                if isinstance(error_obj, dict):
                    error_detail = error_obj.get("message", error_detail)
            elif hasattr(e, "body") and isinstance(e.body, list) and len(e.body) > 0:
                # Handle the specific list structure seen in some Gemini responses
                first_item = e.body[0]
                if isinstance(first_item, dict) and "error" in first_item:
                    error_detail = first_item["error"].get("message", error_detail)
            else:
                # Fallback to the message attribute or string representation
                raw_msg = getattr(e, "message", str(e))
                # If it's the "Error code: 429 - [{...}]" format, try to strip the prefix
                if " - " in raw_msg:
                    error_detail = raw_msg.split(" - ", 1)[1]
                else:
                    error_detail = raw_msg
        except Exception:
            error_detail = str(e)

        raise HTTPException(status_code=429, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

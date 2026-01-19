from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Runner, RunConfig, InputGuardrailTripwireTriggered
from gemini_config import gemini_model
from agent import create_crypto_agent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Crypto Agent API")

# Define request model
class ChatRequest(BaseModel):
    message: str

# Define response model
class ChatResponse(BaseModel):
    response: str

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
        
        # Run the agent
        result = await Runner.run(crypto_agent, request.message, run_config=run_config)
        
        return ChatResponse(response=result.final_output)
    
    except InputGuardrailTripwireTriggered as e:
        # Guardrail was triggered - return a friendly response
        # Extract the output_info from the guardrail result if available
        guardrail_message = "I cannot provide predictions, investment advice, or answers to hypothetical questions. I can only help with current cryptocurrency market data and information."
        
        # Try to get the custom message from the guardrail
        if e.guardrail_result and e.guardrail_result.output and e.guardrail_result.output.output_info:
            guardrail_message = str(e.guardrail_result.output.output_info)
        
        return ChatResponse(response=guardrail_message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

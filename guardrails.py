from agents import Agent, ModelSettings, input_guardrail, GuardrailFunctionOutput, Runner
from gemini_config import gemini_model

# Define the Safety Agent
safety_agent = Agent(
    name="SafetyClassifier",
    model=gemini_model,
    instructions=(
        "You are a strict content safety classifier for a Crypto Agent.\n"
        "Analyze the User Query provided by the user.\n"
        "Does it ask for:\n"
        "1. Price predictions / future analysis?\n"
        "2. Investment / financial advice?\n"
        "3. Hypothetical 'what if' scenarios about prices?\n\n"
        "Reply with 'VIOLATION' if it matches any criteria. Reply 'SAFE' otherwise."
    ),
    model_settings=ModelSettings(tool_choice="none")
)

@input_guardrail
async def user_intent_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    """
    Guardrail to prevent the agent from answering price predictions,
    investment advice, or hypothetical questions.
    """
    # Extract the user message from input
    # Input can be a string or a list of message objects
    if isinstance(input, str):
        message = input
    elif isinstance(input, list) and len(input) > 0:
        # Get the last user message from the list
        last_msg = input[-1]
        if isinstance(last_msg, dict):
            message = last_msg.get("content", str(last_msg))
        else:
            message = str(last_msg)
    else:
        message = str(input)
    
    print(f"--- Guardrail checking: {message} ---")
    
    try:
        # Run the safety agent to classify the message
        result = await Runner.run(safety_agent, message)
        verdict = result.final_output.strip().upper()
        print(f"Guardrail Verdict: {verdict}")
        
        if "VIOLATION" in verdict:
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info="I cannot provide predictions, investment advice, or answers to hypothetical questions."
            )
            
    except Exception as e:
        print(f"Guardrail Check Failed: {e}")
        # If guardrail fails, we might choose to fail open or closed.
        # For now, let's allow it but log the error.

    return GuardrailFunctionOutput(tripwire_triggered=False, output_info="Query passed safety check.")

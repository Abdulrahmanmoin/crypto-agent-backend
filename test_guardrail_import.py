
try:
    from agents import input_guardrail, GuardrailFunctionOutput, AgentContext
    print("Import successful")
    print(f"input_guardrail: {input_guardrail}")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")

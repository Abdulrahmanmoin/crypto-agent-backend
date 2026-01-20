from gemini_config import gemini_model
print(f"Attributes of gemini_model: {dir(gemini_model)}")
try:
    print(f"openai_client: {gemini_model.openai_client}")
except AttributeError:
    print("openai_client attribute NOT found")

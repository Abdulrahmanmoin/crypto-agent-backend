try:
    import openai_agents
    print("Success: import openai_agents")
    print(f"Location: {openai_agents.__file__}")
except ImportError:
    print("Failed: import openai_agents")

try:
    import agents
    print("Success: import agents")
    print(f"Location: {agents.__file__}")
except ImportError:
    print("Failed: import agents")

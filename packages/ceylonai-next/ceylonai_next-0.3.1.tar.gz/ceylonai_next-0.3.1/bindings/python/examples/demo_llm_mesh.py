import asyncio
from ceylonai_next import LlmAgent, PyLocalMesh


async def main():
    print("Demo: LLM Agent with Mesh-Based Routing")
    print("=" * 60)
    print("\nThis demo shows two approaches:")
    print("1. Direct agent messaging - simple, straightforward")
    print("2. Mesh send_to() - for agent-to-agent communication")

    # Create LLM agent with custom actions
    print("\nCreating weather assistant agent...")
    weather_agent = LlmAgent("weather_agent", "ollama::gemma3:latest")
    weather_agent.with_system_prompt(
        "You are a helpful weather assistant. Use available tools to provide weather information."
    )

    # Define custom action for weather
    @weather_agent.action(description="Get the current weather for a location")
    def get_weather(location: str, unit: str = "celsius"):
        print(f"  [Action] Fetching weather for {location}...")
        if "london" in location.lower():
            return f"Weather in {location}: Rainy, 15 degrees {unit}"
        elif "paris" in location.lower():
            return f"Weather in {location}: Sunny, 22 degrees {unit}"
        elif "tokyo" in location.lower():
            return f"Weather in {location}: Cloudy, 18 degrees {unit}"
        else:
            return f"Weather in {location}: Partly cloudy, 20 degrees {unit}"

    # Build the LLM agent
    weather_agent.build()
    print("✓ Weather agent built")

    # Create mesh network
    mesh = PyLocalMesh("demo_mesh")
    print("✓ Created mesh network: demo_mesh\n")

    # For mesh-based routing, we would typically:
    # 1. Create a wrapper class implementing PyAgent interface
    # 2. Add agents to the mesh
    # 3. Use mesh.send_to(agent_name, message) for routing
    #
    # However, this demo focuses on the simpler direct approach
    # which is more suitable for single-agent scenarios.

    print("=" * 60)
    print("DIRECT AGENT MESSAGING")
    print("=" * 60)
    print("Using agent.send_message_async() directly\n")

    # Test 1: Direct call
    print("-" * 40)
    print("Test 1: Weather query for London")
    print("-" * 40)
    print("User: What's the weather in London?")
    response = await weather_agent.send_message_async("What's the weather in London?")
    print(f"Agent: {response}\n")

    await asyncio.sleep(1)

    # Test 2: Another query
    print("-" * 40)
    print("Test 2: Weather query for Paris")
    print("-" * 40)
    print("User: How about Paris?")
    response = await weather_agent.send_message_async("How about Paris?")
    print(f"Agent: {response}\n")

    await asyncio.sleep(1)

    # Test 3: Compare cities
    print("-" * 40)
    print("Test 3: Compare multiple cities")
    print("-" * 40)
    print("User: Compare weather in Tokyo and London")
    response = await weather_agent.send_message_async(
        "Compare the weather in Tokyo and London"
    )
    print(f"Agent: {response}\n")

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\n📚 Key Concepts:")
    print("  ✓ LlmAgent - High-level LLM interface with action decorators")
    print("  ✓ PyLocalMesh - Local mesh network (created but not actively used here)")
    print("  ✓ Direct messaging - agent.send_message_async()")
    print("  ✓ Custom actions - @agent.action() decorator")
    print("\n💡 Mesh Routing (mesh.send_to()):")
    print("  For true mesh-based routing where agents communicate via the mesh,")
    print("  you would wrap LlmAgent in a PyAgent-compatible wrapper class that")
    print("  implements the on_message() callback to handle mesh messages.")
    print("  This is useful for multi-agent coordinator patterns.")


if __name__ == "__main__":
    asyncio.run(main())

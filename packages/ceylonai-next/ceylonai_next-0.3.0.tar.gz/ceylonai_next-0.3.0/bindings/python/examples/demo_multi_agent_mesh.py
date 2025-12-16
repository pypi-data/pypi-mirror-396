"""
Demo: Multi-Agent Communication with LlmAgent

This demonstrates two LLM agents working together, but uses direct agent calls
rather than mesh routing since LlmAgent doesn't directly support mesh.send_to().

For true mesh routing with custom agents, see demo_agent_mesh_local.py
"""

import asyncio
from ceylonai_next import LlmAgent, PyLocalMesh


async def main():
    print("Demo: Multi-Agent LLM Communication")
    print("=" * 60)
    print("Two LLM agents working together\n")

    # Create mesh network (for demonstration)
    mesh = PyLocalMesh("multi_agent_mesh")
    print("✓ Created mesh network: multi_agent_mesh\n")

    # Agent 1: Weather Expert
    print("Creating Weather Expert Agent...")
    weather_agent = LlmAgent("weather_expert", "ollama::gemma3:latest")
    weather_agent.with_system_prompt(
        "You are a weather expert. Answer weather questions concisely. "
        "Keep responses to 2-3 sentences maximum."
    )
    weather_agent.with_temperature(0.4)
    weather_agent.with_max_tokens(150)

    # Add weather action
    @weather_agent.action(description="Get weather for a location")
    def get_weather(location: str):
        print(f"  [Weather Expert] Fetching weather for {location}...")
        weather_data = {
            "london": "Rainy, 15°C",
            "paris": "Sunny, 22°C",
            "tokyo": "Cloudy, 18°C",
            "new york": "Snowy, -2°C",
        }
        return weather_data.get(location.lower(), "Unknown location, 20°C")

    weather_agent.build()
    print("  ✓ Weather Expert ready")

    # Agent 2: Travel Advisor
    print("Creating Travel Advisor Agent...")
    travel_agent = LlmAgent("travel_advisor", "ollama::gemma3:latest")
    travel_agent.with_system_prompt(
        "You are a travel advisor. Give brief travel recommendations. "
        "Keep responses to 2-3 sentences. Be enthusiastic and helpful."
    )
    travel_agent.with_temperature(0.7)
    travel_agent.with_max_tokens(150)

    # Add recommendation action
    @travel_agent.action(description="Get travel recommendation")
    def travel_recommendation(weather_info: str):
        print(f"  [Travel Advisor] Analyzing weather: {weather_info}...")
        if "sunny" in weather_info.lower():
            return "Perfect for outdoor sightseeing! Visit parks and landmarks."
        elif "rainy" in weather_info.lower():
            return "Great time for museums and indoor attractions!"
        elif "snowy" in weather_info.lower():
            return "Bundle up! Perfect for cozy cafes and winter sports."
        else:
            return "Good weather for exploring the city!"

    travel_agent.build()
    print("  ✓ Travel Advisor ready\n")

    # Demo: Multi-Agent Workflow
    print("=" * 60)
    print("SCENARIO: Travel Planning Workflow")
    print("=" * 60)
    print("User → Weather Expert → Travel Advisor → User\n")

    # Step 1: Get weather from Weather Expert
    print("-" * 40)
    print("Step 1: User asks Weather Expert")
    print("-" * 40)
    print("User: What's the weather in London?")
    weather_response = await weather_agent.send_message_async(
        "What's the weather in London?"
    )
    print(f"Weather Expert: {weather_response}\n")

    await asyncio.sleep(1)

    # Step 2: Get travel advice from Travel Advisor
    print("-" * 40)
    print("Step 2: User asks Travel Advisor")
    print("-" * 40)
    print("User: What should I do in rainy London?")
    travel_response = await travel_agent.send_message_async(
        "What should I do in rainy London?"
    )
    print(f"Travel Advisor: {travel_response}\n")

    await asyncio.sleep(1)

    # Step 3: Combined workflow
    print("-" * 40)
    print("Step 3: Query Paris weather")
    print("-" * 40)
    print("User: How about Paris?")
    paris_weather = await weather_agent.send_message_async("How about Paris?")
    print(f"Weather Expert: {paris_weather}\n")

    await asyncio.sleep(1)

    # Step 4: Auto-routing based on response
    print("-" * 40)
    print("Step 4: Get Paris travel advice")
    print("-" * 40)
    print("User: Should I visit sunny Paris or rainy London?")
    comparison = await travel_agent.send_message_async(
        "Should I visit sunny Paris or rainy London?"
    )
    print(f"Travel Advisor: {comparison}\n")

    await asyncio.sleep(1)

    # Step 5: Show both agents working together
    print("-" * 40)
    print("Step 5: Tokyo weather + recommendations")
    print("-" * 40)

    # Get Tokyo weather
    print("User (to Weather): What's the weather in Tokyo?")
    tokyo_weather = await weather_agent.send_message_async(
        "What's the weather in Tokyo?"
    )
    print(f"Weather Expert: {tokyo_weather}")

    # Get Tokyo recommendations
    print("\nUser (to Travel): What should I do in Tokyo with this weather?")
    tokyo_travel = await travel_agent.send_message_async(
        "What should I do in Tokyo when it's cloudy?"
    )
    print(f"Travel Advisor: {tokyo_travel}\n")

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\n📚 Key Concepts Demonstrated:")
    print("  ✓ Multiple LlmAgent instances with different roles")
    print("  ✓ Specialized agents (Weather Expert & Travel Advisor)")
    print("  ✓ Custom actions with @agent.action() decorator")
    print("  ✓ Direct agent communication via send_message_async()")
    print("  ✓ Multi-agent workflow patterns")
    print("\n💡 Communication Patterns:")
    print("  • Direct messaging: await agent.send_message_async()")
    print("  • Sequential workflow: Agent A → Agent B → User")
    print("  • Parallel queries: Multiple agents answer same domain")
    print("  • Coordinated responses: Combining multiple agent outputs")
    print("\n📝 Note:")
    print("  For true mesh routing (mesh.send_to()), use custom Agent")
    print("  subclasses as shown in demo_agent_mesh_local.py")


if __name__ == "__main__":
    asyncio.run(main())

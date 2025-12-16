"""
Demo: LLM Agents with Mesh Routing

Demonstrates direct LlmAgent integration with PyLocalMesh:
- LlmAgent directly added to mesh via mesh.add_llm_agent()
- Multiple LLM agents communicating via mesh.send_to()
- Agent-to-agent communication patterns
"""

import time
from ceylonai_next import LlmAgent, LocalMesh


def main():
    print("=" * 70)
    print("Demo: LLM Agents with Mesh Routing")
    print("=" * 70)
    print("Direct LlmAgent mesh integration (no wrapper needed)\n")

    # Create mesh network
    mesh = LocalMesh("llm_mesh")
    print("✓ Created LocalMesh: llm_mesh\n")

    # Agent 1: Weather Expert
    print("Creating Weather Expert Agent...")
    weather_llm = LlmAgent("weather_llm", "ollama::gemma3:latest")
    weather_llm.with_system_prompt(
        "You are a weather expert. Answer weather questions concisely in 2-3 sentences."
    )
    weather_llm.with_temperature(0.4)
    weather_llm.with_max_tokens(150)

    @weather_llm.action(description="Get current weather for a location")
    def get_weather(location: str):
        print(f"  [Tool] get_weather({location})")
        weather_data = {
            "london": "Rainy, 15°C",
            "paris": "Sunny, 22°C",
            "tokyo": "Cloudy, 18°C",
            "new york": "Snowy, -2°C",
        }
        return weather_data.get(location.lower(), "Unknown, 20°C")

    weather_llm.build()
    print("  ✓ Weather Expert ready")

    # Agent 2: Travel Advisor
    print("Creating Travel Advisor Agent...")
    travel_llm = LlmAgent("travel_llm", "ollama::gemma3:latest")
    travel_llm.with_system_prompt(
        "You are a travel advisor. Give brief, enthusiastic recommendations in 2-3 sentences."
    )
    travel_llm.with_temperature(0.7)
    travel_llm.with_max_tokens(150)

    @travel_llm.action(description="Get travel recommendation")
    def recommend_activity(weather: str):
        print(f"  [Tool] recommend_activity({weather})")
        if "sunny" in weather.lower():
            return "Perfect for outdoor sightseeing!"
        elif "rainy" in weather.lower():
            return "Great time for museums!"
        elif "snowy" in weather.lower():
            return "Cozy cafes and winter sports!"
        else:
            return "Good for exploring!"

    travel_llm.build()
    print("  ✓ Travel Advisor ready\n")

    # Add agents to mesh using the add_llm_agent method
    print("Adding agents to mesh...")
    mesh.add_llm_agent(weather_llm)
    mesh.add_llm_agent(travel_llm)
    print("  ✓ Agents added to mesh")

    # Start mesh
    mesh.start()
    print("  ✓ Mesh started\n")

    time.sleep(0.5)

    # Demo 1: Direct routing with mesh.send_to()
    print("=" * 70)
    print("DEMO 1: Direct Message Routing")
    print("=" * 70)
    print("Using mesh.send_to(agent_name, message)\n")

    print("-" * 40)
    print("Query 1: Weather in London")
    print("-" * 40)
    mesh.send_to("weather_llm", "What's the weather in London?")
    time.sleep(3)

    print("\n" + "-" * 40)
    print("Query 2: Weather in Paris")
    print("-" * 40)
    mesh.send_to("weather_llm", "How about Paris?")
    time.sleep(3)

    print("\n" + "-" * 40)
    print("Query 3: Travel advice")
    print("-" * 40)
    mesh.send_to("travel_llm", "What should I do in rainy London?")
    time.sleep(3)

    # Demo 2: Multi-agent workflow
    print("\n" + "=" * 70)
    print("DEMO 2: Multi-Agent Workflow")
    print("=" * 70)
    print("Coordinated queries to different agents\n")

    print("-" * 40)
    print("Step 1: Get Tokyo weather")
    print("-" * 40)
    mesh.send_to("weather_llm", "What's the weather in Tokyo?")
    time.sleep(3)

    print("\n" + "-" * 40)
    print("Step 2: Get travel recommendations")
    print("-" * 40)
    mesh.send_to("travel_llm", "What should I do in cloudy Tokyo?")
    time.sleep(3)

    # Demo 3: Broadcast to all agents
    print("\n" + "=" * 70)
    print("DEMO 3: Broadcast Messages")
    print("=" * 70)
    print("Using mesh.broadcast(message) to send to all agents\n")

    print("-" * 40)
    print("Broadcast 1: General announcement")
    print("-" * 40)
    print("Broadcasting: 'System announcement: Please prepare status report'")
    mesh.broadcast("System announcement: Please prepare status report")
    time.sleep(3)

    print("\n" + "-" * 40)
    print("Broadcast 2: With exclusion")
    print("-" * 40)
    print("Broadcasting to all except weather_expert...")
    mesh.broadcast(
        "Special update for travel-related agents only", exclude="weather_llm"
    )
    time.sleep(3)

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\n📚 Key Concepts Demonstrated:")
    print("  ✓ mesh.add_llm_agent(agent) - Direct LlmAgent mesh integration")
    print("  ✓ mesh.send_to(name, msg) - Direct message routing by name")
    print("  ✓ mesh.broadcast(msg) - Send to all agents")
    print("  ✓ mesh.broadcast(msg, exclude=name) - Broadcast with exclusion")
    print("  ✓ Agent decoupling - Agents communicate via names, not references")
    print("  ✓ Custom actions - @agent.action() works through mesh")
    print("\n💡 Benefits of Direct Integration:")
    print("  • No wrapper class needed")
    print("  • Loose coupling between agents")
    print("  • Easy to add/remove agents dynamically")
    print("  • Consistent API for local & distributed")
    print("  • Enables coordinator and swarm patterns")
    print("  • Broadcast for system-wide announcements")


if __name__ == "__main__":
    main()

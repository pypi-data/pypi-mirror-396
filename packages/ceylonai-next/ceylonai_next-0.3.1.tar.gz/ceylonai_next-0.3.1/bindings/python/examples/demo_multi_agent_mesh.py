"""
Demo: Multi-Agent Communication with Mesh Routing

This demonstrates two LLM agents working together using the mesh routing pattern:
- mesh.add_llm_agent() for direct LlmAgent integration
- mesh.submit() for fire-and-forget requests
- mesh.wait_for() for getting specific results
"""

import time
from ceylonai_next import LlmAgent, LocalMesh


def main():
    print("Demo: Multi-Agent LLM Communication")
    print("=" * 60)
    print("Two LLM agents working together via mesh routing\n")

    # Create mesh network
    mesh = LocalMesh("multi_agent_mesh")
    print("✓ Created mesh network: multi_agent_mesh\n")

    # Agent 1: Weather Expert
    print("Creating Weather Expert Agent...")
    weather_agent = LlmAgent("weather_expert", "ollama::gemma3:latest")
    weather_agent.with_system_prompt(
        "You are a weather expert. Respond with brief, helpful weather information. "
        "Keep responses to 1-2 sentences."
    )
    weather_agent.with_temperature(0.4)
    weather_agent.with_max_tokens(100)
    weather_agent.build()
    print("  ✓ Weather Expert ready")

    # Agent 2: Travel Advisor
    print("Creating Travel Advisor Agent...")
    travel_agent = LlmAgent("travel_advisor", "ollama::gemma3:latest")
    travel_agent.with_system_prompt(
        "You are a travel advisor. Give brief, enthusiastic travel recommendations. "
        "Keep responses to 1-2 sentences."
    )
    travel_agent.with_temperature(0.7)
    travel_agent.with_max_tokens(100)
    travel_agent.build()
    print("  ✓ Travel Advisor ready\n")

    # Add agents to mesh using add_llm_agent
    print("Adding agents to mesh...")
    mesh.add_llm_agent(weather_agent)
    mesh.add_llm_agent(travel_agent)
    print("  ✓ Both agents added to mesh")

    # Start mesh
    mesh.start()
    print("  ✓ Mesh started\n")

    time.sleep(0.5)

    # Demo: Multi-Agent Workflow via Mesh
    print("=" * 60)
    print("SCENARIO: Travel Planning Workflow")
    print("=" * 60)
    print("Using mesh.submit() and mesh.wait_for() for routing\n")

    # Step 1: Get weather from Weather Expert
    print("-" * 40)
    print("Step 1: Query Weather Expert")
    print("-" * 40)
    print("User: What's the weather like in London today?")

    req1 = mesh.submit("weather_expert", "What's the weather like in London today?")
    result1 = mesh.wait_for(req1, timeout=30.0, reminder_interval=10.0)
    print(f"Weather Expert: {result1.response}\n")

    time.sleep(0.5)

    # Step 2: Get travel advice from Travel Advisor
    print("-" * 40)
    print("Step 2: Query Travel Advisor")
    print("-" * 40)
    print("User: What should I do if it's raining in London?")

    req2 = mesh.submit("travel_advisor", "What should I do if it's raining in London?")
    result2 = mesh.wait_for(req2, timeout=30.0, reminder_interval=10.0)
    print(f"Travel Advisor: {result2.response}\n")

    time.sleep(0.5)

    # Step 3: Paris weather
    print("-" * 40)
    print("Step 3: Query Paris weather")
    print("-" * 40)
    print("User: What's the typical weather in Paris in spring?")

    req3 = mesh.submit(
        "weather_expert", "What's the typical weather in Paris in spring?"
    )
    result3 = mesh.wait_for(req3, timeout=30.0, reminder_interval=10.0)
    print(f"Weather Expert: {result3.response}\n")

    time.sleep(0.5)

    # Step 4: Travel comparison
    print("-" * 40)
    print("Step 4: Get travel recommendation")
    print("-" * 40)
    print("User: Should I visit Paris or London for a spring vacation?")

    req4 = mesh.submit(
        "travel_advisor", "Should I visit Paris or London for a spring vacation?"
    )
    result4 = mesh.wait_for(req4, timeout=30.0, reminder_interval=10.0)
    print(f"Travel Advisor: {result4.response}\n")

    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\n📚 Key Concepts Demonstrated:")
    print("  ✓ mesh.add_llm_agent() - Direct LlmAgent mesh integration")
    print("  ✓ mesh.submit() - Fire-and-forget with request ID")
    print("  ✓ mesh.wait_for() - Wait for specific result")
    print("  ✓ Multi-agent workflow patterns")
    print("\n💡 Communication Patterns:")
    print("  • Mesh routing: mesh.submit() + mesh.wait_for()")
    print("  • Sequential workflow: Agent A → Agent B → User")
    print("  • Request tracking via request IDs")


if __name__ == "__main__":
    main()

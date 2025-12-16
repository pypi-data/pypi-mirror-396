"""
Demo: Async Mesh Results with LLM Agents

Demonstrates the new async result retrieval pattern:
- mesh.submit(target, message) - Fire-and-forget with request ID
- mesh.get_results() - Non-blocking poll for results
- mesh.collect_results() - Blocking wait with auto-reminders
- mesh.wait_for(request_id) - Wait for specific result
- mesh.send_reminders() - Manual reminder sending
"""

import time
from ceylonai_next import LlmAgent, LocalMesh


def main():
    print("=" * 70)
    print("Demo: Async Mesh Results")
    print("=" * 70)
    print("Fire-and-forget submission with async result retrieval\n")

    # Create mesh network
    mesh = LocalMesh("demo_mesh")
    print("✓ Created LocalMesh: demo_mesh\n")

    # Create Weather Expert Agent
    print("Creating Weather Expert Agent...")
    weather_llm = LlmAgent("weather_llm", "ollama::gemma3:latest")
    weather_llm.with_system_prompt(
        "You are a weather expert. Answer weather questions concisely in 1-2 sentences."
    )
    weather_llm.with_temperature(0.4)
    weather_llm.with_max_tokens(100)
    weather_llm.build()
    print("  ✓ Weather Expert ready")

    # Add agent and start mesh
    mesh.add_llm_agent(weather_llm)
    mesh.start()
    print("  ✓ Mesh started\n")

    time.sleep(0.5)

    # Demo 1: Fire-and-forget with submit()
    print("=" * 70)
    print("DEMO 1: Fire-and-Forget Submission")
    print("=" * 70)
    print("Using mesh.submit() - returns immediately with request ID\n")

    print("Submitting requests...")
    req1 = mesh.submit("weather_llm", "What's the weather in London?")
    print(f"  ✓ Request 1 submitted: {req1[:8]}...")

    req2 = mesh.submit("weather_llm", "What's the weather in Paris?")
    print(f"  ✓ Request 2 submitted: {req2[:8]}...")

    req3 = mesh.submit("weather_llm", "What's the weather in Tokyo?")
    print(f"  ✓ Request 3 submitted: {req3[:8]}...\n")

    # Check pending requests
    pending = mesh.get_pending()
    print(f"Pending requests: {len(pending)}")
    for p in pending:
        print(f"  - {p.id[:8]}... -> {p.target} ({p.elapsed_seconds:.1f}s ago)")

    # Demo 2: Manual polling with get_results()
    print("\n" + "=" * 70)
    print("DEMO 2: Manual Polling")
    print("=" * 70)
    print("Using mesh.get_results() and mesh.send_reminders()\n")

    print("Polling for results...")
    while mesh.has_pending():
        results = mesh.get_results()
        for r in results:
            print(f"  ✓ Got result for {r.request_id[:8]}...")
            print(f"    Response: {r.response[:60]}...")
            print(f"    Duration: {r.duration_ms}ms")

        # Send reminders for requests older than 5 seconds
        reminded = mesh.send_reminders(older_than_secs=5.0)
        if reminded:
            print(f"  Sent {len(reminded)} reminder(s)")

        time.sleep(1)

    print("\n✓ All results collected!\n")

    # Demo 3: Blocking collection with collect_results()
    print("=" * 70)
    print("DEMO 3: Blocking Collection")
    print("=" * 70)
    print("Using mesh.collect_results() - blocks until all complete\n")

    # Submit more requests
    mesh.submit("weather_llm", "Weather in Sydney?")
    mesh.submit("weather_llm", "Weather in Berlin?")
    print("Submitted 2 new requests...")
    print("Waiting for all results (with auto-reminders every 10s)...\n")

    results = mesh.collect_results(reminder_interval=10.0)
    for r in results:
        print(f"  ✓ {r.request_id[:8]}: {r.response[:50]}...")

    print("\n✓ All results collected!\n")

    # Demo 4: Wait for specific result
    print("=" * 70)
    print("DEMO 4: Wait for Single Result")
    print("=" * 70)
    print("Using mesh.wait_for(request_id) - wait for specific result\n")

    req = mesh.submit("weather_llm", "Weather in New York?")
    print(f"Submitted request: {req[:8]}...")
    print("Waiting for this specific result...\n")

    try:
        result = mesh.wait_for(req, timeout=30.0, reminder_interval=10.0)
        print(f"  ✓ Got result!")
        print(f"    Response: {result.response}")
        print(f"    Duration: {result.duration_ms}ms")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\n📚 New APIs Demonstrated:")
    print("  ✓ mesh.submit(target, msg) - Fire-and-forget, returns request_id")
    print("  ✓ mesh.get_pending() - Check pending requests")
    print("  ✓ mesh.get_results() - Poll for completed results")
    print("  ✓ mesh.send_reminders(secs) - Send reminders for stale requests")
    print("  ✓ mesh.collect_results(interval) - Block until all complete")
    print("  ✓ mesh.wait_for(id, timeout) - Wait for specific result")


if __name__ == "__main__":
    main()

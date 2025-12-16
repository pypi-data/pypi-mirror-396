"""
Demo: Broadcast Messaging with Mesh Agents

Demonstrates broadcast functionality in PyLocalMesh:
- Broadcasting messages to all agents
- Broadcasting with agent exclusion
- Coordinated agent responses to broadcasts
- Use cases for system-wide announcements
"""

import time
import asyncio
from ceylonai_next import LlmAgent, Agent, PyLocalMesh


class LlmMeshAgent(Agent):
    """
    Wrapper that enables LlmAgent to work with PyLocalMesh.

    This bridges LlmAgent (high-level LLM interface) with Agent (mesh agent interface)
    by implementing the on_message() callback required for mesh routing.
    """

    def __new__(cls, name: str, llm_agent: LlmAgent):
        """Override __new__() to bypass PyAgent initialization."""
        return Agent.__new__(cls)

    def __init__(self, name: str, llm_agent: LlmAgent):
        """Initialize mesh-compatible LLM agent."""
        super().__init__()
        self._agent_name = name
        self.llm_agent = llm_agent
        self.message_count = 0
        self.broadcast_count = 0

    def on_message(self, message, context=None):
        """
        Handle incoming messages from mesh.

        Uses async send_message_async to avoid runtime conflicts.
        """
        self.message_count += 1

        # Check if it's a broadcast message
        message_str = message if isinstance(message, str) else message.decode("utf-8")
        is_broadcast = (
            "System announcement" in message_str or "Special update" in message_str
        )

        if is_broadcast:
            self.broadcast_count += 1
            print(f"\n📢 [{self.name()}] Received broadcast #{self.broadcast_count}")
            print(f"   Content: {message_str}")
            # For broadcasts, we acknowledge but don't need LLM response
            return f"[{self.name()}] Acknowledged: {message_str}"
        else:
            print(f"\n📨 [{self.name()}] Received message #{self.message_count}")
            print(f"   Message: {message_str}")

        try:
            # Use async version to avoid tokio runtime conflicts
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(
                    self.llm_agent.send_message_async(message_str)
                )
            finally:
                loop.close()

            print(f"💬 [{self.name()}] Response: {response}")
            return response

        except Exception as e:
            error_msg = f"Error processing message: {e}"
            print(f"❌ [{self.name()}] {error_msg}")
            return error_msg


def main():
    print("=" * 70)
    print("Demo: Broadcast Messaging with Mesh Agents")
    print("=" * 70)
    print("Showcasing broadcast patterns in multi-agent systems\n")

    # Create mesh network
    mesh = PyLocalMesh("broadcast_demo_mesh")
    print("✓ Created PyLocalMesh: broadcast_demo_mesh\n")

    # Agent 1: Coordinator
    print("Creating Coordinator Agent...")
    coordinator_llm = LlmAgent("coordinator_llm", "ollama::gemma3:latest")
    coordinator_llm.with_system_prompt(
        "You are a coordinator agent. Respond briefly to status requests and announcements."
    )
    coordinator_llm.with_temperature(0.3)
    coordinator_llm.with_max_tokens(100)
    coordinator_llm.build()
    coordinator = LlmMeshAgent("coordinator", coordinator_llm)
    print("  ✓ Coordinator ready")

    # Agent 2: Worker A
    print("Creating Worker A Agent...")
    worker_a_llm = LlmAgent("worker_a_llm", "ollama::gemma3:latest")
    worker_a_llm.with_system_prompt(
        "You are Worker A. Acknowledge tasks and system messages briefly."
    )
    worker_a_llm.with_temperature(0.3)
    worker_a_llm.with_max_tokens(100)
    worker_a_llm.build()
    worker_a = LlmMeshAgent("worker_a", worker_a_llm)
    print("  ✓ Worker A ready")

    # Agent 3: Worker B
    print("Creating Worker B Agent...")
    worker_b_llm = LlmAgent("worker_b_llm", "ollama::gemma3:latest")
    worker_b_llm.with_system_prompt(
        "You are Worker B. Acknowledge tasks and system messages briefly."
    )
    worker_b_llm.with_temperature(0.3)
    worker_b_llm.with_max_tokens(100)
    worker_b_llm.build()
    worker_b = LlmMeshAgent("worker_b", worker_b_llm)
    print("  ✓ Worker B ready\n")

    # Add agents to mesh
    print("Adding agents to mesh...")
    mesh.add_agent(coordinator)
    mesh.add_agent(worker_a)
    mesh.add_agent(worker_b)
    print("  ✓ All agents added to mesh")

    # Start mesh
    mesh.start()
    print("  ✓ Mesh started\n")

    time.sleep(0.5)

    # Demo 1: Broadcast to all agents
    print("=" * 70)
    print("DEMO 1: Broadcast to All Agents")
    print("=" * 70)
    print("Sending a system announcement to all agents\n")

    print("-" * 40)
    print("Broadcasting system announcement...")
    print("-" * 40)
    mesh.broadcast("System announcement: All agents report status")
    time.sleep(2)

    # Demo 2: Direct message (for comparison)
    print("\n" + "=" * 70)
    print("DEMO 2: Direct Message (For Comparison)")
    print("=" * 70)
    print("Sending direct message to coordinator\n")

    print("-" * 40)
    print("Direct message to coordinator...")
    print("-" * 40)
    mesh.send_to("coordinator", "What is your current status?")
    time.sleep(3)

    # Demo 3: Broadcast with exclusion
    print("\n" + "=" * 70)
    print("DEMO 3: Broadcast with Exclusion")
    print("=" * 70)
    print("Broadcasting to all workers, excluding coordinator\n")

    print("-" * 40)
    print("Broadcasting to workers only...")
    print("-" * 40)
    mesh.broadcast(
        "Special update: Worker tasks have been updated", exclude="coordinator"
    )
    time.sleep(2)

    # Demo 4: Multiple broadcasts
    print("\n" + "=" * 70)
    print("DEMO 4: Multiple Broadcast Patterns")
    print("=" * 70)
    print("Demonstrating different broadcast scenarios\n")

    print("-" * 40)
    print("Scenario 1: System maintenance announcement")
    print("-" * 40)
    mesh.broadcast("System announcement: Scheduled maintenance in 5 minutes")
    time.sleep(2)

    print("\n" + "-" * 40)
    print("Scenario 2: Exclude Worker A")
    print("-" * 40)
    mesh.broadcast(
        "Special update: Worker B and Coordinator alignment", exclude="worker_a"
    )
    time.sleep(2)

    # Show statistics
    print("\n" + "=" * 70)
    print("Statistics")
    print("=" * 70)
    print(f"Coordinator:")
    print(f"  - Total messages: {coordinator.message_count}")
    print(f"  - Broadcast messages: {coordinator.broadcast_count}")
    print(f"\nWorker A:")
    print(f"  - Total messages: {worker_a.message_count}")
    print(f"  - Broadcast messages: {worker_a.broadcast_count}")
    print(f"\nWorker B:")
    print(f"  - Total messages: {worker_b.message_count}")
    print(f"  - Broadcast messages: {worker_b.broadcast_count}")

    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print("\n📚 Key Concepts Demonstrated:")
    print("  ✓ mesh.broadcast(msg) - Send message to all agents")
    print("  ✓ mesh.broadcast(msg, exclude=name) - Exclude specific agent")
    print("  ✓ System-wide announcements - Coordinated messaging")
    print("  ✓ Selective broadcasting - Target specific agent groups")
    print("  ✓ Message tracking - Count broadcast vs direct messages")
    print("\n💡 Broadcast Use Cases:")
    print("  • System maintenance notifications")
    print("  • Configuration updates to all agents")
    print("  • Emergency alerts")
    print("  • Status synchronization")
    print("  • Coordinated task distribution")
    print("  • Selective group communication (using exclude)")


if __name__ == "__main__":
    main()

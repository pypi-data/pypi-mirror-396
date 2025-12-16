#!/usr/bin/env python3
"""
Ceylon AI - Local Agent Mesh Example

Demonstrates basic local mesh networking with multiple agents:
- Creating a local mesh network
- Adding multiple agents to the mesh
- Agent-to-agent communication
- Message routing and handling
- Synchronous message processing

This is the simplest example of Ceylon's mesh architecture.
"""

import time
from ceylonai_next import Agent, LocalMesh


class PingAgent(Agent):
    """Agent that responds to ping messages"""

    def __init__(self, name):
        super().__init__(name)
        self.ping_count = 0

    def on_message(self, message, context=None):
        """Handle incoming ping messages"""
        self.ping_count += 1
        print(f"🏓 [{self.name()}] Received ping #{self.ping_count}: {message}")
        return f"Pong from {self.name()} (count: {self.ping_count})"


class EchoAgent(Agent):
    """Agent that echoes messages back"""

    def __init__(self, name):
        super().__init__(name)
        self.messages_received = []

    def on_message(self, message, context=None):
        """Handle incoming messages by echoing them"""
        self.messages_received.append(message)
        print(f"📢 [{self.name()}] Echoing: {message}")
        return f"Echo: {message}"


class RouterAgent(Agent):
    """Agent that routes messages to other agents"""

    def __init__(self, name, mesh):
        super().__init__(name)
        self.mesh = mesh
        self.routed_count = 0

    def on_message(self, message, context=None):
        """Route messages to appropriate agents"""
        self.routed_count += 1
        print(f"🔀 [{self.name()}] Routing message #{self.routed_count}: {message}")

        # Parse routing instruction from message
        # Format: "route:target_agent:actual_message"
        if message.startswith("route:"):
            parts = message.split(":", 2)
            if len(parts) >= 3:
                target = parts[1]
                actual_msg = parts[2]
                print(f"   ➡️  Forwarding to {target}")
                self.mesh.send_to(target, actual_msg)
                return f"Routed to {target}"

        return "Invalid routing format. Use: route:target:message"


def main():
    """Main demo of local mesh networking"""
    print("=" * 70)
    print("Ceylon AI - Local Agent Mesh Demo")
    print("=" * 70)
    print()

    # Step 1: Create the mesh network
    print("🌐 Creating local mesh network...")
    mesh = LocalMesh("demo_local_mesh")
    print("   ✓ Mesh 'demo_local_mesh' created")
    print()

    # Step 2: Create agents
    print("🤖 Creating agents...")
    ping_agent = PingAgent("ping_agent")
    echo_agent = EchoAgent("echo_agent")
    router_agent = RouterAgent("router_agent", mesh)
    print("   ✓ Created ping_agent")
    print("   ✓ Created echo_agent")
    print("   ✓ Created router_agent")
    print()

    # Step 3: Add agents to mesh
    print("🔗 Adding agents to mesh...")
    mesh.add_agent(ping_agent)
    mesh.add_agent(echo_agent)
    mesh.add_agent(router_agent)
    print("   ✓ All agents added to mesh")
    print()

    # Step 4: Direct messaging
    print("=" * 70)
    print("Test 1: Direct Messaging")
    print("=" * 70)
    print()

    print("Sending direct messages to agents...")
    mesh.send_to("ping_agent", "Hello Ping!")
    time.sleep(0.1)

    mesh.send_to("echo_agent", "Hello Echo!")
    time.sleep(0.1)

    mesh.send_to("ping_agent", "Another ping")
    time.sleep(0.1)
    mesh.process_messages()  # Process pending messages
    print()

    # Step 5: Routed messaging
    print("=" * 70)
    print("Test 2: Routed Messaging")
    print("=" * 70)
    print()

    print("Sending messages through router agent...")
    mesh.send_to("router_agent", "route:ping_agent:Routed ping message")
    time.sleep(0.1)

    mesh.send_to("router_agent", "route:echo_agent:Routed echo message")
    time.sleep(0.1)
    mesh.process_messages()  # Process routed messages
    print()

    # Step 6: Multiple messages
    print("=" * 70)
    print("Test 3: Multiple Messages")
    print("=" * 70)
    print()

    print("Sending batch of messages...")
    messages = [
        ("ping_agent", "Batch ping 1"),
        ("ping_agent", "Batch ping 2"),
        ("echo_agent", "Batch echo 1"),
        ("echo_agent", "Batch echo 2"),
    ]

    for target, msg in messages:
        mesh.send_to(target, msg)
        time.sleep(0.05)
    mesh.process_messages()  # Process batch messages
    print()

    # Step 7: Show statistics
    print("=" * 70)
    print("Statistics")
    print("=" * 70)
    print()
    print("Ping Agent:")
    print(f"  • Total pings received: {ping_agent.ping_count}")
    print()
    print("Echo Agent:")
    print(f"  • Total messages received: {len(echo_agent.messages_received)}")
    print(f"  • Messages: {echo_agent.messages_received}")
    print()
    print("Router Agent:")
    print(f"  • Total messages routed: {router_agent.routed_count}")
    print()

    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Key Concepts Demonstrated:")
    print("  ✓ PyLocalMesh - Local in-memory mesh network")
    print("  ✓ Custom Agents - Agents with custom message handlers")
    print("  ✓ Direct Messaging - mesh.send_to(agent_name, message)")
    print("  ✓ Agent Communication - Agents sending to other agents")
    print("  ✓ Message Routing - Router pattern implementation")
    print()


if __name__ == "__main__":
    main()

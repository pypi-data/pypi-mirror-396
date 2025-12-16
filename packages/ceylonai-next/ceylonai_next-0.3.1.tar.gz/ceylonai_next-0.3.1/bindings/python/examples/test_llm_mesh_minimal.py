"""
Minimal test for LlmMeshAgent wrapper
"""

from ceylonai_next import LlmAgent, Agent, PyLocalMesh


class LlmMeshAgent(Agent):
    """Minimal wrapper for testing"""

    def __new__(cls, name: str, llm_agent: LlmAgent):
        return Agent.__new__(cls)

    def __init__(self, name: str, llm_agent: LlmAgent):
        super().__init__()
        self._agent_name = name
        self.llm_agent = llm_agent

    def on_message(self, message, context=None):
        print(f"[{self.name()}] Received: {message}")
        response = self.llm_agent.send_message(message)
        print(f"[{self.name()}] Response: {response}")
        return response


def main():
    print("Testing LlmMeshAgent wrapper...")

    # Create simple LLM agent
    print("\n1. Creating LlmAgent...")
    agent_llm = LlmAgent("test_llm", "ollama::gemma3:latest")
    agent_llm.with_system_prompt("You are a test agent. Keep responses to 1 sentence.")
    agent_llm.build()
    print("   ✓ LlmAgent created")

    # Wrap in mesh agent
    print("\n2. Creating LlmMeshAgent wrapper...")
    mesh_agent = LlmMeshAgent("test_agent", agent_llm)
    print(f"   ✓ Wrapper created with name: {mesh_agent.name()}")

    # Test on_message directly
    print("\n3. Testing on_message() directly...")
    response = mesh_agent.on_message("Hello, test!")
    print(f"   ✓ Direct call works")

    # Now try mesh
    print("\n4. Creating mesh...")
    mesh = PyLocalMesh("test_mesh")
    print("   ✓ Mesh created")

    print("\n5. Adding agent to mesh...")
    try:
        mesh.add_agent(mesh_agent)
        print("   ✓ Agent added to mesh")
    except Exception as e:
        print(f"   ✗ Failed to add agent: {e}")
        return

    print("\n6. Starting mesh...")
    try:
        mesh.start()
        print("   ✓ Mesh started")
    except Exception as e:
        print(f"   ✗ Failed to start mesh: {e}")
        return

    print("\n7. Sending message via mesh...")
    try:
        mesh.send_to("test_agent", "Test message via mesh")
        print("   ✓ Message sent")
    except Exception as e:
        print(f"   ✗ Failed to send: {e}")

    print("\n✅ Test complete!")


if __name__ == "__main__":
    main()

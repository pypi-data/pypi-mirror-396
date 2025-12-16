# Import from the native Rust extension module explicitly
from ceylonai_next.ceylonai_next import (
    # Mesh components
    PyLocalMesh,
    PyDistributedMesh,
    PyMeshRequest,
    PyMeshResult,
    # Agent components
    PyAgent,
    PyAgentContext,
    PyAgentMessageProcessor,
    # Action/Tool components
    _PyAction,
    PyToolInvoker,
    # LLM components
    PyLlmAgent,
    PyLlmConfig,
    # Memory components
    PyMemoryEntry,
    PyMemoryQuery,
    PyInMemoryBackend,
    PyRedisBackend,
    # ReAct framework components
    PyReActConfig,
    PyReActStep,
    PyReActResult,
    # Registry components
    PyAgentMetadata,
    PyInMemoryRegistry,
    # Logging components
    PyLoggingConfig,
    PyLoggingHandle,
    init_logging_py,
    # Metrics
    get_metrics,
)
import inspect
import json
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# Define the public API
__all__ = [
    # Rust native bindings (re-exported)
    "PyLocalMesh",
    "PyDistributedMesh",
    "PyMeshRequest",
    "PyMeshResult",
    "PyAgent",
    "PyAgentContext",
    "PyAgentMessageProcessor",
    "_PyAction",
    "PyToolInvoker",
    "PyLlmAgent",
    "PyLlmConfig",
    "PyMemoryEntry",
    "PyMemoryQuery",
    "PyInMemoryBackend",
    "PyRedisBackend",
    "PyReActConfig",
    "PyReActStep",
    "PyReActResult",
    "PyAgentMetadata",
    "PyInMemoryRegistry",
    "PyLoggingConfig",
    "PyLoggingHandle",
    "init_logging_py",
    "get_metrics",
    # Python wrappers
    "PyAction",
    "FunctionalAction",
    "Agent",
    "LocalMesh",
    "DistributedMesh",
    "LlmConfig",
    "LlmAgent",
    "ReActConfig",
    "ReActStep",
    "ReActResult",
    "MemoryEntry",
    "MemoryQuery",
    "InMemoryBackend",
    "RedisBackend",
    "Memory",
    "LoggingConfig",
    "LoggingHandle",
    "init_logging",
    "MeshRequest",
    "MeshResult",
]


def _generate_schema_from_signature(func):
    """
    Generates a JSON schema from a function's type hints.
    """
    sig = inspect.signature(func)
    properties = {}
    required = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_type = "string"  # Default to string
        if param.annotation != inspect.Parameter.empty:
            if param.annotation in type_map:
                param_type = type_map[param.annotation]
            # Handle Optional, List, etc. later if needed

        properties[name] = {"type": param_type}

        if param.default == inspect.Parameter.empty:
            required.append(name)

    schema = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return json.dumps(schema)


class PyAction(_PyAction):
    def __new__(cls, name, description, input_schema=None, output_schema=None):
        if input_schema is None:
            input_schema = _generate_schema_from_signature(cls.execute)
        return super().__new__(cls, name, description, input_schema, output_schema)


class FunctionalAction(PyAction):
    def __new__(cls, func, name, description, input_schema=None, output_schema=None):
        # If input_schema is not provided, generate it from the function
        if input_schema is None:
            input_schema = _generate_schema_from_signature(func)
        # Create the instance using the parent's __new__
        instance = super().__new__(cls, name, description, input_schema, output_schema)
        # Store the function on the instance
        instance.func = func
        return instance

    def execute(self, context, inputs):
        # We need to map inputs to function arguments
        # For now, we assume inputs is a dict matching arguments
        # We also need to pass context if the function expects it

        sig = inspect.signature(self.func)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "context":
                kwargs["context"] = context
            elif name in inputs:
                kwargs[name] = inputs[name]
            elif param.default != inspect.Parameter.empty:
                continue  # Use default
            else:
                # Missing argument
                pass

        return self.func(**kwargs)


class Agent(PyAgent):
    def __init__(self, name="agent"):
        super().__init__()
        self._agent_name = name
        self.tool_invoker = PyToolInvoker()

    def name(self):
        return self._agent_name

    def action(self, name=None, description=""):
        def decorator(func):
            action_name = name or func.__name__
            action_desc = description or func.__doc__ or ""

            action = FunctionalAction(func, action_name, action_desc)
            self.tool_invoker.register(action)
            return func

        return decorator

    def on_message(self, message, context=None):
        """Handle incoming message. Override this method to process messages.

        Can be a synchronous method or an async method (async def).

        To return a response, return it from this method and it will be
        stored in last_response.

        Args:
            message: The message content (bytes or string)
            context: Optional PyAgentContext

        Returns:
            Response string that will be stored
        """
        # Default implementation does nothing
        # Subclasses should override this
        return None

    def send_message(self, message):
        """Send a message to the agent and get the response.

        This wraps on_message and returns the response.

        Args:
            message: Message string to send

        Returns:
            Response from the agent's on_message handler
        """
        # Create a dummy context
        context = PyAgentContext("python")

        # Call on_message (which can be overridden by subclasses)
        response = self.on_message(message, context)

        # Store the response in Rust
        self.set_last_response(response)

        return response if response is not None else "Message received"

    def last_response(self):
        """Get the last response from the agent.

        Returns:
            The last response string, or None if no messages sent yet
        """
        return self.get_last_response()


class LocalMesh(PyLocalMesh):
    """Python wrapper for LocalMesh with message processing support.

    Example:
        mesh = LocalMesh("my_mesh")
        agent = Agent("my_agent")
        mesh.add_agent(agent)  # Returns processor
        mesh.send_to("my_agent", "Hello")
        mesh.process_messages()  # Process pending messages
    """

    def __new__(cls, name):
        """Create a new LocalMesh instance."""
        instance = super().__new__(cls, name)
        instance._processors = []
        return instance

    def add_agent(self, agent):
        """Add an agent to the mesh.

        Returns a message processor that can be used to process messages
        for this specific agent. The mesh also stores it internally
        for batch processing via process_messages().
        """
        processor = super().add_agent(agent)
        self._processors.append(processor)
        return processor

    def process_messages(self):
        """Process all pending messages for all agents.

        This must be called periodically (e.g., in a loop) to let agents
        receive their messages. Messages are queued asynchronously and
        processed on the Python main thread for thread safety.

        Returns:
            Total number of messages processed across all agents.
        """
        total = 0
        for processor in self._processors:
            total += processor.process_pending()
        return total

    def add_llm_agent(self, agent):
        """Add an LlmAgent to the mesh.

        This method allows LlmAgent instances to be added to the mesh
        directly. Messages sent to the agent are automatically processed
        by the LLM.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        # Pass the internal _agent (PyLlmAgent) to the Rust binding
        return super().add_llm_agent(agent._agent)


class DistributedMesh(PyDistributedMesh):
    """Python wrapper for DistributedMesh with message processing support.

    Example:
        mesh = DistributedMesh("my_mesh", 9000)
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.process_messages()  # Process pending messages
    """

    def __new__(cls, name, port):
        """Create a new DistributedMesh instance."""
        instance = super().__new__(cls, name, port)
        instance._processors = []
        return instance

    def add_agent(self, agent):
        """Add an agent to the mesh.

        Returns a message processor that can be used to process messages
        for this specific agent.
        """
        processor = super().add_agent(agent)
        self._processors.append(processor)
        return processor

    def process_messages(self):
        """Process all pending messages for all agents."""
        total = 0
        for processor in self._processors:
            total += processor.process_pending()
        return total

    def add_llm_agent(self, agent):
        """Add an LlmAgent directly to the mesh.

        This method allows LlmAgent instances to be added to the mesh
        without needing a wrapper class. Messages sent to the agent
        are automatically processed by the LLM.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        # Pass the internal _agent (PyLlmAgent) to the Rust binding
        return super().add_llm_agent(agent._agent)


class LlmConfig(PyLlmConfig):
    """Configuration for LLM Agent.
    
    Example:
        config = LlmConfig.builder() \\
            .provider("ollama") \\
            .model("llama3.2:latest") \\
            .temperature(0.7) \\
            .build()
    """

    pass


class LlmAgent(Agent):
    """Python wrapper for LlmAgent with fluent builder API.

    Example:
        # Builder style
        agent = LlmAgent("my_agent", "ollama::gemma3:latest")
        agent.with_system_prompt("You are a helpful assistant.")
        agent.build()

        # Config style
        config = LlmConfig.builder().provider("ollama").model("llama2").build()
        agent = LlmAgent("my_agent", config)

        # Connect to mesh (after building)
        mesh = LocalMesh("my_mesh")
        mesh.add_llm_agent(agent)
    """

    def __new__(cls, *args, **kwargs):
        """Override __new__ to bypass PyAgent initialization."""
        return Agent.__new__(cls)

    def __init__(self, name, model_or_config, memory=None):
        """Create a new LLM agent.

        Args:
            name: Agent name (str)
            model_or_config: Model string (str) OR LlmConfig object
            memory: InMemoryBackend object (optional)
        """
        self._agent_name = name

        if isinstance(model_or_config, (LlmConfig, PyLlmConfig)):
            self._agent = PyLlmAgent.with_config(name, model_or_config)
        else:
            self._agent = PyLlmAgent(name, model_or_config)

        if memory:
            self._agent.with_memory(memory)

    def name(self):
        """Return the agent name."""
        return self._agent_name

    # Builder methods - delegate to Rust PyLlmAgent
    def with_api_key(self, api_key):
        """Set the API key for the LLM provider."""
        self._agent.with_api_key(api_key)
        return self

    def with_system_prompt(self, prompt):
        """Set the system prompt for the agent."""
        self._agent.with_system_prompt(prompt)
        return self

    def with_temperature(self, temp):
        """Set the temperature for generation (0.0 - 2.0)."""
        self._agent.with_temperature(temp)
        return self

    def with_max_tokens(self, tokens):
        """Set the maximum number of tokens to generate."""
        self._agent.with_max_tokens(tokens)
        return self

    def with_memory(self, memory):
        """Set the memory backend for the agent."""
        self._agent.with_memory(memory)
        return self

    def build(self):
        """Build the agent. Must be called before sending messages."""
        self._agent.build()
        return self

    def is_built(self):
        """Check if the agent has been built."""
        return self._agent.is_built()

    # Message methods - delegate to Rust (Rust handles "not built" error)
    def send_message(self, message):
        """Send a message to the agent."""
        return self._agent.send_message(message)

    async def send_message_async(self, message):
        """Send a message to the agent asynchronously."""
        return await self._agent.send_message_async(message)

    async def query_async(self, message):
        """Alias for send_message_async."""
        return await self.send_message_async(message)

    # Action registration - Python-specific due to decorator pattern
    def register_action(self, action):
        """Register a Python action with the agent."""
        self._agent.add_action(action)
        return self

    def action(self, name=None, description=""):
        """Decorator to register a function as an action.

        Example:
            @agent.action(description="Get weather")
            def get_weather(location: str):
                return "Sunny"
        """

        def decorator(func):
            action_name = name or func.__name__
            action_desc = description or func.__doc__ or ""
            action = FunctionalAction(func, action_name, action_desc)
            self.register_action(action)
            return func

        return decorator

    # ReAct methods - delegate to Rust
    def with_react(self, config=None):
        """Enable ReAct (Reason + Act) mode."""
        if config is None:
            config = PyReActConfig()
        self._agent.with_react(config)
        return self

    def send_message_react(self, message):
        """Send a message using ReAct reasoning mode."""
        return self._agent.send_message_react(message)


# ReAct Framework - use Rust implementations directly
# These aliases maintain backward compatibility with existing code
ReActConfig = PyReActConfig
ReActStep = PyReActStep
ReActResult = PyReActResult


class MemoryEntry(PyMemoryEntry):
    """Python wrapper for MemoryEntry with fluent API.

    Example:
        entry = MemoryEntry("Hello, world!")
        entry.with_metadata("type", "greeting")
        entry.with_metadata("user_id", "123")
        entry.with_ttl_seconds(3600)  # Expires in 1 hour
    """

    pass


class MemoryQuery(PyMemoryQuery):
    """Python wrapper for MemoryQuery with fluent API.

    Example:
        query = MemoryQuery()
        query.with_filter("type", "greeting")
        query.with_filter("user_id", "123")
        query.with_limit(10)
    """

    pass


class InMemoryBackend(PyInMemoryBackend):
    """Python wrapper for InMemoryBackend.

    Example:
        # Simple backend
        backend = InMemoryBackend()

        # With max entries limit (LRU eviction)
        backend = InMemoryBackend.with_max_entries(100)

        # With default TTL
        backend = InMemoryBackend.with_ttl_seconds(3600)

        # Store and retrieve
        entry = MemoryEntry("Hello, world!")
        entry_id = backend.store(entry)
        retrieved = backend.get(entry_id)
    """

    pass


class RedisBackend(PyRedisBackend):
    """Python wrapper for RedisBackend.

    Example:
        backend = RedisBackend("redis://localhost:6379")
        backend = backend.with_prefix("my_agent")
        backend = backend.with_ttl_seconds(3600)
    """

    pass


class Memory(ABC):
    """Abstract base class for custom memory backends.

    Extend this class to create custom memory implementations that can be used
    with LlmAgent. Useful for integrating vector databases, cloud storage, etc.

    Example:
        class VectorMemory(Memory):
            def __init__(self):
                self.vectors = {}

            def store(self, entry: MemoryEntry) -> str:
                # Store with vector embedding
                self.vectors[entry.id] = entry
                return entry.id

            def get(self, id: str) -> Optional[MemoryEntry]:
                return self.vectors.get(id)

            def search(self, query: MemoryQuery) -> List[MemoryEntry]:
                # Implement vector similarity search
                return list(self.vectors.values())

            def delete(self, id: str) -> bool:
                if id in self.vectors:
                    del self.vectors[id]
                    return True
                return False

            def clear(self):
                self.vectors.clear()

            def count(self) -> int:
                return len(self.vectors)

        # Use with agent
        agent = LlmAgent("agent", "model")
        agent.with_memory(VectorMemory())
    """

    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry and return its ID."""
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        pass

    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search for memory entries matching the query."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a memory entry. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all memory entries."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of entries in memory."""
        pass


class LoggingConfig(PyLoggingConfig):
    """Configuration for logging.

    Example:
        config = LoggingConfig("info", "ceylon.log", True)
    """

    pass


class LoggingHandle(PyLoggingHandle):
    """Handle to keep logging appenders alive."""

    pass


def init_logging(config: LoggingConfig) -> LoggingHandle:
    """Initialize logging with the given configuration.

    Args:
        config: LoggingConfig object

    Returns:
        LoggingHandle: Handle to keep logging active. Must be kept alive.
    """
    return init_logging_py(config)


# Mesh Request/Result aliases for cleaner Python API
MeshRequest = PyMeshRequest
MeshResult = PyMeshResult

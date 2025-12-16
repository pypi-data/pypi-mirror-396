use async_trait::async_trait;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use runtime::core::agent::{Agent, AgentContext};
use runtime::core::message::Message;
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};

/// Base class for Python Agents
#[derive(Clone)]
#[pyclass(subclass)]
pub struct PyAgent {
    last_response: Option<String>,
}

#[pymethods]
impl PyAgent {
    #[new]
    #[pyo3(signature = (*_args, **_kwargs))]
    fn new(_args: &Bound<'_, pyo3::types::PyTuple>, _kwargs: Option<&Bound<'_, PyDict>>) -> Self {
        PyAgent { last_response: None }
    }

    fn name(&self) -> String {
        "agent".to_string() // Default name, should be overridden by subclasses
    }

    /// Set the last response from the agent
    fn set_last_response(&mut self, response: Option<String>) {
        self.last_response = response;
    }

    /// Get the last response from the agent
    fn get_last_response(&self) -> Option<String> {
        self.last_response.clone()
    }

    fn act(self_: Py<Self>, action_name: String, inputs: Py<PyDict>) -> PyResult<Py<PyAny>> {
        Python::with_gil(|py| {
            let bound = self_.bind(py);
            if let Ok(tool_invoker) = bound.getattr("tool_invoker") {
                let json = py.import("json")?;
                let inputs_str: String = json.call_method1("dumps", (inputs,))?.extract()?;

                let result = tool_invoker.call_method1("invoke", (action_name, inputs_str))?;
                Ok(result.into())
            } else {
                Ok(py.None())
            }
        })
    }
}

/// Message stored in the pending queue for Python processing
#[derive(Clone)]
pub struct PendingMessage {
    pub payload: String,
    pub sender: String,
    pub topic: String,
}

/// Thread-safe message queue for Python agent callbacks
pub type MessageQueue = Arc<Mutex<VecDeque<PendingMessage>>>;

/// Wrapper to adapt Python Agents to Rust Agent trait.
/// Uses a message queue pattern to avoid calling Python from Tokio worker threads.
pub struct PythonAgentWrapper {
    pub agent: Py<PyAgent>,
    pub pending_messages: MessageQueue,
    pub agent_name: String,
}

impl PythonAgentWrapper {
    pub fn new(agent: Py<PyAgent>, pending_messages: MessageQueue) -> Self {
        // Get agent name on construction (happens on Python main thread)
        let agent_name = Python::with_gil(|py| {
            let bound = agent.bind(py);
            if let Ok(name) = bound.call_method0("name") {
                name.extract().unwrap_or_else(|_| "unknown".to_string())
            } else {
                "unknown".to_string()
            }
        });
        
        PythonAgentWrapper {
            agent,
            pending_messages,
            agent_name,
        }
    }
}

#[async_trait::async_trait]
impl Agent for PythonAgentWrapper {
    fn name(&self) -> String {
        self.agent_name.clone()
    }

    async fn on_start(&mut self, _ctx: &mut AgentContext) -> runtime::core::error::Result<()> {
        // on_start is called during add_agent which happens on Python main thread
        // so we can safely call Python here
        Python::with_gil(|py| {
            let agent = self.agent.bind(py);
            if agent.hasattr("on_start")? {
                agent.call_method1("on_start", (py.None(),))?;
            }
            Ok(())
        })
        .map_err(|e: PyErr| runtime::core::error::Error::MeshError(e.to_string()))
    }

    async fn on_message(
        &mut self,
        msg: Message,
        _ctx: &mut AgentContext,
    ) -> runtime::core::error::Result<()> {
        // CRITICAL: This runs on a Tokio worker thread, NOT the Python main thread.
        // We cannot call Python directly here. Instead, queue the message for
        // later processing by Python on its main thread.
        let pending = PendingMessage {
            payload: String::from_utf8_lossy(&msg.payload).to_string(),
            sender: msg.sender.clone(),
            topic: msg.topic.clone(),
        };
        
        if let Ok(mut queue) = self.pending_messages.lock() {
            queue.push_back(pending);
        }
        
        Ok(())
    }

    async fn on_stop(&mut self, _ctx: &mut AgentContext) -> runtime::core::error::Result<()> {
        // on_stop may be called from worker thread, so we skip Python callback here
        // If needed, Python code should call a cleanup method explicitly
        Ok(())
    }
}

/// Python-callable processor for queued agent messages.
/// Python code calls process_pending() to drain the queue and invoke callbacks.
#[pyclass]
pub struct PyAgentMessageProcessor {
    pending_messages: MessageQueue,
    agent: Py<PyAgent>,
    #[pyo3(get)]
    agent_name: String,
}

#[pymethods]
impl PyAgentMessageProcessor {
    /// Process all pending messages, calling on_message for each.
    /// Returns the number of messages processed.
    /// This must be called from the Python main thread.
    fn process_pending(&self) -> PyResult<usize> {
        Python::with_gil(|py| {
            let mut messages_to_process = Vec::new();
            
            // Drain the queue while holding the lock briefly
            if let Ok(mut queue) = self.pending_messages.lock() {
                while let Some(msg) = queue.pop_front() {
                    messages_to_process.push(msg);
                }
            }
            
            let count = messages_to_process.len();
            let agent = self.agent.bind(py);
            
            // Process messages outside the lock
            for msg in messages_to_process {
                if agent.hasattr("on_message")? {
                    let result = agent.call_method1("on_message", (msg.payload, py.None()))?;
                    
                    // Handle async on_message methods
                    let asyncio = py.import("asyncio")?;
                    let is_coroutine = asyncio
                        .call_method1("iscoroutine", (result.clone(),))?
                        .extract::<bool>()?;
                    
                    if is_coroutine {
                        // Check if an event loop is already running
                        match asyncio.call_method0("get_running_loop") {
                            Ok(loop_obj) => {
                                // Loop running (e.g. pytest-asyncio, or main async loop)
                                // Schedule the coroutine as a task so it runs when the loop yields
                                let _ = loop_obj.call_method1("create_task", (result,));
                            },
                            Err(_) => {
                                // No loop running, run synchronously
                                let new_loop = asyncio.call_method0("new_event_loop")?;
                                asyncio.call_method1("set_event_loop", (new_loop.clone(),))?;
                                let _ = new_loop.call_method1("run_until_complete", (result,));
                                new_loop.call_method0("close")?;
                            }
                        }
                    }
                }
            }
            
            Ok(count)
        })
    }
    
    /// Check how many messages are pending
    fn pending_count(&self) -> usize {
        self.pending_messages
            .lock()
            .map(|q| q.len())
            .unwrap_or(0)
    }
    
    /// Check if there are any pending messages
    fn has_pending(&self) -> bool {
        self.pending_count() > 0
    }
}

impl PyAgentMessageProcessor {
    pub fn new(agent: Py<PyAgent>, pending_messages: MessageQueue, agent_name: String) -> Self {
        PyAgentMessageProcessor {
            pending_messages,
            agent,
            agent_name,
        }
    }
}

/// Python wrapper for AgentContext
#[pyclass]
#[derive(Clone)]
pub struct PyAgentContext {
    #[pyo3(get)]
    pub mesh_name: String,
}

#[pymethods]
impl PyAgentContext {
    #[new]
    fn new(mesh_name: String) -> Self {
        PyAgentContext { mesh_name }
    }
}

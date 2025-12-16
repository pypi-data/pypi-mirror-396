use pyo3::prelude::*;
use runtime::core::message::Message;
use runtime::core::mesh::Mesh;
use runtime::LocalMesh;
use distributed::DistributedMesh;
use std::sync::Arc;
use std::collections::VecDeque;
use std::sync::Mutex;
use crate::runtime::RUNTIME;
use crate::agent::{PythonAgentWrapper, PyAgentMessageProcessor};
use crate::registry::PyInMemoryRegistry;
use crate::llm::{LlmAgentWrapper, PyLlmAgent};

/// Python wrapper for LocalMesh
#[pyclass(subclass)]
pub struct PyLocalMesh {
    pub inner: Arc<LocalMesh>,
}

#[pymethods]
impl PyLocalMesh {
    #[new]
    fn new(name: String) -> Self {
        PyLocalMesh {
            inner: Arc::new(LocalMesh::new(name)),
        }
    }

    fn start(&self, py: Python<'_>) -> PyResult<()> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.start()
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Add an agent to the mesh and return a message processor.
    /// The returned processor must be used to process pending messages
    /// by calling processor.process_pending() periodically.
    fn add_agent(&self, py: Python<'_>, agent: Py<crate::agent::PyAgent>) -> PyResult<PyAgentMessageProcessor> {
        let mesh = self.inner.clone();
        
        // Create shared message queue
        let pending_messages = Arc::new(Mutex::new(VecDeque::new()));
        
        // Get agent name before moving agent
        let agent_name = {
            let bound = agent.bind(py);
            if let Ok(name) = bound.call_method0("name") {
                name.extract().unwrap_or_else(|_| "unknown".to_string())
            } else {
                "unknown".to_string()
            }
        };
        
        // Create the processor that Python will use
        let processor = PyAgentMessageProcessor::new(
            agent.clone_ref(py),
            pending_messages.clone(),
            agent_name,
        );
        
        // Create agent wrapper with shared queue
        let agent_wrapper = Box::new(PythonAgentWrapper::new(agent, pending_messages));

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.add_agent(agent_wrapper)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })?;
        
        Ok(processor)
    }

    /// Add an LlmAgent directly to the mesh.
    /// The agent must be built before calling this method.
    /// Returns the agent name for reference.
    fn add_llm_agent(&self, py: Python<'_>, agent: &PyLlmAgent) -> PyResult<String> {
        let mesh = self.inner.clone();
        
        // Get the inner Arc and name from the PyLlmAgent
        let (inner, name) = agent.get_inner_for_mesh()?;
        let agent_name = name.clone();
        
        // Create the LlmAgentWrapper
        let agent_wrapper = Box::new(LlmAgentWrapper::new(inner, name));

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.add_agent(agent_wrapper)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })?;
        
        Ok(agent_name)
    }

    fn send_to(&self, py: Python<'_>, target: String, payload: String) -> PyResult<()> {
        let mesh = self.inner.clone();
        let msg = Message::new("system", payload.into_bytes(), target.clone());

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.send(msg, &target)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    #[pyo3(signature = (payload, exclude=None))]
    fn broadcast(&self, py: Python<'_>, payload: String, exclude: Option<String>) -> PyResult<()> {
        let mesh = self.inner.clone();
        let msg = Message::new("system", payload.into_bytes(), "broadcast".to_string());

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                let exclude_ref = exclude.as_deref();
                let results = mesh.broadcast(msg, exclude_ref)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                
                // Check if any broadcasts failed
                for result in results {
                    if let Err(e) = result {
                        eprintln!("Broadcast error: {}", e);
                    }
                }
                
                Ok(())
            })
        })
    }

    /// Submit a request (fire-and-forget). Returns request ID.
    fn submit(&self, py: Python<'_>, target: String, payload: String) -> PyResult<String> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.submit(&target, payload)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Get pending requests
    fn get_pending(&self) -> Vec<PyMeshRequest> {
        self.inner.get_pending()
            .into_iter()
            .map(|r| PyMeshRequest::from(r))
            .collect()
    }

    /// Check if there are pending requests
    fn has_pending(&self) -> bool {
        self.inner.has_pending()
    }

    /// Get available results (removes them from queue)
    fn get_results(&self) -> Vec<PyMeshResult> {
        self.inner.get_results()
            .into_iter()
            .map(|r| PyMeshResult::from(r))
            .collect()
    }

    /// Peek at results without removing
    fn peek_results(&self) -> Vec<PyMeshResult> {
        self.inner.peek_results()
            .into_iter()
            .map(|r| PyMeshResult::from(r))
            .collect()
    }

    /// Send reminders for stale requests
    #[pyo3(signature = (older_than_secs=30.0))]
    fn send_reminders(&self, py: Python<'_>, older_than_secs: f64) -> PyResult<Vec<String>> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.send_reminders(older_than_secs)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Wait for a specific result with auto-reminders
    #[pyo3(signature = (request_id, timeout=60.0, reminder_interval=30.0))]
    fn wait_for(&self, py: Python<'_>, request_id: String, timeout: f64, reminder_interval: f64) -> PyResult<PyMeshResult> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.wait_for(&request_id, timeout, reminder_interval)
                    .await
                    .map(PyMeshResult::from)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Collect all results, blocking until all pending complete
    #[pyo3(signature = (reminder_interval=30.0))]
    fn collect_results(&self, py: Python<'_>, reminder_interval: f64) -> Vec<PyMeshResult> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.collect_results(reminder_interval)
                    .await
                    .into_iter()
                    .map(PyMeshResult::from)
                    .collect()
            })
        })
    }
}

/// Python wrapper for MeshRequest
#[pyclass]
#[derive(Clone)]
pub struct PyMeshRequest {
    #[pyo3(get)]
    pub id: String,
    #[pyo3(get)]
    pub target: String,
    #[pyo3(get)]
    pub payload: String,
    #[pyo3(get)]
    pub elapsed_seconds: f64,
    #[pyo3(get)]
    pub reminder_count: u32,
}

impl From<runtime::core::request_queue::MeshRequest> for PyMeshRequest {
    fn from(req: runtime::core::request_queue::MeshRequest) -> Self {
        let elapsed_seconds = req.elapsed_seconds();
        PyMeshRequest {
            id: req.id,
            target: req.target,
            payload: req.payload,
            elapsed_seconds,
            reminder_count: req.reminder_count,
        }
    }
}

#[pymethods]
impl PyMeshRequest {
    fn __repr__(&self) -> String {
        format!("MeshRequest(id='{}', target='{}', elapsed={:.1}s)", self.id, self.target, self.elapsed_seconds)
    }
}

/// Python wrapper for MeshResult
#[pyclass]
#[derive(Clone)]
pub struct PyMeshResult {
    #[pyo3(get)]
    pub request_id: String,
    #[pyo3(get)]
    pub target: String,
    #[pyo3(get)]
    pub response: String,
    #[pyo3(get)]
    pub duration_ms: u64,
}

impl From<runtime::core::request_queue::MeshResult> for PyMeshResult {
    fn from(res: runtime::core::request_queue::MeshResult) -> Self {
        PyMeshResult {
            request_id: res.request_id,
            target: res.target,
            response: res.response,
            duration_ms: res.duration_ms,
        }
    }
}

#[pymethods]
impl PyMeshResult {
    fn __repr__(&self) -> String {
        format!("MeshResult(request_id='{}', duration={}ms)", self.request_id, self.duration_ms)
    }
}


/// Python wrapper for DistributedMesh
#[pyclass(subclass)]
pub struct PyDistributedMesh {
    pub inner: Arc<DistributedMesh>,
}

#[pymethods]
impl PyDistributedMesh {
    #[new]
    fn new(name: String, port: u16) -> Self {
        PyDistributedMesh {
            inner: Arc::new(DistributedMesh::new(name, port)),
        }
    }

    fn start(&self, py: Python<'_>) -> PyResult<()> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.start()
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    fn stop(&self, py: Python<'_>) -> PyResult<()> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.stop()
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Add an agent to the mesh and return a message processor.
    /// The returned processor must be used to process pending messages
    /// by calling processor.process_pending() periodically.
    fn add_agent(&self, py: Python<'_>, agent: Py<crate::agent::PyAgent>) -> PyResult<PyAgentMessageProcessor> {
        let mesh = self.inner.clone();
        
        // Create shared message queue
        let pending_messages = Arc::new(Mutex::new(VecDeque::new()));
        
        // Get agent name before moving agent
        let agent_name = {
            let bound = agent.bind(py);
            if let Ok(name) = bound.call_method0("name") {
                name.extract().unwrap_or_else(|_| "unknown".to_string())
            } else {
                "unknown".to_string()
            }
        };
        
        // Create the processor that Python will use
        let processor = PyAgentMessageProcessor::new(
            agent.clone_ref(py),
            pending_messages.clone(),
            agent_name,
        );
        
        // Create agent wrapper with shared queue
        let agent_wrapper = Box::new(PythonAgentWrapper::new(agent, pending_messages));

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.add_agent(agent_wrapper)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })?;
        
        Ok(processor)
    }

    /// Add an LlmAgent directly to the mesh.
    /// The agent must be built before calling this method.
    /// Returns the agent name for reference.
    fn add_llm_agent(&self, py: Python<'_>, agent: &PyLlmAgent) -> PyResult<String> {
        let mesh = self.inner.clone();
        
        // Get the inner Arc and name from the PyLlmAgent
        let (inner, name) = agent.get_inner_for_mesh()?;
        let agent_name = name.clone();
        
        // Create the LlmAgentWrapper
        let agent_wrapper = Box::new(LlmAgentWrapper::new(inner, name));

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.add_agent(agent_wrapper)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })?;
        
        Ok(agent_name)
    }

    fn connect_peer(&self, py: Python<'_>, agent_name: String, url: String) -> PyResult<()> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.connect_peer(agent_name, url).await;
                Ok(())
            })
        })
    }

    fn send_to(&self, py: Python<'_>, target: String, payload: String) -> PyResult<()> {
        let mesh = self.inner.clone();
        let msg = Message::new("system", payload.into_bytes(), target.clone());

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.send(msg, &target)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    #[pyo3(signature = (payload, exclude=None))]
    fn broadcast(&self, py: Python<'_>, payload: String, exclude: Option<String>) -> PyResult<()> {
        let mesh = self.inner.clone();
        let msg = Message::new("system", payload.into_bytes(), "broadcast".to_string());

        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                let exclude_ref = exclude.as_deref();
                let results = mesh.broadcast(msg, exclude_ref)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
                
                // Check if any broadcasts failed
                for result in results {
                    if let Err(e) = result {
                        eprintln!("Broadcast error: {}", e);
                    }
                }
                
                Ok(())
            })
        })
    }

    /// Submit a request (fire-and-forget). Returns request ID.
    fn submit(&self, py: Python<'_>, target: String, payload: String) -> PyResult<String> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.submit(&target, payload)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Get pending requests
    fn get_pending(&self) -> Vec<PyMeshRequest> {
        self.inner.get_pending()
            .into_iter()
            .map(|r| PyMeshRequest::from(r))
            .collect()
    }

    /// Check if there are pending requests
    fn has_pending(&self) -> bool {
        self.inner.has_pending()
    }

    /// Get available results (removes them from queue)
    fn get_results(&self) -> Vec<PyMeshResult> {
        self.inner.get_results()
            .into_iter()
            .map(|r| PyMeshResult::from(r))
            .collect()
    }

    /// Peek at results without removing
    fn peek_results(&self) -> Vec<PyMeshResult> {
        self.inner.peek_results()
            .into_iter()
            .map(|r| PyMeshResult::from(r))
            .collect()
    }

    /// Send reminders for stale requests
    #[pyo3(signature = (older_than_secs=30.0))]
    fn send_reminders(&self, py: Python<'_>, older_than_secs: f64) -> PyResult<Vec<String>> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.send_reminders(older_than_secs)
                    .await
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Wait for a specific result with auto-reminders
    #[pyo3(signature = (request_id, timeout=60.0, reminder_interval=30.0))]
    fn wait_for(&self, py: Python<'_>, request_id: String, timeout: f64, reminder_interval: f64) -> PyResult<PyMeshResult> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.wait_for(&request_id, timeout, reminder_interval)
                    .await
                    .map(PyMeshResult::from)
                    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
            })
        })
    }

    /// Collect all results, blocking until all pending complete
    #[pyo3(signature = (reminder_interval=30.0))]
    fn collect_results(&self, py: Python<'_>, reminder_interval: f64) -> Vec<PyMeshResult> {
        let mesh = self.inner.clone();
        py.allow_threads(|| {
            RUNTIME.block_on(async move {
                mesh.collect_results(reminder_interval)
                    .await
                    .into_iter()
                    .map(PyMeshResult::from)
                    .collect()
            })
        })
    }

    #[staticmethod]
    fn with_registry(name: String, port: u16, registry: &PyInMemoryRegistry) -> Self {
        let reg = registry.inner.clone();
        PyDistributedMesh {
            inner: Arc::new(DistributedMesh::with_registry(name, port, reg)),
        }
    }
}



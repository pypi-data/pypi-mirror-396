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

    #[staticmethod]
    fn with_registry(name: String, port: u16, registry: &PyInMemoryRegistry) -> Self {
        let reg = registry.inner.clone();
        PyDistributedMesh {
            inner: Arc::new(DistributedMesh::with_registry(name, port, reg)),
        }
    }
}



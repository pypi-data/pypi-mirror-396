use tokio::runtime::Runtime;

// Create a multi-threaded Tokio runtime for async execution.
//
// NOTE: Python agent callbacks (via PythonAgentWrapper::on_message) may fail
// when using LocalMesh with Python Agent subclasses because tokio::spawn runs
// tasks on worker threads that don't have Python interpreter attached.
//
// For Python agents, use the LlmAgent-based approach which handles threading
// correctly, or use async Python code (demo_async_agent.py) which avoids the
// mesh's internal tokio::spawn by using Python's own async loop.
lazy_static::lazy_static! {
    pub static ref RUNTIME: Runtime = Runtime::new().unwrap();
}

use crate::core::error::Result;
use crate::core::message::Message;
use crate::core::request_queue::RequestQueue;
use async_trait::async_trait;
use std::sync::Arc;

#[async_trait]
pub trait Agent: Send + Sync {
    fn name(&self) -> String;
    async fn on_start(&mut self, _ctx: &mut AgentContext) -> Result<()> {
        Ok(())
    }
    async fn on_message(&mut self, _msg: Message, _ctx: &mut AgentContext) -> Result<()> {
        // Default implementation does nothing
        Ok(())
    }

    /// Handle a generic string message and return a generic response.
    /// Default implementation returns an echo response.
    async fn on_generic_message(
        &mut self,
        msg: crate::core::message::GenericMessage,
        _ctx: &mut AgentContext,
    ) -> Result<crate::core::message::GenericResponse> {
        // Simple default: echo the content back
        Ok(crate::core::message::GenericResponse::new(msg.content))
    }
    async fn on_stop(&mut self, _ctx: &mut AgentContext) -> Result<()> {
        Ok(())
    }

    /// Get the tool invoker for this agent (if it has actions)
    fn tool_invoker(&self) -> Option<&crate::core::action::ToolInvoker> {
        None // Default: no actions
    }

    /// Get mutable tool invoker for registration
    fn tool_invoker_mut(&mut self) -> Option<&mut crate::core::action::ToolInvoker> {
        None
    }
}

pub struct AgentContext {
    pub mesh_name: String,
    request_queue: Option<Arc<RequestQueue>>,
}

impl AgentContext {
    /// Create context without request queue (for standalone use)
    pub fn new(mesh_name: String, request_queue: Option<Arc<RequestQueue>>) -> Self {
        Self {
            mesh_name,
            request_queue,
        }
    }

    /// Report a result for a request (used by agents to send responses back)
    pub fn report_result(&self, request_id: &str, response: String) {
        if let Some(queue) = &self.request_queue {
            queue.complete(request_id, response);
        }
    }

    /// Check if this context has a request queue
    pub fn has_request_queue(&self) -> bool {
        self.request_queue.is_some()
    }
}

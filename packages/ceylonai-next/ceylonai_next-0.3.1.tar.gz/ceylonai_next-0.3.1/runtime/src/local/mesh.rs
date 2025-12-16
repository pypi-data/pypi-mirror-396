use crate::core::agent::{Agent, AgentContext};
use crate::core::error::{Error, Result};
use crate::core::mesh::Mesh;
use crate::core::message::Message;
use crate::core::request_queue::{MeshRequest, MeshResult, RequestQueue};
use async_trait::async_trait;
use dashmap::DashMap;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::mpsc::{self, Sender};
use tokio::task::JoinHandle;

pub struct LocalMesh {
    name: String,
    agents: DashMap<String, Sender<Message>>,
    tasks: DashMap<String, JoinHandle<()>>,
    request_queue: Arc<RequestQueue>,
}

impl LocalMesh {
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            agents: DashMap::new(),
            tasks: DashMap::new(),
            request_queue: Arc::new(RequestQueue::new()),
        }
    }

    /// Get the request queue (for sharing with agent wrappers)
    pub fn request_queue(&self) -> Arc<RequestQueue> {
        self.request_queue.clone()
    }
}

#[async_trait]
impl Mesh for LocalMesh {
    async fn start(&self) -> Result<()> {
        // For local mesh, start might just be a signal,
        // but agents are started when added for now.
        Ok(())
    }

    async fn stop(&self) -> Result<()> {
        for entry in self.tasks.iter() {
            entry.value().abort();
        }
        self.tasks.clear();
        self.agents.clear();
        Ok(())
    }

    async fn add_agent(&self, mut agent: Box<dyn Agent + 'static>) -> Result<()> {
        let name = agent.name();
        if self.agents.contains_key(&name) {
            return Err(Error::MeshError(format!("Agent {} already exists", name)));
        }

        let (tx, mut rx) = mpsc::channel(100);
        self.agents.insert(name.clone(), tx);

        let mesh_name = self.name.clone();
        let agent_name = name.clone();
        let request_queue = self.request_queue.clone();

        // Spawn agent loop
        let handle = tokio::spawn(async move {
            let mut ctx = AgentContext::new(mesh_name, Some(request_queue));
            if let Err(e) = agent.on_start(&mut ctx).await {
                eprintln!("Error starting agent {}: {:?}", agent_name, e);
                return;
            }

            while let Some(msg) = rx.recv().await {
                let now = chrono::Utc::now().timestamp_micros();
                let latency = (now - msg.created_at).max(0) as u64;
                crate::metrics::metrics().record_message(latency);

                let start = std::time::Instant::now();
                if let Err(e) = agent.on_message(msg, &mut ctx).await {
                    eprintln!("Error processing message in agent {}: {:?}", agent_name, e);
                    crate::metrics::metrics().record_error("agent_message_error");
                }
                let duration = start.elapsed().as_micros() as u64;
                crate::metrics::metrics().record_agent_execution(duration);
            }

            if let Err(e) = agent.on_stop(&mut ctx).await {
                eprintln!("Error stopping agent {}: {:?}", agent_name, e);
            }
        });

        self.tasks.insert(name, handle);
        Ok(())
    }

    async fn send(&self, message: Message, target: &str) -> Result<()> {
        if let Some(sender) = self.agents.get(target) {
            sender
                .send(message)
                .await
                .map_err(|_| Error::MeshError(format!("Failed to send to agent {}", target)))?;
            Ok(())
        } else {
            Err(Error::AgentNotFound(target.to_string()))
        }
    }
}

impl LocalMesh {
    /// Broadcast a message to all agents in the mesh
    pub async fn broadcast(
        &self,
        message: Message,
        exclude: Option<&str>,
    ) -> Result<Vec<Result<()>>> {
        let mut results = Vec::new();

        for entry in self.agents.iter() {
            let agent_name = entry.key();

            // Skip excluded agent if specified
            if let Some(excluded) = exclude {
                if agent_name == excluded {
                    continue;
                }
            }

            // Clone message for each agent
            let msg = Message::new(
                message.sender.clone(),
                message.payload.clone(),
                agent_name.clone(),
            );

            let result = entry.value().send(msg).await.map_err(|_| {
                Error::MeshError(format!("Failed to broadcast to agent {}", agent_name))
            });

            results.push(result);
        }

        Ok(results)
    }

    /// Submit a request (fire-and-forget). Returns request ID.
    pub async fn submit(&self, target: &str, payload: String) -> Result<String> {
        let request_id = self.request_queue.submit(target, payload.clone());

        let mut msg = Message::new("request", payload.into_bytes(), target);
        msg.set_correlation_id(&request_id);

        self.send(msg, target).await?;
        Ok(request_id)
    }

    /// Get pending requests
    pub fn get_pending(&self) -> Vec<MeshRequest> {
        self.request_queue.get_pending()
    }

    /// Check if there are pending requests
    pub fn has_pending(&self) -> bool {
        self.request_queue.has_pending()
    }

    /// Get available results (removes them from queue)
    pub fn get_results(&self) -> Vec<MeshResult> {
        self.request_queue.take_results()
    }

    /// Peek at results without removing
    pub fn peek_results(&self) -> Vec<MeshResult> {
        self.request_queue.peek_results()
    }

    /// Send reminders for stale requests
    pub async fn send_reminders(&self, older_than_secs: f64) -> Result<Vec<String>> {
        let stale = self
            .request_queue
            .get_stale(Duration::from_secs_f64(older_than_secs));
        let mut reminded = Vec::new();

        for req in stale {
            let mut reminder_msg = Message::new(
                "reminder",
                format!("REMINDER: Please complete request {}", req.id).into_bytes(),
                &req.target,
            );
            reminder_msg.set_correlation_id(&req.id);

            if self.send(reminder_msg, &req.target).await.is_ok() {
                self.request_queue.increment_reminder(&req.id);
                reminded.push(req.id);
            }
        }

        Ok(reminded)
    }

    /// Wait for a specific result with auto-reminders
    pub async fn wait_for(
        &self,
        request_id: &str,
        timeout_secs: f64,
        reminder_interval_secs: f64,
    ) -> Result<MeshResult> {
        let timeout = Duration::from_secs_f64(timeout_secs);
        let reminder_interval = Duration::from_secs_f64(reminder_interval_secs);
        let deadline = std::time::Instant::now() + timeout;
        let mut last_reminder = std::time::Instant::now();

        loop {
            // Check if result is available
            if let Some(result) = self.request_queue.take_result(request_id) {
                return Ok(result);
            }

            // Check if request still exists
            let pending = self.request_queue.get_pending();
            let request = pending.iter().find(|r| r.id == request_id);
            if request.is_none() {
                return Err(Error::MeshError(format!(
                    "Request {} not found",
                    request_id
                )));
            }

            // Check timeout
            if std::time::Instant::now() >= deadline {
                return Err(Error::MeshError(format!(
                    "Request {} timed out",
                    request_id
                )));
            }

            // Send reminder if interval passed
            if last_reminder.elapsed() >= reminder_interval {
                let _ = self.send_reminders(reminder_interval_secs).await;
                last_reminder = std::time::Instant::now();
            }

            // Wait briefly
            tokio::time::sleep(Duration::from_millis(100)).await;
        }
    }

    /// Collect all results, blocking until all pending complete
    pub async fn collect_results(&self, reminder_interval_secs: f64) -> Vec<MeshResult> {
        let reminder_interval = Duration::from_secs_f64(reminder_interval_secs);
        let mut last_reminder = std::time::Instant::now();
        let mut all_results = Vec::new();

        while self.request_queue.has_pending() {
            // Collect any available results
            let results = self.request_queue.take_results();
            all_results.extend(results);

            // Send reminders if interval passed
            if last_reminder.elapsed() >= reminder_interval {
                let _ = self.send_reminders(reminder_interval_secs).await;
                last_reminder = std::time::Instant::now();
            }

            // Wait briefly before checking again
            tokio::time::sleep(Duration::from_millis(100)).await;
        }

        // Get any final results
        let results = self.request_queue.take_results();
        all_results.extend(results);

        all_results
    }
}

use crate::ceylon::mesh_service_server::MeshServiceServer;
use crate::service::GrpcMeshService;
use async_trait::async_trait;
use runtime::core::error::Result;
use runtime::{Agent, LocalMesh, Mesh, Message};
use std::sync::Arc;
use tonic::transport::Server;

use crate::ceylon::mesh_service_client::MeshServiceClient;
use crate::ceylon::Envelope;
use crate::registry::{AgentMetadata, HealthStatus, InMemoryRegistry, Registry};
use std::collections::HashMap;
use tokio::sync::RwLock;

pub struct DistributedMesh {
    local_mesh: Arc<LocalMesh>,
    port: u16,
    // Map of agent_name -> node_url
    peers: Arc<RwLock<HashMap<String, String>>>,
    registry: Arc<dyn Registry + Send + Sync>,
}

impl DistributedMesh {
    pub fn new(name: impl Into<String>, port: u16) -> Self {
        Self {
            local_mesh: Arc::new(LocalMesh::new(name)),
            port,
            peers: Arc::new(RwLock::new(HashMap::new())),
            registry: Arc::new(InMemoryRegistry::new()),
        }
    }

    pub fn with_registry(
        name: impl Into<String>,
        port: u16,
        registry: Arc<dyn Registry + Send + Sync>,
    ) -> Self {
        Self {
            local_mesh: Arc::new(LocalMesh::new(name)),
            port,
            peers: Arc::new(RwLock::new(HashMap::new())),
            registry,
        }
    }

    pub async fn connect_peer(&self, agent_name: String, url: String) {
        let mut peers = self.peers.write().await;
        peers.insert(agent_name, url);
    }
}

#[async_trait]
impl Mesh for DistributedMesh {
    async fn start(&self) -> Result<()> {
        self.local_mesh.start().await?;

        let addr = format!("0.0.0.0:{}", self.port).parse().map_err(|e| {
            runtime::core::error::Error::MeshError(format!("Invalid address: {}", e))
        })?;
        let service = GrpcMeshService::new(self.local_mesh.clone());

        println!("Starting DistributedMesh on port {}", self.port);

        tokio::spawn(async move {
            if let Err(e) = Server::builder()
                .add_service(MeshServiceServer::new(service))
                .serve(addr)
                .await
            {
                eprintln!("gRPC server error: {}", e);
            }
        });

        Ok(())
    }

    async fn stop(&self) -> Result<()> {
        self.local_mesh.stop().await
    }

    async fn add_agent(&self, agent: Box<dyn Agent + 'static>) -> Result<()> {
        let name = agent.name();
        self.local_mesh.add_agent(agent).await?;

        // Register in the registry
        let metadata = AgentMetadata {
            id: name.clone(),
            name: name,
            address: format!("http://127.0.0.1:{}", self.port),
            capabilities: vec![], // TODO: Extract capabilities from agent
            health_status: HealthStatus::Healthy,
            last_heartbeat: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
        };

        self.registry.register(metadata).await?;
        Ok(())
    }

    async fn send(&self, message: Message, target: &str) -> Result<()> {
        // Check if target is local
        // We don't have a direct way to check if agent is local in LocalMesh public API easily
        // without trying to send or checking registry.
        // But LocalMesh.send will fail if agent not found.

        // Let's check our peers map first.
        let peer_url = {
            let peers = self.peers.read().await;
            if let Some(url) = peers.get(target) {
                Some(url.clone())
            } else {
                // Check registry
                if let Ok(Some(metadata)) = self.registry.get_agent(target).await {
                    Some(metadata.address)
                } else {
                    None
                }
            }
        };

        if let Some(url) = peer_url {
            // It's a remote agent
            // TODO: Cache clients
            let mut client = MeshServiceClient::connect(url).await.map_err(|e| {
                runtime::core::error::Error::MeshError(format!("Failed to connect to peer: {}", e))
            })?;

            let proto_msg: crate::ceylon::Message = message.into();
            let envelope = Envelope {
                message: Some(proto_msg),
                target_agent: Some(target.to_string()),
                target_node: None,
            };

            let _ = client
                .send(tonic::Request::new(envelope))
                .await
                .map_err(|e| {
                    runtime::core::error::Error::MeshError(format!("Failed to send to peer: {}", e))
                })?;

            Ok(())
        } else {
            // Try local
            self.local_mesh.send(message, target).await
        }
    }
}

impl DistributedMesh {
    /// Broadcast a message to all agents in the mesh (local and remote)
    pub async fn broadcast(
        &self,
        message: Message,
        exclude: Option<&str>,
    ) -> Result<Vec<Result<()>>> {
        // Broadcast to local agents first
        let local_results = self.local_mesh.broadcast(message.clone(), exclude).await?;

        // TODO: Broadcast to remote agents via registry
        // For now, only broadcasting to local agents

        Ok(local_results)
    }

    /// Submit a request (fire-and-forget). Returns request ID.
    pub async fn submit(&self, target: &str, payload: String) -> Result<String> {
        self.local_mesh.submit(target, payload).await
    }

    /// Get pending requests
    pub fn get_pending(&self) -> Vec<runtime::core::request_queue::MeshRequest> {
        self.local_mesh.get_pending()
    }

    /// Check if there are pending requests
    pub fn has_pending(&self) -> bool {
        self.local_mesh.has_pending()
    }

    /// Get available results (removes them from queue)
    pub fn get_results(&self) -> Vec<runtime::core::request_queue::MeshResult> {
        self.local_mesh.get_results()
    }

    /// Peek at results without removing
    pub fn peek_results(&self) -> Vec<runtime::core::request_queue::MeshResult> {
        self.local_mesh.peek_results()
    }

    /// Send reminders for stale requests
    pub async fn send_reminders(&self, older_than_secs: f64) -> Result<Vec<String>> {
        self.local_mesh.send_reminders(older_than_secs).await
    }

    /// Wait for a specific result with auto-reminders
    pub async fn wait_for(
        &self,
        request_id: &str,
        timeout_secs: f64,
        reminder_interval_secs: f64,
    ) -> Result<runtime::core::request_queue::MeshResult> {
        self.local_mesh
            .wait_for(request_id, timeout_secs, reminder_interval_secs)
            .await
    }

    /// Collect all results, blocking until all pending complete
    pub async fn collect_results(
        &self,
        reminder_interval_secs: f64,
    ) -> Vec<runtime::core::request_queue::MeshResult> {
        self.local_mesh
            .collect_results(reminder_interval_secs)
            .await
    }
}

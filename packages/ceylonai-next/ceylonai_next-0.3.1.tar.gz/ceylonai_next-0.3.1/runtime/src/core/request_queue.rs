use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use std::sync::Mutex;
use std::time::{Duration, Instant};
use tokio::sync::Notify;
use uuid::Uuid;

/// Status of a mesh request
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum RequestStatus {
    Pending,
    Completed,
    Failed(String),
    TimedOut,
}

/// A request submitted to the mesh
#[derive(Debug, Clone)]
pub struct MeshRequest {
    pub id: String,
    pub target: String,
    pub payload: String,
    pub submitted_at: Instant,
    pub status: RequestStatus,
    pub reminder_count: u32,
}

impl MeshRequest {
    pub fn new(target: impl Into<String>, payload: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            target: target.into(),
            payload: payload.into(),
            submitted_at: Instant::now(),
            status: RequestStatus::Pending,
            reminder_count: 0,
        }
    }

    /// Get elapsed time since submission in seconds
    pub fn elapsed_seconds(&self) -> f64 {
        self.submitted_at.elapsed().as_secs_f64()
    }
}

/// A result from processing a mesh request
#[derive(Debug, Clone)]
pub struct MeshResult {
    pub request_id: String,
    pub target: String,
    pub response: String,
    pub completed_at: Instant,
    pub duration_ms: u64,
}

impl MeshResult {
    pub fn new(
        request_id: impl Into<String>,
        target: impl Into<String>,
        response: impl Into<String>,
        duration_ms: u64,
    ) -> Self {
        Self {
            request_id: request_id.into(),
            target: target.into(),
            response: response.into(),
            completed_at: Instant::now(),
            duration_ms,
        }
    }
}

/// Manages pending requests and completed results for a mesh
pub struct RequestQueue {
    pending: DashMap<String, MeshRequest>,
    results: Mutex<VecDeque<MeshResult>>,
    result_notify: Notify,
    max_results: usize,
}

impl Default for RequestQueue {
    fn default() -> Self {
        Self::new()
    }
}

impl RequestQueue {
    /// Create a new request queue
    pub fn new() -> Self {
        Self::with_max_results(1000)
    }

    /// Create with a maximum result buffer size
    pub fn with_max_results(max_results: usize) -> Self {
        Self {
            pending: DashMap::new(),
            results: Mutex::new(VecDeque::new()),
            result_notify: Notify::new(),
            max_results,
        }
    }

    /// Submit a new request, returns the request ID
    pub fn submit(&self, target: &str, payload: String) -> String {
        let request = MeshRequest::new(target, payload);
        let id = request.id.clone();
        self.pending.insert(id.clone(), request);
        id
    }

    /// Mark a request as completed with a response
    pub fn complete(&self, request_id: &str, response: String) {
        if let Some((_, request)) = self.pending.remove(request_id) {
            let duration_ms = request.submitted_at.elapsed().as_millis() as u64;
            let result = MeshResult::new(request_id, &request.target, response, duration_ms);

            let mut results = self.results.lock().unwrap();
            results.push_back(result);

            // Enforce max results limit
            while results.len() > self.max_results {
                results.pop_front();
            }

            // Wake up any waiters
            self.result_notify.notify_waiters();
        }
    }

    /// Mark a request as failed
    pub fn fail(&self, request_id: &str, error: String) {
        if let Some(mut entry) = self.pending.get_mut(request_id) {
            entry.status = RequestStatus::Failed(error);
        }
        self.pending.remove(request_id);
        self.result_notify.notify_waiters();
    }

    /// Get all pending requests
    pub fn get_pending(&self) -> Vec<MeshRequest> {
        self.pending.iter().map(|e| e.value().clone()).collect()
    }

    /// Get pending requests older than the specified duration
    pub fn get_stale(&self, older_than: Duration) -> Vec<MeshRequest> {
        self.pending
            .iter()
            .filter(|e| e.value().submitted_at.elapsed() > older_than)
            .map(|e| e.value().clone())
            .collect()
    }

    /// Check if there are any pending requests
    pub fn has_pending(&self) -> bool {
        !self.pending.is_empty()
    }

    /// Get number of pending requests
    pub fn pending_count(&self) -> usize {
        self.pending.len()
    }

    /// Increment reminder count for a request
    pub fn increment_reminder(&self, request_id: &str) {
        if let Some(mut entry) = self.pending.get_mut(request_id) {
            entry.reminder_count += 1;
        }
    }

    /// Get available results (removes them from the queue)
    pub fn take_results(&self) -> Vec<MeshResult> {
        let mut results = self.results.lock().unwrap();
        results.drain(..).collect()
    }

    /// Peek at results without removing them
    pub fn peek_results(&self) -> Vec<MeshResult> {
        let results = self.results.lock().unwrap();
        results.iter().cloned().collect()
    }

    /// Get result for a specific request (removes it if found)
    pub fn take_result(&self, request_id: &str) -> Option<MeshResult> {
        let mut results = self.results.lock().unwrap();
        if let Some(pos) = results.iter().position(|r| r.request_id == request_id) {
            results.remove(pos)
        } else {
            None
        }
    }

    /// Wait for the next result to become available
    pub async fn wait_next(&self, timeout: Duration) -> Option<MeshResult> {
        let deadline = Instant::now() + timeout;

        loop {
            // Check for available results first
            {
                let mut results = self.results.lock().unwrap();
                if let Some(result) = results.pop_front() {
                    return Some(result);
                }
            }

            // No pending requests means nothing to wait for
            if !self.has_pending() {
                return None;
            }

            // Calculate remaining time
            let remaining = deadline.saturating_duration_since(Instant::now());
            if remaining.is_zero() {
                return None; // Timeout
            }

            // Wait for notification or timeout
            let _ = tokio::time::timeout(remaining, self.result_notify.notified()).await;
        }
    }

    /// Wait for a specific result
    pub async fn wait_for(&self, request_id: &str, timeout: Duration) -> Option<MeshResult> {
        let deadline = Instant::now() + timeout;

        loop {
            // Check if result is available
            if let Some(result) = self.take_result(request_id) {
                return Some(result);
            }

            // Check if request is still pending
            if !self.pending.contains_key(request_id) {
                return None; // Request doesn't exist or was removed
            }

            // Calculate remaining time
            let remaining = deadline.saturating_duration_since(Instant::now());
            if remaining.is_zero() {
                return None; // Timeout
            }

            // Wait for notification or timeout
            let _ = tokio::time::timeout(remaining, self.result_notify.notified()).await;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_submit_and_complete() {
        let queue = RequestQueue::new();

        let id = queue.submit("agent1", "hello".to_string());
        assert_eq!(queue.pending_count(), 1);
        assert!(queue.has_pending());

        queue.complete(&id, "world".to_string());
        assert_eq!(queue.pending_count(), 0);
        assert!(!queue.has_pending());

        let results = queue.take_results();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].request_id, id);
        assert_eq!(results[0].response, "world");
    }

    #[test]
    fn test_get_stale() {
        let queue = RequestQueue::new();

        queue.submit("agent1", "msg1".to_string());

        // Immediately, nothing is stale
        let stale = queue.get_stale(Duration::from_secs(1));
        assert!(stale.is_empty());
    }

    #[test]
    fn test_increment_reminder() {
        let queue = RequestQueue::new();

        let id = queue.submit("agent1", "msg".to_string());

        queue.increment_reminder(&id);
        queue.increment_reminder(&id);

        let pending = queue.get_pending();
        assert_eq!(pending[0].reminder_count, 2);
    }
}

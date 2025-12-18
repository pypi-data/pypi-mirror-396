# Agent Memory Hub

**Enterprise-grade agent memory management solution with region governance.**

`agent-memory-hub` provides a standardized, secure, and compliant way for AI agents to store and recall memories. It enforces region residency requirements (data sovereignty) and provides a clean abstraction over storage backends, defaulting to Google Cloud.

## Features

- **Session-based Memory**: Isolate memory by agent and session ID.
- **Region Governance**: Enforce data residency (e.g., `us-central1`, `europe-west1`).
- **Backend Agnostic**: Adapter pattern supports multiple backends (Default: Google ADK/GCS).
- **Enterprise Security**: No hardcoded secrets, strictly typed, and compliance-ready.

## Installation

```bash
pip install agent-memory-hub
```

## Quick Start

```python
from agent_memory_hub import MemoryClient

# Initialize the client with strict region requirements
memory = MemoryClient(
    agent_id="travel_agent",
    session_id="sess_001",
    region="asia-south1",
    region_restricted=True
)

# Store a memory (will fail if backend is not in asia-south1)
memory.write("User prefers vegetarian food", "episodic")

# Recall memory
print(memory.recall("episodic"))
```

## Region Governance

This SDK is designed for global deployments where data sovereignty is critical.
When `region_restricted=True` is set, the SDK performs a handshake with the control plane to verify that the underlying storage is physically located in the requested region before writing any data.

## GCP Prerequisites

By default, this package uses Google Cloud Storage as the backing store.

1. **Authentication**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set or you are authenticated via `gcloud auth application-default login`.
2. **Permissions**: The service account requires `storage.objects.create` and `storage.objects.get` permissions on the target bucket.
3. **Buckets**: Buckets should be named following the convention `memory-hub-{region}-{environment}` (e.g., `memory-hub-asia-south1-prod`).

## Security & Compliance

- **No Secrets**: This library does not handle secrets directly. Use IAM roles.
- **Dependency Pinning**: All dependencies are pinned to secure versions.
- **Audit**: Compatible with `pip-audit` and `bandit`.

See [SECURITY.md](SECURITY.md) for vulnerability disclosure.

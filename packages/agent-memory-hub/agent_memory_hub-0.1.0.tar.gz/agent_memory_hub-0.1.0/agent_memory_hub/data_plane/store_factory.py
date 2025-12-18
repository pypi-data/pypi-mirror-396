"""
Factory for creating session stores.
"""

from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore, SessionStore


class StoreFactory:
    """Factory to create the appropriate session store backend."""
    
    @staticmethod
    def get_store(
        backend: str = "adk", 
        region: str = "us-central1",
        bucket_prefix: str = "memory-hub"
    ) -> SessionStore:
        """
        Returns a session store instance.
        """
        if backend == "adk":
            # Convention: memory-hub-{region}-prod or similar. 
            # Simplified for this example.
            bucket_name = f"{bucket_prefix}-{region}"
            return AdkSessionStore(bucket_name=bucket_name, region=region)
        
        raise ValueError(f"Unknown backend: {backend}")

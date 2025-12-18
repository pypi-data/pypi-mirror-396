"""
Routes memory requests to the appropriate data plane based on configuration.
"""

from typing import Any, Optional

from agent_memory_hub.control_plane.region_guard import RegionGuard
from agent_memory_hub.data_plane.adk_session_store import SessionStore
from agent_memory_hub.data_plane.store_factory import StoreFactory


class MemoryRouter:
    """
    Routes read/write requests to the correct store, ensuring region compliance.
    """
    def __init__(
        self, 
        region_guard: RegionGuard, 
        backend: str = "adk"
    ):
        self.region_guard = region_guard
        self.backend = backend
        # Initialize store lazily or eagerly? Eagerly for router is fine.
        self.store: SessionStore = StoreFactory.get_store(
            backend=backend, 
            region=region_guard.current_region
        )

    def write(self, session_id: str, key: str, value: Any) -> None:
        """
        Writes data ensuring regional compliance.
        """
        # Double check residency (redundant but safe)
        self.region_guard.check_residency(self.region_guard.current_region)
        self.store.write(session_id, key, value)

    def read(self, session_id: str, key: str) -> Optional[Any]:
        """
        Reads data.
        """
        self.region_guard.check_residency(self.region_guard.current_region)
        return self.store.read(session_id, key)

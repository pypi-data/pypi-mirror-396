"""
Contract protocols for region governance.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class RegionAware(Protocol):
    """Protocol for components that must be aware of their operating region."""
    
    @property
    def current_region(self) -> str:
        """Return the current active region."""
        ...

    def validate_region(self, target_region: str) -> bool:
        """Validate if the operation is allowed in the target region."""
        ...

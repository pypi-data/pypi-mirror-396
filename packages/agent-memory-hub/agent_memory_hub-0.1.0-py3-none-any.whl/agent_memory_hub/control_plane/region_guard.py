"""
Region enforcement logic.
"""

from typing import Optional

from agent_memory_hub.config.regions import SUPPORTED_REGIONS
from agent_memory_hub.control_plane.region_contract import RegionAware


class RegionGuard(RegionAware):
    """
    Enforces region constraints for memory operations.
    """
    def __init__(self, region: str):
        if region not in SUPPORTED_REGIONS:
            raise ValueError(
                f"Region '{region}' is not supported. Supported: {SUPPORTED_REGIONS}"
            )
        self._region = region

    @property
    def current_region(self) -> str:
        return self._region

    def validate_region(self, target_region: str) -> bool:
        """
        Validates if the operation matches the guard's region.
        """
        return self._region == target_region

    def check_residency(self, operation_region: Optional[str] = None) -> None:
        """
        Raises generic RuntimeError if region mismatch.
        """
        if operation_region and operation_region != self._region:
             raise RuntimeError(
                 f"Region violation: Operation in '{operation_region}' "
                 f"but guard locked to '{self._region}'"
             )

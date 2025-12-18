"""
Region configuration and constants.
"""

from typing import Final, Set

# Supported regions for data residency
REGION_US_CENTRAL1: Final[str] = "us-central1"
REGION_EUROPE_WEST1: Final[str] = "europe-west1"
REGION_ASIA_SOUTH1: Final[str] = "asia-south1"

SUPPORTED_REGIONS: Final[Set[str]] = {
    REGION_US_CENTRAL1,
    REGION_EUROPE_WEST1,
    REGION_ASIA_SOUTH1,
}

# Fallback zone or region logic could be defined here
DEFAULT_REGION: Final[str] = REGION_US_CENTRAL1

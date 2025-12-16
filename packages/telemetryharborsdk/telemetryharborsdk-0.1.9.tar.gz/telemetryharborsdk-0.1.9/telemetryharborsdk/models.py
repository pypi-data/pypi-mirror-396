# models.py
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Union

def get_utc_now_iso() -> str:
    """Returns the current time in UTC ISO format with a 'Z' suffix."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

# Define the structure for your 'General' reading
class GeneralReading(BaseModel):
    """A general-purpose telemetry reading."""
    ship_id: str
    cargo_id: str
    value: float
    # Use default_factory to automatically add the timestamp if not provided
    time: str = Field(default_factory=get_utc_now_iso)

# Define the structure for your future 'GPS' reading
""" class GpsReading(BaseModel):
    A GPS location reading.
    ship_id: str
    latitude: float = Field(..., ge=-90, le=90)  # Add validation rules
    longitude: float = Field(..., ge=-180, le=180)
    time: str = Field(default_factory=get_utc_now_iso) """

# A type hint representing any of the valid reading models.
# Add new models here, e.g., Union[GeneralReading, GpsReading, EngineReading]
HarborPayload = Union[GeneralReading]

"""Model for the foreninglet Activities"""

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Activity:
    """Implements a Foreninglet Activities model"""

    ActivityId: str  # API returns strings for IDs
    Name: str
    PriceNow: Optional[str] = "0.00"  # API returns strings for prices
    OnlineEnrollmentEnabled: Optional[str] = "0"  # API returns "0" or "1" as strings
    SettlementDate: Optional[str] = None
    CloseDate: Optional[str] = None
    ExternalDescriptions: List[dict[str, str]] = field(default_factory=list)
    Categories: List[str] = field(default_factory=list)
    DepartmentId: Optional[str] = None  # API returns strings for IDs
    # Handle potential additional fields that might appear in test data
    EndDate: Optional[str] = None
    BackgroundColor: Optional[str] = None
    Type: Optional[str] = None


@dataclass
@dataclass_json
class ActivityList:
    """List of Activity objects"""

    Activities: List[Activity]

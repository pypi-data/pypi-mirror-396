"""A data class for a ForeningLet Member, to map a member from the API to an object"""

import os
from typing import Optional

from pydantic import BaseModel, model_validator

from foreninglet_data.activities import Activities
from foreninglet_data.api import ForeningLet

# Module-level cache to avoid repeated API calls across all Member instances
_activities_cache = None
_memberships_cache = None


def clear_member_cache():
    """Clear the cached activities and memberships - useful for testing"""
    global _activities_cache, _memberships_cache
    _activities_cache = None
    _memberships_cache = None


class Member(BaseModel):
    """Implements a Foreninglet Member"""

    MemberId: int
    MemberNumber: int
    MemberCode: str  # 'd8a8d9241f0ec44' - The members password
    FirstName: str  # 'John' - First name
    LastName: str  # 'Doe', - Last name
    Address: str  # 'Femvej 7' - Address line 1
    Address2: Optional[str] = ""  # - Address line 2
    Zip: int  # '4320'
    City: str  # 'Byen'
    CountryCode: str  # 'DK'
    Email: str  # 'me@me.com'
    Birthday: str  # '1977-01-01'
    Gender: str  # 'Mand','Kvinde' - Danish words for 'Male' and 'Female'
    Phone: Optional[str] = ""  # '12345678 - this will accomodate country code
    Mobile: Optional[str] = ""
    EnrollmentDate: str  # - the date the member joined, as a string representation
    DeliveryMethod: Optional[str] = (
        ""  # - How invoicing will be handled for this member
    )
    PbsAgreementNumber: int = 0
    Note: Optional[str] = ""
    Password: str = ""
    Saldo: int = 0
    SaldoPaymentDeadline: Optional[str] = ""
    Created: str = ""
    Updated: str = ""
    Property: str = ""
    GenuineMember: bool = False
    Image: str = "0"
    MemberField1: str = ""
    MemberField2: str = ""
    MemberField3: str = ""
    MemberField4: str = ""
    MemberField5: str = ""
    MemberField6: str = ""
    MemberField7: str = ""
    MemberField8: str = ""
    MemberField9: str = ""
    MemberField10: str = ""
    MemberField11: str = ""
    MemberField12: str = ""
    MemberField13: str = ""
    MemberField14: str = ""
    MemberField15: str = ""
    MemberField16: str = ""
    MemberField17: str = ""
    MemberField18: str = ""
    MemberField19: str = ""
    MemberField20: str = ""
    ConsentField1: str = ""
    ConsentField2: str = ""
    ConsentField3: str = ""
    ConsentField4: str = ""
    ConsentField5: str = ""
    Activities: str = ""
    activity_ids: str = ""
    Membership: str = ""

    @model_validator(mode="after")
    def register_membership(self):
        """
        Maps the members activity ids to a membership,
        and adds the membership to the member objects
        membership attribute
        """

        global _activities_cache, _memberships_cache

        # Use module-level cache to avoid repeated API calls
        if _memberships_cache is None:
            if _activities_cache is None:
                foreninglet = ForeningLet()
                _activities_cache = foreninglet.get_activities()

            activities = Activities(_activities_cache)
            membership_keywords_str = os.getenv(
                "MEMBERSHIP_KEYWORDS", "medlemskab,medlemsskab"
            )
            membership_keywords = tuple(
                keyword.strip() for keyword in membership_keywords_str.split(",")
            )
            _memberships_cache = activities.identify_memberships(membership_keywords)

        activity_ids = self.activity_ids
        for activity_id in activity_ids.split(","):
            activity_id = activity_id.strip()  # Remove any whitespace
            if activity_id in _memberships_cache:
                self.Membership = _memberships_cache[activity_id]
                break  # Found a match, stop looking
        return self

"""Modules to handle member activities"""

from functools import lru_cache

from foreninglet_data.models.activities_model import Activity


class Activities:
    """Class to handle member activities
    It takes a list of activities as json
    and provides methods to handle the activities
    :param activities: list of activities
    :type activities: list

    output:
    - get_activities: return the list of activities
    - make_activity_map: return a dictionary of activities
    - identify_memberships: return a dictionary of memberships

    """

    def __init__(self, activities: list):
        self.activities = [Activity(**activity) for activity in activities]

    def get_activities(self):
        """Return the list of activities"""
        return self.activities

    def make_activity_map(self):
        """Return a dictionary of activities mapping the ActivityId to the Name"""
        activity_map = {}
        for activity in self.activities:
            activity_map[activity.ActivityId] = activity.Name

        return activity_map

    @lru_cache(maxsize=1280)
    def identify_memberships(self, membership_keywords: list) -> dict:
        """Return a dictionary of memberships"""
        membership_map = {}
        for activity in self.activities:
            activity_model = Activity.from_dict(activity)
            # test activity name for membership keywords
            for keyword in membership_keywords:
                if keyword.lower() in activity_model.Name.lower():
                    membership_map[activity_model.ActivityId] = activity_model.Name
        return membership_map

"""Testing the activities module."""

# The test file is named test_activities.py, and the module is named activities.py.

import pytest
import vcr

from foreninglet_data.activities import Activities
from foreninglet_data.api import ForeningLet
from foreninglet_data.models.activities_model import Activity

from .mock_member import MockMember


@vcr.use_cassette(
    "tests/cassettes/test_data_fl_api_activities_anon.yaml",
    filter_headers=["authorization"],
)
@pytest.mark.vcr
def test_activities_initialize():
    """Test the initialize function."""
    fl_obj = ForeningLet()
    actvity_list = fl_obj.get_activities()
    activities_obj = Activities(actvity_list)
    assert isinstance(activities_obj, Activities)


@vcr.use_cassette(
    "tests/cassettes/test_data_fl_api_activities_anon.yaml",
    filter_headers=["authorization"],
)
@pytest.mark.vcr
def test_get_activities():
    """Test the get_activities function."""
    fl_obj = ForeningLet()
    activity_list = fl_obj.get_activities()
    assert isinstance(activity_list, list)


@vcr.use_cassette(
    "tests/cassettes/test_data_fl_api_activities_anon.yaml",
    filter_headers=["authorization"],
)
@pytest.mark.vcr
def test_make_activity_map():
    """Test the make_activity_map function."""
    fl_obj = ForeningLet()
    activity_list = fl_obj.get_activities()
    activity_obj = Activities(activity_list)
    activity_map = activity_obj.make_activity_map()
    assert isinstance(activity_map, dict)


@vcr.use_cassette(
    "tests/cassettes/test_data_fl_api_activities_anon.yaml",
    filter_headers=["authorization"],
)
@pytest.mark.vcr
def test_mapping_activity_to_model():
    """Test mapping activity to model"""
    fl_obj = ForeningLet()
    activity_list = fl_obj.get_activities()
    activity = activity_list[0]
    activity_model = Activity.from_dict(activity)
    assert isinstance(activity_model, Activity)


@vcr.use_cassette(
    "tests/cassettes/test_data_fl_api_activities_anon.yaml",
    filter_headers=["authorization"],
)
@pytest.mark.vcr
def test_map_menmberships():
    """Test mapping memberships from the activities"""
    fl_obj = ForeningLet()
    actvity_list = fl_obj.get_activities()
    activity_obj = Activities(actvity_list)
    membership_keywords = ["medlemskab", "medlemsskab"]
    memberships = activity_obj.identify_memberships(tuple(membership_keywords))
    assert isinstance(memberships, dict)


def test_map_membership_on_a_member():
    """Test mapping a membership to a member"""
    fl_obj = ForeningLet()
    memberships = fl_obj.get_memberships()

    member_obj = MockMember()
    member = member_obj.mock_member(output_type="obj")
    assert isinstance(member.Membership, str)
    assert member.Membership in memberships.values()


def test_create_activity_model():
    """Test creating an activity model"""
    activity = {
        "ActivityId": "12345",
        "Name": "3 måneders medlemskab",
        "OnlineEnrollmentEnabled": "1",
        "SettlementDate": "0000-00-00T00:00:00+0000",
        "ExternalDescriptions": [],
        "Categories": [],
        "PriceNow": "0.00",
    }
    activity_model = Activity.from_dict(activity)
    assert isinstance(activity_model, Activity)
    assert activity_model.Name == "3 måneders medlemskab"
    assert activity_model.ActivityId == "12345"
    assert activity_model.OnlineEnrollmentEnabled == "1"
    assert activity_model.SettlementDate == "0000-00-00T00:00:00+0000"
    assert activity_model.ExternalDescriptions == []
    assert activity_model.Categories == []


def test_create_activity_model_with_no_externaldescriptions():
    """Test creating an activity model"""
    activity = {
        "ActivityId": "12345",
        "Name": "3 måneders medlemskab",
        "OnlineEnrollmentEnabled": "1",
        "SettlementDate": "0000-00-00T00:00:00+0000",
        "Categories": [],
        "PriceNow": "0.00",
    }
    activity_model = Activity.from_dict(activity)
    assert isinstance(activity_model, Activity)
    assert activity_model.Name == "3 måneders medlemskab"
    assert activity_model.ActivityId == "12345"
    assert activity_model.OnlineEnrollmentEnabled == "1"
    assert activity_model.SettlementDate == "0000-00-00T00:00:00+0000"
    assert activity_model.ExternalDescriptions == []
    assert activity_model.Categories == []


def test_create_activity_model_with_externaldescriptions():
    """Test creating an activity model with external descriptions field"""
    activity = {
        "ActivityId": "12345",
        "Name": "3 måneders medlemskab",
        "OnlineEnrollmentEnabled": "1",
        "SettlementDate": "0000-00-00T00:00:00+0000",
        "ExternalDescriptions": [
            {"Headline": "Headline1", "Text": "Text1"},
            {"Headline": "Headline2", "Text": "Text2"},
        ],
        "Categories": [],
        "PriceNow": "0.00",
    }
    activity_model = Activity.from_dict(activity)
    assert isinstance(activity_model, Activity)
    assert activity_model.Name == "3 måneders medlemskab"
    assert activity_model.ActivityId == "12345"
    assert activity_model.OnlineEnrollmentEnabled == "1"
    assert activity_model.SettlementDate == "0000-00-00T00:00:00+0000"
    assert activity_model.ExternalDescriptions == [
        {"Headline": "Headline1", "Text": "Text1"},
        {"Headline": "Headline2", "Text": "Text2"},
    ]
    assert activity_model.Categories == []

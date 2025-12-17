import pytest
import vcr

from foreninglet_data.models import member_model

from .mock_member import MockMember
from .test_utils import TestUtils


@vcr.use_cassette("tests/vcr_cassettes/test_data_fl_api_activities_anon.yaml")
@pytest.mark.vcr
def test_create_member_object():
    """Test of getting a ForeningLet Member Objet"""
    member = member_model.Member(**TestUtils().dict_for_member())
    assert isinstance(member, member_model.Member)


def test_mock_member_firstname():
    """
    Testing the mock member class
    - to see the name being different from the baseclass of Member
    """
    member = member_model.Member(**TestUtils().dict_for_member())
    name = member.FirstName
    mocked_member_obj = MockMember()
    mocked_member = mocked_member_obj.mock_member(output_type="obj")
    assert mocked_member.FirstName != name


def test_mock_member_lastname():
    """
    Testing the mock member class
    - to see the name being different from the baseclass of Member
    """
    member = member_model.Member(**TestUtils().dict_for_member())
    name = member.LastName
    mocked_member_obj = MockMember()
    mocked_member = mocked_member_obj.mock_member(output_type="obj")
    assert mocked_member.LastName != name


def test_mock_member_memberid():
    """
    Testing the mock member class
    - to see the name being different from the baseclass of Member
    """
    member = member_model.Member(**TestUtils().dict_for_member())
    name = member.MemberId
    mocked_member_obj = MockMember()
    mocked_member = mocked_member_obj.mock_member(output_type="obj")
    assert mocked_member.MemberId != name

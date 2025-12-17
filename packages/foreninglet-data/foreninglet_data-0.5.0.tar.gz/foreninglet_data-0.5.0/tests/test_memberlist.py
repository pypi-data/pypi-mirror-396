"""
Testing the ForeningLet Data Memberlist class
"""

import json
from datetime import datetime

import pandas as pd
import pytest
import vcr
from dateutil.relativedelta import relativedelta

from foreninglet_data.api import ForeningLet
from foreninglet_data.memberlist import Memberlist


def test_memberlist_isobject(mocked_memberlist):
    """
    A test to see a memberlist object has the correct membercount attribute
    """
    memberlist_obj = Memberlist(mocked_memberlist(2, 0))
    assert isinstance(memberlist_obj, object)


def test_memberlist_loads_memberlist(mocked_memberlist):
    """
    Test to make sure the passed memberlist is held by the memberlist object
    """
    memberlist = mocked_memberlist(5, 0)
    memberlist_obj = Memberlist(memberlist)
    assert memberlist_obj.memberlist == memberlist


def test_memberlist_has_correct_membercount(mocked_memberlist):
    """
    Tests the memberlist object to initialize the count of members as an attribute
    """
    memberlist = mocked_memberlist(11, 0)
    memberlist_obj = Memberlist(memberlist)
    assert memberlist_obj.member_count == 11


def test_memberlist_has_correct_gender_count(mocked_memberlist):
    """
    Tests the memberlist object to initialize the count of members for each gender
    as attributes
    """
    memberlist = mocked_memberlist(12, 0)
    df = pd.read_json(json.dumps(memberlist))
    groups = df.groupby("Gender").size()
    males = 0
    females = 0
    if groups.get("M", "") != "":
        males = groups["M"]
    if groups.get("Mand", "") != "":
        males += groups["Mand"]
    if groups.get("K", "") != "":
        females = groups["K"]
    if groups.get("Kvinde", "") != "":
        females += groups["Kvinde"]
    memberlist_obj = Memberlist(memberlist)
    assert memberlist_obj.count_men == males
    assert memberlist_obj.count_women == females


@vcr.use_cassette("tests/cassettes/test_data_fl_api_get_anon.yaml")
@pytest.mark.vcr()
def test_memberlist_class_works_with_real_api_data():
    """
    Tests the memberlist class works with memberlist data
    coming from the ForeningLet API
    """
    fl_obj = ForeningLet()
    memberlist = fl_obj.get_memberlist()
    memberlist_obj = Memberlist(memberlist)
    assert isinstance(memberlist_obj.member_count, int)


def test_memberlist_only_genuine_members(mocked_memberlist):
    """
    Test to only get members where genuinemember == 1
    """
    memberlist = mocked_memberlist(20, 0)
    memberlist_obj = Memberlist(memberlist)

    gen_member_count = 0
    for member in memberlist:
        gen_member_count += member["GenuineMember"]
    assert memberlist_obj.genuine_member_count == gen_member_count


def test_memberlist_age_counts_totals_returns_dict(mocked_memberlist):
    """
    Test to retrieve the number of members for each age group
    """
    memberlist = mocked_memberlist(20, 0)
    memberlist_obj = Memberlist(memberlist)
    age_counts = memberlist_obj.members_age_list
    assert isinstance(age_counts, dict)


def test_memberlist_age_counts_totals_returns_dict_matching_genuine_membercount(
    mocked_memberlist,
):
    """
    Test to retrieve the number of members for each age group
    """
    this_memberlist = mocked_memberlist(20, 0)
    my_memberlist_obj = Memberlist(this_memberlist)
    age_counts = my_memberlist_obj.members_age_list
    print(f"Age count count:{len(age_counts)}")
    member_counts_total = 0
    for member_count in age_counts.values():
        member_counts_total += member_count
        print(f"Member count: {member_count} ")
    assert member_counts_total == 20


def test_memberlist_works_with_wrong_birthday(mocked_memberlist):
    """
    Tests the memberlist object to initialize the count of members as an attribute
    """
    memberlist = mocked_memberlist(1, 0)
    memberlist[0]["Birthday"] = ""
    memberlist_obj = Memberlist(memberlist)
    assert memberlist_obj.member_count == 1


def test_new_member_per_month(mocked_memberlist):
    """Test retrieving a list of new members per month"""
    memberlist = mocked_memberlist(30, 0)
    for member in memberlist:
        # set member['EnrollmentDate'] to same day last month
        member["EnrollmentDate"] = (
            datetime.today() - relativedelta(months=1)
        ).strftime("%Y-%m-%d")
        # update the memberlist with the new EnrollmentDate
        memberlist[memberlist.index(member)] = member
    current_date = datetime.strptime(datetime.today().strftime("%Y-%m"), "%Y-%m")
    months_back_1 = (current_date - relativedelta(months=1)).strftime("%Y-%m")
    member_obj = Memberlist(memberlist)
    df = member_obj.memberlist_dataframe
    # extract EnrollmentDate from a dataframe,
    # change from string to datetime, then format EnrollmentDate from year month day to year month
    df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])
    # group the dataframe by year and month and count the number of members in each group
    df_dates = df.groupby(df["EnrollmentDate"].dt.strftime("%Y-%m")).size()
    # assert the number of members enrolled in the last month equals the number of rows
    # in the memberlist list of json data matching the EnrollmentDate

    assert df_dates[months_back_1] == member_obj.new_members_previous_month


# Test the number of members with an EnrollmentDate in the current month
def test_count_new_members_current_month(mocked_memberlist):
    """
    Test to count the number of members with an EnrollmentDate in the current month
    """
    memberlist = mocked_memberlist(30, 0)
    for member in memberlist:
        # set member['EnrollmentDate'] to same day last month
        member["EnrollmentDate"] = datetime.today().strftime("%Y-%m-%d")
        # update the memberlist with the new EnrollmentDate
        memberlist[memberlist.index(member)] = member
    member_obj = Memberlist(memberlist)
    df = member_obj.memberlist_dataframe
    # extract EnrollmentDate from a dataframe,
    # change from string to datetime, then format EnrollmentDate from year month day to year month
    df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])
    # group the dataframe by year and month and count the number of members in each group
    df_dates = df.groupby(df["EnrollmentDate"].dt.strftime("%Y-%m")).size()
    # assert the number of members enrolled in the last month equals the number of rows
    # in the memberlist list of json data matching the EnrollmentDate
    assert (
        df_dates[datetime.today().strftime("%Y-%m")]
        == member_obj.new_members_current_month
    )


def test_members_per_year(mocked_memberlist):
    """
    Test to count the number of members per year
    """
    memberlist = mocked_memberlist(30, 0)
    year_subtract = 0
    for member in memberlist:
        # Set member['EnrollmentDate'] to same day last year
        member["EnrollmentDate"] = (
            datetime.today() - relativedelta(years=year_subtract)
        ).strftime("%Y-%m-%d")
        member["GenuineMember"] = 1
        # For every 5 members subtract one year from the EnrollmentDate
        if memberlist.index(member) % 5 == 0:
            year_subtract += 1
        # update the memberlist with the new EnrollmentDate
        memberlist[memberlist.index(member)] = member
    member_obj = Memberlist(memberlist)
    df = member_obj.memberlist_dataframe
    # Count number members per year from earliest year to latest year, but only where GenuineMember == 1
    df_dates = (
        df[df["GenuineMember"] == 1]
        .groupby(df["EnrollmentDate"].dt.strftime("%Y"))
        .size()
    )
    # Get the highest value from the df_dates series
    earliest_year = df_dates.index.min()

    # Get the latest year from the dataframe
    latest_year = df_dates.index.max()

    # Count number members per year
    df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])

    assert df_dates[latest_year] == member_obj.members_current_year
    assert (
        df_dates[(datetime.today() - relativedelta(years=1)).strftime("%Y")]
        == member_obj.members_last_year
    )


def test_number_of_members_under_25(mocked_memberlist):
    """
    Test to count the number of members under 25 years old
    """
    memberlist = mocked_memberlist(10, 0)
    current_year = datetime.now().year
    for member in memberlist:
        # Set member['Birthday'] to be 20 years ago
        member["Birthday"] = f"{current_year - 20}-01-01"
        # update the memberlist with the new Birthday
        memberlist[memberlist.index(member)] = member
    member_obj = Memberlist(memberlist)
    assert member_obj.count_members_under_25 == 10

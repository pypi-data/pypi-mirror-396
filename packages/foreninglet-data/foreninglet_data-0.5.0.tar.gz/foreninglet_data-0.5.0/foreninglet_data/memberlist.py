"""
Class for handling the ForeningLet Memberlist data
"""

import json
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from loguru import logger


class Memberlist:
    """
    Handles memberlist data from the ForeningLet API
    The class is instatiated by passing a JSON object containing memberlist data
    as it is returned from the API.
    """

    memberlist = ""
    genuine_member_count = 0
    member_count = 0
    count_men = 0
    count_women = 0
    count_members_under_25 = 0
    memberlist_dataframe = pd.DataFrame()
    members_age_list = {}
    new_members_previous_month = 0
    members_current_year = 0
    members_last_year = 0
    members_per_year = {}

    def __new__(cls, *args):
        """Make sure we create a clean memberlist object every time"""
        cls.count_men = 0
        cls.count_women = 0
        cls.count_members_under_25 = 0
        cls.genuine_member_count = 0
        cls.member_count = 0
        cls.memberlist = ""
        cls.memberlist_dataframe = pd.DataFrame()
        cls.members_age_list = {}
        cls.new_members_previous_month = 0
        cls.new_members_previous_month_percentage = 0
        cls.new_members_current_month = 0
        cls.new_members_current_month_percentage = 0
        cls.members_current_year = 0
        cls.members_per_year = {}
        return super().__new__(cls)

    def __init__(self, memberlist) -> None:
        self.memberlist = memberlist
        self._load_memberlist_to_dataframe()
        self._count_members()
        self._count_genuine_members()
        self._count_genders()
        self._count_members_under_25()
        self._create_member_ages_list()
        self._set_new_members_previous_month()
        self.set_new_members_current_month()
        self.set_members_per_year()

    def _count_members(self):
        """
        Method to count the number of members
        """
        df = self.memberlist_dataframe
        self.member_count = len(df)

    def _count_genuine_members(self):
        """
        Method to get the count of genuine members
        """
        df = self.memberlist_dataframe
        self.genuine_member_count = len(df.loc[df["GenuineMember"] == 1])

    def _count_genders(self):
        """
        Method to count the number of men and women in the memberlist
        Men are signified by 'Gender' = 'M' (danish - M for Mand)
        Women are signified by 'Gender' = 'K' (danish - K for Kvinde)
        """
        df = self.memberlist_dataframe
        groups = df.groupby("Gender").size()
        men = 0
        women = 0
        if groups.get("M", "") != "":
            men = groups["M"]
        if groups.get("Mand", "") != "":
            men += groups["Mand"]
        if groups.get("K", "") != "":
            women = groups["K"]
        if groups.get("Kvinde", "") != "":
            women += groups["Kvinde"]
        self.count_men = men
        self.count_women = women

    def _count_members_under_25(self):
        """
        Method to count the number of members who are 25 years old or younger
        """
        count = 0
        for member in self.memberlist:
            if member["Birthday"] == "":
                # Skip members with no birthday - they won't be counted
                continue
            try:
                birthday = datetime.strptime(member["Birthday"], "%Y-%m-%d")
                now = datetime.now()
                diff = relativedelta(now, birthday)
                age = diff.years
                if age <= 25:
                    count += 1
            except (ValueError, TypeError):
                # Skip members with invalid birthday format
                continue
        self.count_members_under_25 = count

    def _load_memberlist_to_dataframe(self):
        """
        Method loading the memberlist to a dataframe
        """
        the_memberlist = self.memberlist
        if isinstance(the_memberlist, list):
            the_memberlist = json.dumps(self.memberlist)
        self.memberlist_dataframe = pd.read_json(the_memberlist)

    def _create_member_ages_list(self) -> None:
        """
        Method to count the number of members for each age in the memberlist.
        Will fill in 0 for an age, if no members have that age.
        """
        min_age = 0
        max_age = 0
        for member in self.memberlist:
            if member["Birthday"] == "":
                corrected_birthday = datetime.today().strftime("%Y-%m-%d")
                logger.warning(
                    f"Corrected birthday to be {corrected_birthday} for memberid: {member['MemberId']}, memberNumber: {member['MemberNumber']}, name: {member['FirstName']} {member['LastName']} "
                )
                member["Birthday"] = corrected_birthday
            birthday = datetime.strptime(member["Birthday"], "%Y-%m-%d")
            now = datetime.now()
            diff = relativedelta(now, birthday)
            age = diff.years
            if self.members_age_list.get(age, None) is None:
                self.members_age_list[age] = 1
            else:
                self.members_age_list[age] += 1
            if age < min_age or min_age == 0:
                min_age = age
            if age > max_age or max_age == 0:
                max_age = age
        # We want the age list to contain the full range of ages from min_age to max_age
        # so fill in the ages not in the list with a 0
        for i in range(min_age, max_age - min_age):
            if self.members_age_list.get(i, None) is None:
                self.members_age_list[i] = 0
        # The list should be sorted by age ascending

        sorted_list = dict(sorted(self.members_age_list.items()))
        self.members_age_list = {}
        self.members_age_list = sorted_list

    # A method counting the number of members with an EnrollmentDate in the previous month
    def count_new_members_previous_month(self):
        """
        Method to count the number of members with an EnrollmentDate in the previous month
        """
        df = self.memberlist_dataframe
        now = datetime.now()
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year - 1 if now.month == 1 else now.year
        # convert EnrollmentDate to datetime
        df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])
        prev_month_members = df.loc[
            (df["EnrollmentDate"].dt.month == prev_month)
            & (df["EnrollmentDate"].dt.year == prev_year)
        ]
        return len(prev_month_members)

    # A method setting class attributes for the number of members with an EnrollmentDate in the previous month
    def _set_new_members_previous_month(self):
        """
        Method to set class attributes for the number of members with an EnrollmentDate in the previous month
        """
        self.new_members_previous_month = self.count_new_members_previous_month()
        self.new_members_previous_month_percentage = (
            self.new_members_previous_month / self.member_count * 100
        )
        self.new_members_previous_month_percentage = round(
            self.new_members_previous_month_percentage, 2
        )
        self.new_members_previous_month_percentage = (
            f"{self.new_members_previous_month_percentage}%"
        )
        self.new_members_previous_month_percentage = (
            self.new_members_previous_month_percentage.replace(".", ",")
        )

    # Method to get the number of members with an EnrollmentDate in the current month
    def count_new_members_current_month(self):
        """
        Method to count the number of members with an EnrollmentDate in the current month
        """
        df = self.memberlist_dataframe
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        # convert EnrollmentDate to datetime
        df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])
        current_month_members = df.loc[
            (df["EnrollmentDate"].dt.month == current_month)
            & (df["EnrollmentDate"].dt.year == current_year)
        ]
        return len(current_month_members)

    # Method to set class attributes for the number of members with an EnrollmentDate in the current month
    def set_new_members_current_month(self):
        """
        Method to set class attributes for the number of members with an EnrollmentDate in the current month
        """
        self.new_members_current_month = self.count_new_members_current_month()
        self.new_members_current_month_percentage = (
            self.new_members_current_month / self.member_count * 100
        )
        self.new_members_current_month_percentage = round(
            self.new_members_current_month_percentage, 2
        )
        self.new_members_current_month_percentage = (
            f"{self.new_members_current_month_percentage}%"
        )
        self.new_members_current_month_percentage = (
            self.new_members_current_month_percentage.replace(".", ",")
        )

    # METHOD to count the number of members per year
    def count_members_per_year(self):
        """
        Method to count the number of members per year
        """
        df = self.memberlist_dataframe
        # convert EnrollmentDate to datetime
        df["EnrollmentDate"] = pd.to_datetime(df["EnrollmentDate"])
        df_dates = (
            df[df["GenuineMember"] == 1]
            .groupby(df["EnrollmentDate"].dt.strftime("%Y"))
            .size()
        )
        return df_dates

    def set_members_per_year(self):
        """
        Method to set class attributes for the number of members per year
        """
        self.members_per_year = self.count_members_per_year()
        self.members_current_year = self.members_per_year.get(
            datetime.today().strftime("%Y"), 0
        )
        self.members_last_year = self.members_per_year.get(
            (datetime.today() - relativedelta(years=1)).strftime("%Y"), 0
        )
        self.members_per_year = self.members_per_year.to_dict()
        self.members_per_year = dict(sorted(self.members_per_year.items()))

    def get_addresses_and_zip_numbers(self) -> None:
        """Method to extract street addresses and zip numbers as a csv file"""
        df = self.memberlist_dataframe
        addresses = df[["Address", "Zip"]]
        addresses.to_csv("addresses.csv", index=False)

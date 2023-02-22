import pytest
from selenium.webdriver.support.select import Select

from PythonFramework.TestData.homePageData import HomePageData
from PythonFramework.pageObjects.HomePage import HomePage
from PythonFramework.utilities.BaseClass import BaseClass


class TestHomePage(BaseClass):

    def test_form_submission(self, GetData):  # here we load the fixture onto method parameters
        home_page = HomePage(self.driver)
        home_page.GetName().send_keys(GetData["firstname"])
        home_page.GetEmail().send_keys(GetData["email"])
        home_page.GetPassword().send_keys("katana22")
        home_page.GetCheckBox1().click()

        home_page.GetInlineRadio1().click()
        self.SelectOptionByText(home_page.GetGenderDropdown(), GetData["gender"])  # custom utility with the 2 params
        # defined

        home_page.GetSubmit().click()

        message = home_page.GetAlertText().text
        print(message)
        assert "Success" in message  # we assert the word is present in the message variable
        self.driver.refresh()  # execution happens once with every data set so a need of refreshing browser is needed
        # to avoid data concatenation

    @pytest.fixture(params=HomePageData.test_homePage_data)
    def GetData(self, request):
        return request.param

# E2E Test to buy a product from the catalog
import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from PythonFramework.pageObjects.CheckoutPage import CheckOutPage
from PythonFramework.pageObjects.HomePage import HomePage
from PythonFramework.utilities.BaseClass import BaseClass


# @pytest.mark.usefixtures("setup")
class TestOne(BaseClass):

    def test_e2e(self):

        home_page = HomePage(self.driver)
        # a[href*='/angularpractice/shop'] --> this uses regular expression. Or a[href*='shop']
        home_page.GetShopItems().click()
        self.driver.implicitly_wait(5)

        check_out_page = CheckOutPage(self.driver)
        products_grid = check_out_page.GetCardTitles()
        for product in products_grid:
            product_name = product.find_element(By.XPATH, "div/h4/a").text
            if product_name == "Blackberry":
                card_button = check_out_page.GetCardButton()

        check_out_button = check_out_page.GetAddCheckOutButton().click()
        add_check_out_button = check_out_page.GetCheckOutButton().click()
        country_box = check_out_page.GetCountryBox().send_keys("spa")

        wait = self.VerifyLinkPresence("Spain")  # here we use utility function
        self.driver.find_element(By.LINK_TEXT, "Spain").click()
        check_box_primary = check_out_page.GetCheckBoxPrimary().click()
        purchase_button = check_out_page.GetPurchaseButton().click()
        success_message = check_out_page.GetSuccessMessage().text
        print(success_message)
        assert "Success! Thank you!" in success_message  # using a partial text helps to avoid possible errors

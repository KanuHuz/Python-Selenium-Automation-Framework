import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


@pytest.mark.usefixtures("setup")
class BaseClass:

    def VerifyLinkPresence(self, text):  # the country name grabbed gets stored into text parameter
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, text)))

    def SelectOptionByText(self, locator, text):
        dropdown = Select(locator)
        dropdown_option = dropdown.select_by_visible_text(text)

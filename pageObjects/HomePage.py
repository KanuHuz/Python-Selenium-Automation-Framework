from selenium.webdriver.common.by import By
from selenium import webdriver


class HomePage:

    def __init__(self, driver):
        self.driver = driver

    shop = (By.CSS_SELECTOR, "a[href*='/angularpractice/shop']")
    name = (By.CSS_SELECTOR, "input[name='name']")
    email = (By.NAME, "email")
    password = (By.ID, "exampleInputPassword1")
    check_box1 = (By.ID, "exampleCheck1")
    gender_dropdown = (By.ID, "exampleFormControlSelect1")
    inline_radio1 = (By.CSS_SELECTOR, "#inlineRadio1")
    submit = (By.XPATH, "//input[@type='submit']")
    alert_text = (By.CLASS_NAME, "alert-success")

    def GetShopItems(self):
        return self.driver.find_element(*HomePage.shop)  # * used to deserialize and call arg into function as a tuple

    def GetName(self):
        return self.driver.find_element(*HomePage.name)

    def GetEmail(self):
        return self.driver.find_element(*HomePage.email)

    def GetPassword(self):
        return self.driver.find_element(*HomePage.password)

    def GetCheckBox1(self):
        return self.driver.find_element(*HomePage.check_box1)

    def GetGenderDropdown(self):
        return self.driver.find_element(*HomePage.gender_dropdown)

    def GetInlineRadio1(self):
        return self.driver.find_element(*HomePage.inline_radio1)

    def GetSubmit(self):
        return self.driver.find_element(*HomePage.submit)

    def GetAlertText(self):
        return self.driver.find_element(*HomePage.alert_text)


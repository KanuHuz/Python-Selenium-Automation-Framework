from selenium.webdriver.common.by import By
from selenium import webdriver


class CheckOutPage:

    def __init__(self, driver):
        self.driver = driver

    cardTitles = (By.XPATH, "//div[@class='card h-100']")
    cardButton = (By.XPATH, "div/button")
    addCheckOutButton = (By.XPATH, "//a[@class='nav-link btn btn-primary']")
    checkOutButton = (By.XPATH, "//button[@class='btn btn-success']")
    checkBoxPrimary = (By.XPATH, "//div[@class='checkbox checkbox-primary']")
    purchaseButton = (By.XPATH, "//input[@value='Purchase']")
    successMessage = (By.XPATH,"//div/div[@class='alert alert-success alert-dismissible']")
    countryBox = (By.ID, "country")

    def GetCardTitles(self):
        return self.driver.find_elements(*CheckOutPage.cardTitles)

    def GetCardButton(self):
        return self.driver.find_elements(*CheckOutPage.cardButton)

    def GetAddCheckOutButton(self):
        return self.driver.find_element(*CheckOutPage.addCheckOutButton)

    def GetCheckOutButton(self):
        return self.driver.find_element(*CheckOutPage.checkOutButton)

    def GetCheckBoxPrimary(self):
        return self.driver.find_element(*CheckOutPage.checkBoxPrimary)

    def GetPurchaseButton(self):
        return self.driver.find_element(*CheckOutPage.purchaseButton)

    def GetSuccessMessage(self):
        return self.driver.find_element(*CheckOutPage.successMessage)

    def GetCountryBox(self):
        return self.driver.find_element(*CheckOutPage.countryBox)



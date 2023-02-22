import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def pytest_addoption(parser):
    parser.addoption(
        "--browser_name", action="store", default="chrome"
    )


@pytest.fixture(scope="class")  # scope makes this execute before the class
def setup(request):
    browser_name = request.config.getoption("browser_name")
    if browser_name == "chrome":
        service_obj = Service("/Users/facundo.huser/Documents/ChromeDriver/chromedriver")
        driver = webdriver.Chrome(service=service_obj)
        driver.maximize_window()
        driver.get("https://rahulshettyacademy.com/angularpractice")
        request.cls.driver = driver
    elif browser_name == "firefox":
        service_obj1 = Service("/Users/facundo.huser/Documents/GeckoDriver/geckodriver")
        driver = webdriver.Firefox(service=service_obj1)
        driver.maximize_window()
        driver.get("https://rahulshettyacademy.com/angularpractice")
        request.cls.driver = driver

    # this step has teardown. It executes after the rest has been executed
    yield
    driver.close()



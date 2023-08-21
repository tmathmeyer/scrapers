from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def get_chromedriver():
  from selenium.webdriver.chrome.service import Service as ChromeService
  from selenium.webdriver.chrome.options import Options

  options = Options()
  options.add_experimental_option("prefs", {
    "download.default_directory": "/home/ted/Downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
  })

  service = ChromeService(executable_path="/usr/bin/chromedriver")
  return webdriver.Chrome(service=service, options=options)


def get_chase_authenticated_driver(username, password):
  """Return a logged-in Chase Amazon card selenium driver instance."""
  driver = get_chromedriver()
  driver.get("https://secure09ea.chase.com/web/auth/dashboard#/dashboard/index/index")
  time.sleep(3)
  iframe = driver.find_element(By.ID, "logonbox")
  driver.switch_to.frame(iframe)

  input_element = driver.find_element(By.XPATH, '//input[@data-validate="userId"]')
  input_element.send_keys(username)

  password_element = driver.find_element(By.ID, "password-text-input-field")
  password_element.send_keys(password)

  driver.find_element(By.ID, "signin-button").click()
  time.sleep(10)
  return driver


def load_download_page(driver):
  driver.get('https://secure26ea.chase.com/web/auth/dashboard#/dashboard/accountDetails/downloadAccountTransactions/index;params=CARD,BAC,850730849,')
  time.sleep(5)


def download_for_card(driver, last_four):
  driver.find_element(By.ID, 'select-downloadActivityOptionId').click()
  time.sleep(1)
  driver.find_element(By.XPATH, f'//mds-select-option[@label="Year to date"]').click()
  time.sleep(1)
  driver.find_element(By.ID, 'select-account-selector').click()
  time.sleep(1)
  driver.find_element(By.XPATH, f'//mds-select-option[@label="CREDIT CARD (...{last_four})"]').click()
  time.sleep(1)
  driver.find_element(By.XPATH, '//mds-button[@text="Download"]').click()




if __name__ == '__main__':
  import getpass

  uname = input("Username: ")
  pwd = getpass.getpass()

  driver = get_chase_authenticated_driver(uname, pwd)
  download_for_card(driver, 'xxxx')

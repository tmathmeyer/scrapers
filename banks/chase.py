
import time

from selenium import webdriver

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

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

  options.add_argument('--user-data-dir=./datadir')
  service = ChromeService(executable_path="/usr/bin/chromedriver")
  return webdriver.Chrome(service=service, options=options)


def load_cookies(driver):
  try:
    import cookies
    for cookie in cookies.COOKIES:
      driver.add_cookie(cookie)
  except:
    pass


def await_element(driver, tag, seconds):
  WebDriverWait(driver, seconds).until(
    expected_conditions.visibility_of_element_located(
      (By.CSS_SELECTOR, tag)))



def get_chase_authenticated_driver(username, password):
  """Return a logged-in Chase Amazon card selenium driver instance."""
  driver = get_chromedriver()
  driver.get("https://secure09ea.chase.com/web/auth/?fromOrigin=https://secure09ea.chase.com")

  await_element(driver, '#logon-content', 30)
  #export_cookies = load_cookies(driver)

  username_container = driver.find_element(By.XPATH, '//mds-text-input')
  password_container = driver.find_element(By.XPATH, '//mds-text-input-secure')

  username_input = username_container.shadow_root.find_element(By.NAME, 'username')
  password_input = password_container.shadow_root.find_element(By.NAME, 'password-input')

  username_input.send_keys(username)
  password_input.send_keys(password)

  driver.find_element(By.ID, "signin-button").click()
  await_element(driver, '#ovd-layout-container', 30)

  driver.get_cookies()

  return driver


def load_download_page(driver):
  driver.get('https://secure26ea.chase.com/web/auth/dashboard#/dashboard/accountDetails/downloadAccountTransactions/index;params=CARD,BAC,850730849,')
  await_element(driver, '#account-selector', 30)


def download_for_card(driver, last_four):
  load_download_page(driver)
  found = False

  account_selector = driver.find_element(By.ID, 'account-selector').shadow_root
  account_selector.find_element(By.ID, 'select-account-selector').click()
  account_dropdown = account_selector.find_elements(By.CLASS_NAME, 'mds-select__menu')
  print(account_dropdown[0].get_attribute('style'))
  time.sleep(2)
  for element in account_dropdown[0].find_elements(By.CLASS_NAME, 'mds-select-option--cpo'):
    print(element)
    if last_four in element.get_attribute('label'):
      element.click()
      found = True
  if not Found:
    return 'Unable to select account'
  found = False

  await_element(driver, '#downloadFileTypeOption', 30)
  format_selector = driver.find_element(By.ID, 'downloadFileTypeOption').shadow_root
  format_selector.find_element(By.ID, 'select-downloadFileTypeOption').click()
  time.sleep(1)
  for element in format_selector.find_elements(By.CLASS_NAME, 'mds-select-option--cpo'):
    if element.get_attribute('value') == 'QFX':
      element.click()
      found = True
  if not Found:
    return 'Unable download QFX'
  found = False

  await_element(driver, '#downloadActivityOptionId', 30)
  daterange_selector = driver.find_element(By.ID, 'downloadActivityOptionId').shadow_root
  daterange_selector.find_element(By.ID, 'select-downloadActivityOptionId').click()
  time.sleep(1)
  for element in daterange_selector.find_elements(By.CLASS_NAME, 'mds-select-option--cpo'):
    if element.get_attribute('value') == 'YEAR_TO_DATE':
      element.click()
      found = True
  if not Found:
    return 'Unable download Year-to-date'

  time.sleep(10)
  driver.find_element(By.ID, 'download').click()




if __name__ == '__main__':
  import getpass

  #uname = input("Username: ")
  pwd = getpass.getpass()

  uname = ''

  driver = get_chase_authenticated_driver(uname, pwd)
  download_for_card(driver, '5448')

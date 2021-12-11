"""
Description: Basic, simple selenium-based script for checking and making appointments at LBV (German DMV)
Authors: Jakob Everding
Date: 10.12.2021 (first: 08.12.2021)
"""
import os
from dotenv import load_dotenv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Config and import secrets
secrets_loc = os.path.join(os.path.abspath(os.getcwd()), "secrets", ".env")
load_dotenv(dotenv_path=secrets_loc)
system = os.environ.get("system")
first_name = os.environ.get("first_name")
last_name = os.environ.get("last_name")
email = os.environ.get("email")
path_b_driver = os.environ.get("path_b_driver")


# Prepare selenium
options = Options()
if system.lower() == "linux":
    options.add_argument("no-sandbox")
options.add_argument("headless")
options.add_argument("window-size=1500,1200")
service = Service(path_b_driver)

driver = webdriver.Chrome(options=options, service=service)
driver.get("https://www.lbv-termine.de/frontend/onlinedienstleistung.php?dienstleistungsid=176")

# Site: Data protection
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "datenschutzgelesen"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "weiterbutton"))).click()

# Site: Personal data
fname_box = driver.find_element(by=By.ID, value="vorname")
fname_box.send_keys(first_name)
lname_box = driver.find_element(by=By.ID, value="nachname")
lname_box.send_keys(last_name)
email_box = driver.find_element(by=By.ID, value="email")
email_box.send_keys(email)
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "weiterbutton"))).click()

# Site: Site selection
x = driver.find_element(by=By.CSS_SELECTOR, value="a[href*='terminauswahl.php?standortid=109']")
x.click()

# Site: Date selection
dates = driver.find_elements(by=By.NAME, value="daten")
min_date_str = dates[0].get_attribute("id")
# Proceed only if earliest available date is before some specified date
min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
if min_date < datetime(2021, 12, 22):
    x = driver.find_element(by=By.ID, value=min_date_str)
    x.click()

    times = driver.find_elements(by=By.NAME, value="zeiten")
    min_time = times[0].get_attribute("id")
    driver.find_element(by=By.ID, value=min_time).click()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "weiterbutton"))).click()

    # End
    print("Appointment booked, ending selenium")
    driver.quit()

else:
    # End
    print("No appointment booked, ending selenium")
    driver.quit()

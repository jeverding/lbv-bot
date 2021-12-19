"""
Description: Basic, simple selenium-based script for checking and making appointments at LBV (German DMV)
Authors: Jakob Everding
Date: 19.12.2021 (first: 08.12.2021)
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging

from src.rotate import rotate_proxies

# Config and import secrets
secrets_loc = os.path.join(os.path.abspath(os.getcwd()), "secrets", ".env")
load_dotenv(dotenv_path=secrets_loc)
first_name = os.environ.get("first_name")
last_name = os.environ.get("last_name")
email = os.environ.get("email")

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


@rotate_proxies
def book_fs(driver):
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
    driver.find_element(by=By.CSS_SELECTOR, value="a[href*='terminauswahl.php?standortid=109']").click()

    # Site: Date selection
    dates = driver.find_elements(by=By.NAME, value="daten")
    min_date_str = dates[0].get_attribute("id")
    # Proceed only if earliest available date is before some specified date
    min_date = datetime.strptime(min_date_str, "%Y-%m-%d")
    if min_date < datetime(2021, 12, 22):
        driver.find_element(by=By.ID, value=min_date_str).click()

        driver.implicitly_wait(20)
        times = driver.find_elements(by=By.NAME, value="zeiten")
        min_time = times[0].get_attribute("id")
        driver.find_element(by=By.ID, value=min_time).click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "weiterbutton"))).click()
        print("Appointment booked, end")
    else:
        print("No appointment booked, end")


def main():
    book_fs()


if __name__ == "__main__":
    main()

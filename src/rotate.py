"""
Description: This scripts automates the Selenium webdriver configuration with rotating proxies
Authors: Jakob Everding
Date: 12.12.2021 (first: 11.12.2021)
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from itertools import cycle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Config and import secrets
secrets_loc = str(Path.cwd() / "secrets" / ".env")
load_dotenv(dotenv_path=secrets_loc)
system = os.environ.get("system")
first_name = os.environ.get("first_name")
last_name = os.environ.get("last_name")
email = os.environ.get("email")
path_b_driver = str(Path.cwd() / os.environ.get("path_b_driver"))


def get_proxies() -> list:
    selenium_proxy = Proxy()
    selenium_proxy.proxy_type = ProxyType.SYSTEM
    capabilities = DesiredCapabilities.CHROME
    selenium_proxy.add_to_capabilities(capabilities)

    options = Options()
    if system.lower() == "linux":
        options.add_argument("no-sandbox")
    options.add_argument("headless")
    options.add_argument("window-size=1500,1200")
    service = Service(path_b_driver)
    driver = webdriver.Chrome(options=options, service=service, desired_capabilities=capabilities)
    driver.get("https://free-proxy-list.net/")
    # TODO (JE): Update this part - working atm, but inefficient
    free_proxies = driver.find_elements(by=By.CSS_SELECTOR, value="td")

    proxy_pool = []
    rows = int(len(free_proxies) / 8)
    for i in range(rows):
        ip = free_proxies[i * 8].text
        port = free_proxies[i * 8 + 1].text
        https = free_proxies[i * 8 + 6].text
        if https == "yes":
            proxy_pool.append(f"{ip}:{port}")

    driver.quit()
    return proxy_pool


def driver_proxy(proxy):
    selenium_proxy = Proxy()
    selenium_proxy.proxy_type = ProxyType.MANUAL
    selenium_proxy.http_proxy = proxy
    selenium_proxy.ssl_proxy = proxy

    capabilities = DesiredCapabilities.CHROME
    selenium_proxy.add_to_capabilities(capabilities)

    options = Options()
    if system.lower() == "linux":
        options.add_argument("no-sandbox")
    options.add_argument("headless")
    options.add_argument("window-size=1500,1200")
    service = Service(path_b_driver)
    driver = webdriver.Chrome(options=options, service=service, desired_capabilities=capabilities)

    return driver


def run_selenium():
    # Get https proxies, rotate, and add to webdriver config
    proxy_pool = []
    proxy_iter = cycle(proxy_pool)
    n_proxy = 0
    while True:
        try:
            # TODO (JE): Check if transforming if e.g. to while loop makes sense
            if n_proxy >= len(proxy_pool):
                print("Getting new proxy pool")
                proxy_pool = get_proxies()
                proxy_iter = cycle(proxy_pool)
                n_proxy = 0
            print(f"Proxy position in current pool, n_proxy: {n_proxy}; pool size: {len(proxy_pool)}")
            proxy = next(proxy_iter)
            driver = driver_proxy(proxy=proxy)

            inner_execute(driver=driver)

            if driver:
                driver.quit()
        except Exception as e:
            print(e)
            print(f"Trying with other proxy; n_proxy: {n_proxy}")
            n_proxy += 1
            continue
        break


def inner_execute(driver):
    driver.get("https://www.lbv-termine.de/frontend/onlinedienstleistung.php?dienstleistungsid=176")

    # Bug:
    dates = driver.find_elements(by=By.NAME, value="daten")
    dates = str(dates)

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
        print("Appointment booked, end")

    else:
        # End
        print("No appointment booked, end")


def main():
    run_selenium()


if __name__ == "__main__":
    main()

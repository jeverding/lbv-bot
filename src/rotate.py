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

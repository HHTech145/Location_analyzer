import os
import re
import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
from database.data_json import JsonDataHandler

class WebDriverManager:
    def __init__(self, url):
        self.url = url
        self.driver = self.instantiate_driver()

    def instantiate_driver(self):
        print("In Uber Eats")
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Optional, for better performance
        options.add_argument("--window-size=1920x1080")  # Optional, set window size
        # options.add_argument("--window-position=-2400,-2400")
        options.add_argument('--user-data-dir=C:/Users/USER/AppData/Local/Google/Chrome/User Data/Profile 1')

        # Use a unique temp directory for each session
        # temp_dir = tempfile.mkdtemp()
        # options.add_argument(f"--user-data-dir={temp_dir}")
        # base_download_dir = "D:\\work\\automation\\free_map_tools\\final\\Location_analyzer\\app\\downloaded_csv"

        # prefs = {"download.default_directory" :base_download_dir}
        # options.add_experimental_option("prefs",prefs)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        print("in free map ")
        sleep(2)
        driver.execute_script("document.body.style.zoom='50%'")
        return driver

    def quit(self):
        self.driver.quit()


if __name__ == "__main__":
    url="https://deliveroo.co.uk/"
    driver_manager = WebDriverManager(url)
    sleep(2000)



/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[6]


/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[2]
/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[2]/button

/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[2]/button
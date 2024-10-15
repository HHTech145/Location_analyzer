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

class WebDriverManager:
    def __init__(self, url):
        self.url = url
        self.driver = self.instantiate_driver()

    def instantiate_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Optional, for better performance
        options.add_argument("--window-size=1920x1080")  # Optional, set window size
        options.add_argument("--window-position=-2400,-2400")
        # options.add_argument('--user-data-dir=C:/Users/USER/AppData/Local/Google/Chrome/User Data/Default')

        # Use a unique temp directory for each session
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        sleep(2)
        driver.execute_script("document.body.style.zoom='50%'")
        return driver

    def input_radius_and_postcode(self, postcode,radius):
        # input_field = self.driver.find_element(By.ID, "locationSearchTextBox")
        input_field = self.driver.find_element(By.ID, "tb_radius")

        # Clear any existing value in the field (optional)
        input_field.clear()

        # Pass a value into the input field
        input_field.send_keys(radius)
        sleep(1)

        input_field = self.driver.find_element(By.ID, "locationSearchTextBox")

        # Clear any existing value in the field (optional)
        input_field.clear()

        # Pass a value into the input field
        input_field.send_keys(postcode)

    def click_on_search(self):
        search_button = WebDriverWait(self.driver, 100).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="locationSearchButton"]'))
        )
        search_button.click()
        sleep(10)

    def click_on_save_csv(self):
        sleep(4)
        csv_button = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '(//*[@id="btnDownloadCSV"])[1]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", csv_button)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '(//*[@id="btnDownloadCSV"])[1]'))).click()
        sleep(1)

    def quit(self):
        self.driver.quit()


class CSVHandler:
    @staticmethod
    def get_latest_csv_file(directory):
        files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not files:
            return None
        full_paths = [os.path.join(directory, f) for f in files]
        return max(full_paths, key=os.path.getmtime)

    @staticmethod
    def load_csv_get_postcodes(directory):
        latest_csv_file = CSVHandler.get_latest_csv_file(directory)
        if latest_csv_file is None:
            print("No CSV files found in the directory.")
            return []

        df = pd.read_csv(latest_csv_file, header=None)
        postcodes = df.values.flatten()
        outer_codes = [postcode.strip().split()[0] for postcode in postcodes if isinstance(postcode, str)]
        return list(set(outer_codes))


class DemographicsExtractor:
    @staticmethod
    def extract_demographics(soup):
        demographics = {}

        # Total Population
        population_div = soup.find("span", string="TOTAL POPULATION")
        if population_div:
            number_text = re.search(r'\d+,\d+|\d+', population_div.find_previous_sibling(text=True)).group()
            demographics['total_population'] = number_text

        # Households
        households_div = soup.find("span", string="HOUSEHOLDS")
        if households_div:
            number_text = re.search(r'\d+,\d+|\d+', households_div.find_previous_sibling(text=True)).group()
            demographics['households'] = number_text

        # Unemployment Rate
        unemployment_div = soup.find("span", string="UNEMPLOYMENT RATE")
        if unemployment_div:
            number_text = re.search(r'\d+(\.\d+)?%', unemployment_div.find_previous_sibling(text=True)).group()
            demographics['unemployment_rate'] = number_text

        # Average Household Income
        income_div = soup.find("span", string="AVG HOUSEHOLD INCOME")
        if income_div:
            number_text = re.search(r'£?\d+,\d+|\d+', income_div.find_previous_sibling(text=True)).group()
            demographics['avg_household_income'] = number_text

        return demographics

    @staticmethod
    def extract_additional_data(soup):
        # Extract Employment data
        employment_div = soup.find('div', id='marital-status')
        if employment_div:
            working = employment_div.find_all('li')[0].find('strong').text.strip()
            unemployed = employment_div.find_all('li')[1].find('strong').text.strip()
        else:
            working = None
            unemployed = None

        # Extract Social Grades data
        social_grades_div = soup.find('div', id='social-grades')
        if social_grades_div:
            ab_grade = social_grades_div.find_all('li')[0].find('strong').text.strip()
            c2_grade = social_grades_div.find_all('li')[1].find('strong').text.strip()
            de_grade = social_grades_div.find_all('li')[2].find('strong').text.strip()
        else:
            ab_grade = None
            c2_grade = None
            de_grade = None

        # Extract Ethnicity data
        ethnicity_div = soup.find('header', string="ETHNICITY")
        if ethnicity_div:
            # Find the parent of the header and then target the list items
            ethnicity_section = ethnicity_div.find_parent().find_all('li')
            white = ethnicity_section[0].find('strong').text.strip()
            non_white = ethnicity_section[1].find('strong').text.strip()
        else:
            white = None
            non_white = None

        return {
            "working": working,
            "unemployed": unemployed,
            "ab_grade": ab_grade,
            "c2_grade": c2_grade,
            "de_grade": de_grade,
            "white": white,
            "non_white": non_white
    }


class DemographicsCalculator:
    @staticmethod

    def average_demographics(demo_list):
        # Initialize cumulative sums and counts
        total_population = 0
        total_households = 0
        total_unemployment_rate = 0
        total_avg_income = 0
        total_working = 0
        total_unemployed = 0
        total_ab_grade = 0
        total_c2_grade = 0
        total_de_grade = 0
        total_white = 0
        total_non_white = 0
        
        for demo in demo_list:
            # Convert values to proper types for calculations
            total_population += int(demo['total_population'].replace(',', ''))
            total_households += int(demo['households'].replace(',', ''))
            print("demo['unemployment_rate']",demo['unemployment_rate'])
            # Convert unemployment_rate to float and divide by 100
            total_unemployment_rate += float(demo['unemployment_rate'].strip('%')) / 100  
            # total_unemployment_rate += float(demo['unemployment_rate'].strip('%')) / 100 
            
            # Convert avg_household_income to int for average calculation
            total_avg_income += int(demo['avg_household_income'].replace('£', '').replace(',', ''))
            
            # Convert percentages for working, unemployed, ab, c1/c2, de, white, non-white to float and divide by 100
            total_working += int(demo['working'].strip('%'))  # Keep as percentage for average
            total_unemployed += int(demo['unemployed'].strip('%'))  # Keep as percentage for average
            total_ab_grade += int(demo['ab_grade'].strip('%'))  # Keep as percentage for average
            total_c2_grade += int(demo['c2_grade'].strip('%'))  # Keep as percentage for average
            total_de_grade += int(demo['de_grade'].strip('%'))  # Keep as percentage for average
            total_white += int(demo['white'].strip('%'))  # Keep as percentage for average
            total_non_white += int(demo['non_white'].strip('%'))  # Keep as percentage for average

        print("total_unemployment_rate:",total_unemployment_rate)
        count = len(demo_list)
        
        # Calculate averages
        average_data = {
            "population": total_population // count,
            "households": total_households // count,
            "unemployment_rate": round(total_unemployment_rate / count, 4),  # Round to 4 decimal places
            "avg_household_income": total_avg_income // count,
            "working": round(total_working // count, 2),  # Round to 2 decimal places
            "unemployed": round(total_unemployed // count, 2),  # Round to 2 decimal places
            "ab": round(total_ab_grade // count, 2),  # Round to 2 decimal places
            "c1/c2": round(total_c2_grade // count, 2),  # Round to 2 decimal places
            "de": round(total_de_grade // count, 2),  # Round to 2 decimal places
            "white": round(total_white // count, 2),  # Round to 2 decimal places
            "non-white": round(total_non_white // count, 2)  # Round to 2 decimal places
        }
        
        # Convert percentages to decimal format
        average_data["working"] /= 100
        average_data["unemployed"] /= 100
        average_data["ab"] /= 100
        average_data["c1/c2"] /= 100
        average_data["de"] /= 100
        average_data["white"] /= 100
        average_data["non-white"] /= 100

        return average_data



class WebScraper:
    def __init__(self, url, directory_path):
        self.url = url
        self.directory_path = directory_path
        self.outer_code_list = []
        self.demographics_list = []
        print(self.directory_path)

    def perform_web_actions(self, postcode,radius):
        """Performs actions using WebDriverManager."""
        driver_manager = WebDriverManager(self.url)
        driver_manager.input_radius_and_postcode(postcode,radius)
        sleep(2)
        driver_manager.click_on_search()
        driver_manager.click_on_save_csv()
        sleep(2)
        driver_manager.quit()

    def extract_demographics(self):
        """Extracts demographics for all outer codes."""
        self.outer_code_list=CSVHandler.load_csv_get_postcodes(self.directory_path)
        print(self.outer_code_list)
        for outer_code in self.outer_code_list:
            outer_code = ''.join([char.upper() if char.isalpha() else char for char in outer_code])
            try:
                url = f'https://www.postcodearea.co.uk/postaltowns/uxbridge/{outer_code}/'

                response = requests.get(url)
                response.raise_for_status()  # Ensure we get a valid response
                soup = BeautifulSoup(response.content, 'html.parser')

                demographics = DemographicsExtractor.extract_demographics(soup)
                additional_data = DemographicsExtractor.extract_additional_data(soup)

                combined_data = {**demographics, **additional_data}
                self.demographics_list.append(combined_data)
                print("postcode", outer_code, "combined_data", combined_data)
            except Exception as e:
                print(e)
                continue

        # Calculate average demographics
        final_average_data = DemographicsCalculator.average_demographics(self.demographics_list)
        return final_average_data


if __name__ == "__main__":
    url = 'https://www.freemaptools.com/find-uk-postcodes-inside-radius.htm#google_vignette'
    postcode = "OX2 0DH"
    directory_path = 'D:/work/automation/free_map_tools/downloaded_csv'
    # Usage
    scraper = WebScraper(url=url, directory_path=directory_path)

    # To perform web actions for a specific postcode
    scraper.perform_web_actions(postcode=postcode)

    # To extract demographics
    average_data = scraper.extract_demographics()
    print("Final Average Data:", average_data)

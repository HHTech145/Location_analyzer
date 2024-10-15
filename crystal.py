

import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import re 
import json 
import tempfile

class WebDriverHelper:
    def __init__(self, url):
        self.url = url
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        """Initializes the Chrome WebDriver with specific options."""
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Optional, for better performance
        options.add_argument("--window-size=1920x1080")  # Optional, set window size
        options.add_argument("--window-position=-2400,-2400")
        options.add_argument('--start-maximized')
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def load_page(self):
        """Loads the web page and waits for it to be ready."""
        self.driver.get(self.url)
        self.driver.execute_script("document.body.style.zoom='20%'")
        time.sleep(2)  # Adjust as necessary


    def click_show_more_restaurants(self):
        """Clicks the 'Show more' button for restaurants if it exists."""
        try:
            show_more_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]/button')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            time.sleep(1)
            show_more_button.click()
            time.sleep(2)
        except Exception as e:
            print("Could not find the 'Show more' button for restaurants:", e)

    def click_show_more_pubs(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        """Clicks the 'Show more' button for pubs if it exists."""
        try:
            show_more_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[5]/button')  # Replace with the actual XPath for pubs
            self.driver.execute_script("arguments[0].scrollIntoView(true);", show_more_button)
            time.sleep(1)
            show_more_button.click()
            time.sleep(2)
        except Exception as e:
            print("Could not find the 'Show more' button for pubs:", e)

    def get_restaurant_data(self):
        """Extracts restaurant data from the page and returns it as a DataFrame."""
        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]')
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

        restaurant_list = soup.find('ul', class_='f4_a h6_a h6_d h6_g')
        
        if restaurant_list:
            data = []
            for item in restaurant_list.find_all('li', class_='h6_b'):
                span = item.find('span', class_='h6_c').find_next('span')
                name = span.get_text(strip=True)
                distance = span.find('span', class_='hq_a').get_text(strip=True)
                data.append({'Restaurant': name, 'Distance': distance})
            
            df_restaurants = pd.DataFrame(data)
            return df_restaurants
        else:
            print("No restaurant list found.")
            return pd.DataFrame()  # Return an empty DataFrame if no data is found

    def get_pubs_data(self):
        """Extracts pub data from the page and returns it as a DataFrame."""
        # self.click_show_more_pubs()  # Clicks the 'Show more' button specific to pubs

        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[5]')
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

        pub_list = soup.find('ul', class_='f4_a h6_a h6_d h6_g')  # Adjust class names as needed based on page structure
        
        if pub_list:
            data = []
            for item in pub_list.find_all('li', class_='h6_b'):
                span = item.find('span', class_='h6_c').find_next('span')
                name = span.get_text(strip=True)
                distance = span.find('span', class_='hq_a').get_text(strip=True)
                data.append({'Pub': name, 'Distance': distance})
            
            df_pubs = pd.DataFrame(data)
            return df_pubs
        else:
            print("No pub list found.")
            return pd.DataFrame()

    def store_data_as_json(self, postcode, restaurant_data, pub_data,demo_df):
        """Stores restaurant and pub data in JSON format against the given postcode."""
        # Create a dictionary structure
        data = {
            postcode: {
                'demographics': demo_df.to_dict(orient='records'),
                'restaurants': restaurant_data.to_dict(orient='records'),
                'pubs': pub_data.to_dict(orient='records')

            }
        }
        
        # Save to a JSON file
        filename = f"{postcode}_data.json"
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Data saved to {filename}")

        
    # Function to split the restaurant name from the distance
    def split_name_distance(self,row):
        # Use regex to find the first occurrence of digits in the string
        match = re.search(r'\d+', row)
        if match:
            # Split at the starting index of the first digit
            return row[:match.start()].strip(), row[match.start():].strip()
        return row, ""  # Return the row as is if no match

    def close(self):
        """Closes the WebDriver."""
        self.driver.quit()

class Crystal:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.df_demographic = None

    def fetch_content(self):
        """Fetches HTML content from the given URL and initializes the BeautifulSoup object."""
        response = requests.get(self.url)
        response.raise_for_status()  # Ensure we get a valid response
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def extract_demographics(self):
        """Extracts demographic data and converts it into a pandas DataFrame."""
        data = []
        demographic_divs = self.soup.find_all('div', class_='ha_h')

        for entry in demographic_divs:
            label = entry.find('span', class_='hw_a').get_text(strip=True)
            percentage = entry.find('span', class_='ha_j').find_all('span')[-1].get_text(strip=True)
            data.append({'Demographics': label, 'Percentage': percentage})

        # Convert to DataFrame and clean Percentage column
        self.df_demographic = pd.DataFrame(data)
        self.df_demographic['Percentage'] = self.df_demographic['Percentage'].replace('%', '', regex=True).astype(float)

    def display_data(self):
        """Displays the demographic data."""
        print("_________________________________________")
        print(self.df_demographic)

        return self.df_demographic



def fetch_demographics(url):
    # url = "https://crystalroof.co.uk/report/postcode/TS14AW/demographics"
    crystal = Crystal(url)
    crystal.fetch_content()
    crystal.extract_demographics()
    demo_df=crystal.display_data()
    return demo_df

def fetch_amenities(postcode,url,demo_df):

    # url = "https://crystalroof.co.uk/report/postcode/TS14AW/amenities"
    web_helper = WebDriverHelper(url)
    web_helper.load_page()
    web_helper.click_show_more_restaurants()
    df_restaurants = web_helper.get_restaurant_data()

    # Apply the function to split the Restaurant column
    df_restaurants[['Restaurant', 'Distance']] = df_restaurants['Restaurant'].apply(lambda x: pd.Series(web_helper.split_name_distance(x)))

    print(df_restaurants)

        # Fetch pub data
    web_helper.click_show_more_pubs()
    
    df_pubs = web_helper.get_pubs_data()
    df_pubs[['Pub', 'Distance']] = df_pubs['Pub'].apply(lambda x: pd.Series(web_helper.split_name_distance(x)))
    print(df_pubs)

    web_helper.close()

    web_helper.store_data_as_json(postcode=postcode,restaurant_data=df_restaurants,pub_data=df_pubs,demo_df=demo_df)
    # return df_restaurants



if __name__ == "__main__":
    # Usage example
    postcode="TS14AW"
    url = f"https://crystalroof.co.uk/report/postcode/{postcode}/demographics"
    demo_df=fetch_demographics(url)
    url=f"https://crystalroof.co.uk/report/postcode/{postcode}/amenities"
    fetch_amenities(postcode,url,demo_df)

    # Usage example

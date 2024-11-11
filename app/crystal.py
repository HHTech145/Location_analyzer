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
        
    def click_on_borough_button(self):
        # /html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[4]/div/div[1]/ul/li[2]/button
        # """Clicks the 'Show more' button for restaurants if it exists."""
        try:
            borough_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[4]/div/div[1]/ul/li[2]/button')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", borough_button)
            time.sleep(1)
            borough_button.click()
            time.sleep(2)
        except Exception as e:
            print("Could not find the 'Show more' button for restaurants:", e)

    def get_occupation_data(self):
        try:
            occupation_text_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[3]')
            text_soup = BeautifulSoup(occupation_text_div.get_attribute('innerHTML'), 'html.parser')


            # Extract the paragraph text with class 'hv_a'
            location_text = text_soup.find('p', class_='hv_a').get_text(strip=True)  

            show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[4]')
            soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

            # Find the div that contains the occupations section
            occupation_section = soup.find('div', class_='ha_e')
            if occupation_section:
                occupations = []
                
                # Find all the occupation rows and borough values
                occupation_rows = occupation_section.find_all('div', class_='ha_h')
                for row in occupation_rows:
                    occupation_name = row.find('span', class_='hw_b').get_text(strip=True)
                    borough_value = row.find_all('span')[-1].get_text(strip=True)  # Get the value for the Borough

                    occupations.append({
                        'Occupation': occupation_name,
                        'Percentage': borough_value
                    })

                # Convert to DataFrame for easy analysis
                df_occupations = pd.DataFrame(occupations)
                print("df_occupations_----_____________________________________:",df_occupations,"\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                return df_occupations,location_text
            else:
                print("No occupations section found.")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error occurred while extracting occupations: {e}")
            return pd.DataFrame()
        
    def get_transport_data(self):
        print("----------------------------------------------------------------------------------------------------------------------------------------------/////////////")
        occupation_text_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]')
        soup = BeautifulSoup(occupation_text_div.get_attribute('innerHTML'), 'html.parser')
        # Initialize dictionary to hold the extracted information
        # connectivity_data = {}
        # stations_data = []
        # # Check if the 'Connectivity to public transport' section exists
        # connectivity_div = soup.find('div', class_='es_a')
        # transport_score=""
        # travel_zone=""
        # if connectivity_div:
        #     # Extracting connectivity rating
        #     connectivity_info = connectivity_div.find('div', class_='ig_a dz_a dz_d es_b')
        #     if connectivity_info:
        #         transport_text = connectivity_info.find('p', class_='hu_a dz_e').text.strip()
        #         transport_score = connectivity_info.find('div', class_='hs_a es_c').text.strip()
        #         print(f"{transport_text}: {transport_score}")
            
        #     # Extracting travel zone
        #     travel_zone_info = connectivity_div.find('div', class_='ig_a dz_a es_g')
        #     if travel_zone_info:
        #         travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
        #         travel_zone = travel_zone_info.find('div', class_='hs_a').text.strip()
        #         print(f"{travel_text}: {travel_zone}")
            
        #         # Adding connectivity information to dictionary

        #     connectivity_data = {
        #         "connectivity to public transport": transport_score,
        #         "travel zone": travel_zone
        #     }
        # else:
        #     print("Connectivity to public transport information is not available.")

        # # Find all the station details
        # stations = []
        # # Find all the station details and group them by station name
        # for station in soup.find_all('li', class_='er_c'):
        #     station_name = station.find('p', class_='er_e').text.strip()
        #     distance = station.find('span', class_='er_f').text.strip()
        #     # lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary
        #     # Extract lines
        #     lines = [span.text.strip() for span in station.find_all('span', class_='er_j')]
        #     s = ""
        #     if len(lines) > 1:
        #         for i, line in enumerate(lines):
        #             s += line
        #             if i < len(lines) - 1:
        #                 s += ","
        #     else:
        #         s = lines[0]
        #     print(s)
        #     # Add to the stations_data dictionary
        #     stations_data[station_name] = {"distance": distance, "lines": s}

        # # Create DataFrame for connectivity
        # connectivity_df = pd.DataFrame([connectivity_data])

        # # Create DataFrame for stations
        # stations_df = pd.DataFrame.from_dict(stations_data, orient='index')
        # # Display extracted stations
        # for name, dist in stations:
        #     print(f"Station: {name}, Distance: {dist}")
        connectivity_data = {}
        stations_data = []

        # Check if the 'Connectivity to public transport' section exists
        connectivity_div = soup.find('div', class_='es_a')
        transport_score=""
        travel_zone=""
        if connectivity_div:
            # Extracting connectivity rating
                    # price_blocks = soup.find_all('div', class_=lambda x: x and 'bn' in x and 'de' in x and 'e1' in x,
                    #                 attrs={'data-baseweb': 'block'})
            connectivity_info = connectivity_div.find('div', class_=lambda x: x and 'ig_a' in x and 'dz_a' in x)
            if connectivity_info:
                transport_text = connectivity_info.find('p', class_='hu_a dz_e').text.strip()
                transport_score = connectivity_info.find('div', class_='hs_a es_c').text.strip()
                print("####################################in scraper @##########################################################s")
                print(f"{transport_text}: {transport_score}")
            
            # Extracting travel zone
            travel_zone_info = connectivity_div.find('div', class_='ig_a dz_a es_g')
            if travel_zone_info:
                travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
                travel_zone = travel_zone_info.find('div', class_='hs_a').text.strip()
                print(f"{travel_text}: {travel_zone}")

                # Adding connectivity information to dictionary
                connectivity_data = {
                    "connectivity to public transport": transport_score,
                    "travel zone": travel_zone
                }
        else:
            print("Connectivity to public transport information is not available.")

        # Find all the station details and group them by station name
        for station in soup.find_all('li', class_='er_c'):
            # station_name = station.find('p', class_='er_e').text.strip()
            station_name = station.find('p', class_='er_e').contents[0].strip()
            # Use regex to capture everything before the numeric value
            # match = re.match(r'^(.*?)(?=\s*\d+(\.\d+)?\s*miles?)', station_name)

            # Get the matched group if it exists
            # station_name = match.group(1).strip() if match else ""
            distance = station.find('span', class_='er_f').text.strip()
            # lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary
            # Extract lines
            lines = [span.text.strip() for span in station.find_all('span', class_='er_j')]
            s = ""
            if len(lines) > 1:
                for i, line in enumerate(lines):
                    s += line
                    if i < len(lines) - 1:
                        s += ","
            else:
                s = lines[0]
            print(s)
            # Add to the stations_data dictionary
            stations_data.append({
                "station_name": station_name,
                "distance": distance,
                "lines": s
            })

        # Create DataFrame for connectivity
        connectivity_df = pd.DataFrame([connectivity_data])

        # Create DataFrame for stations
        stations_df = pd.DataFrame(stations_data, columns=['station_name', 'distance', 'lines'])

        # connectivity_df = pd.DataFrame([connectivity_data])
        # stations_df = pd.DataFrame(stations_data)

        print(connectivity_df.head)
        print(stations_df.head)
        return connectivity_df,stations_df


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
        print("------------------------------------------------------",self.df_demographic)
        self.df_demographic['Percentage'] = self.df_demographic['Percentage'].replace('%', '', regex=True).astype(float)

    def display_data(self):
        """Displays the demographic data."""
        print("_________________________________________")
        print(self.df_demographic)

        return self.df_demographic



# class OccupationReport:
#     def __init__(self, url):
#         self.url = url
#         self.soup = None
#         self.fetch_data()

#     def fetch_data(self):
#         try:
#             response = requests.get(self.url)
#             response.raise_for_status()  # Ensure the request was successful
#             self.soup = BeautifulSoup(response.text, 'html.parser')
#         except requests.exceptions.RequestException as e:
#             print(f"Error occurred while fetching the webpage: {e}")

#     def get_borough_occupations(self):
#         if not self.soup:
#             return pd.DataFrame()

#         try:
#             # Find the div that contains the occupations section
#             occupation_section = self.soup.find('div', class_='ha_e')
#             if occupation_section:
#                 occupations = []
                
#                 # Find all the occupation rows and borough values
#                 occupation_rows = occupation_section.find_all('div', class_='ha_h')
#                 for row in occupation_rows:
#                     occupation_name = row.find('span', class_='hw_b').get_text(strip=True)
#                     borough_value = row.find_all('span')[-1].get_text(strip=True)  # Get the value for the Borough

#                     occupations.append({
#                         'Occupation': occupation_name,
#                         'Borough Value': borough_value
#                     })

#                 # Convert to DataFrame for easy analysis
#                 df_occupations = pd.DataFrame(occupations)
#                 print("df_occupations_----_____________________________________:",df_occupations,"\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#                 return df_occupations
#             else:
#                 print("No occupations section found.")
#                 return pd.DataFrame()

#         except Exception as e:
#             print(f"Error occurred while extracting occupations: {e}")
#             return pd.DataFrame()


class HouseholdIncomeScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
    
    # Method to fetch and parse HTML
    def fetch_page(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Check if the request was successful
            self.soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching the webpage: {e}")
            self.soup = None
    
    def separate_local(self,text):
        # Use regex to find a pattern of a word followed by 'local'
        # Use regex to find a word followed by 'local'
        updated_text = re.sub(r'(\w+)(local)', r'\1 \2', text)
        return updated_text
    # Method to scrape neighbourhood, borough, and London income data
    def get_neighbourhood_income(self):
        if not self.soup:
            return pd.DataFrame()

        try:
            income_section = self.soup.find('div', class_='ha_e')
            if income_section:
                # Extract Neighbourhood income and value
                neighbourhood_data = income_section.find('div', class_='ha_n')
                neighbourhood_name = neighbourhood_data.find('span', class_='hw_b').get_text(strip=True)
                neighbourhood_value = neighbourhood_data.find_all('span')[-1].get_text(strip=True)

                # Extract Kingston upon Thames borough income and value
                borough_data = income_section.find_all('div', class_='ha_h')[1]
                borough_name = borough_data.find('span', class_='hw_b').get_text(strip=True)
                print(borough_name)
                borough_name=self.separate_local(borough_name)
                print("-----------------------------London Name:",borough_name)
                borough_value = borough_data.find_all('span')[-1].get_text(strip=True)

                # Extract London income and value
                london_data = income_section.find_all('div', class_='ha_h')[2]
                london_name = london_data.find('span', class_='hw_b').get_text(strip=True)
                print("-----------------------------London Name:",london_name)
                london_value = london_data.find_all('span')[-1].get_text(strip=True)

                # Extract comparison text
                comparison_section = self.soup.find('p', class_='hv_a')
                comparison_text = comparison_section.get_text(strip=True) if comparison_section else "No comparison data found"

                # Prepare data
                data = {
                    'Area': [neighbourhood_name, borough_name, london_name, 'Comparison Text'],
                    'Income': [neighbourhood_value, borough_value, london_value, comparison_text]
                }
                df_neighbourhood_income = pd.DataFrame(data)
                return df_neighbourhood_income
            else:
                print("No income section found.")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error occurred while extracting neighbourhood income: {e}")
            return pd.DataFrame()

    # Method to scrape household income and rating
    def get_household_income(self):
        if not self.soup:
            return pd.DataFrame()

        try:
            # Search for the section that contains the household income information, flexible for class 'gd_a gd_f' or 'gd_a gd_e'
            income_estimate_section = self.soup.find('div', class_=['gd_a', 'gd_f', 'gd_e'])

            if income_estimate_section:
                # Extract the income estimate by looking for the span containing the relevant value
                income_value_element = income_estimate_section.find('span', class_='f7_a')
                income_value = income_value_element.get_text(strip=True) if income_value_element else "No income data found"

                # Extract the income rating (if available)
                income_rating_element = income_estimate_section.find('span', class_='hs_a')
                income_rating = income_rating_element.get_text(strip=True) if income_rating_element else "No rating found"

                # Prepare the data
                data = {
                    'income': income_value,
                    'rating': income_rating
                }

                # Convert the data into a DataFrame
                df_household_income = pd.DataFrame([data])
                return df_household_income
            else:
                print("No household income section found.")
                return pd.DataFrame()

        except Exception as e:
            print(f"Error occurred while extracting household income: {e}")
            return pd.DataFrame()

    def get_address(self):
        if not self.soup:
            return ""

        try:
            # Find the navigation section that contains the address
            address_nav = self.soup.find('nav', class_='h4_a c6_a')
            if address_nav:
                # Extract the address components from the list items
                address_components = [li.get_text(strip=True) for li in address_nav.find_all('li')]
                full_address = ', '.join(address_components)  # Join components with a comma
                return full_address
            else:
                print("No address navigation found.")
                return ""

        except Exception as e:
            print(f"Error occurred while extracting address: {e}")
            return ""
        
    # Method to call both scraping methods and combine results
    def scrape_income_data(self):
        self.fetch_page()

        if self.soup:
            df_neighbourhood_income = self.get_neighbourhood_income()
            df_household_income = self.get_household_income()
            full_address = self.get_address()
            print("##################################################################",full_address)
            # Combine the DataFrames    
            # combined_df = pd.concat([df_neighbourhood_income, df_household_income], ignore_index=True)
            return df_household_income,df_neighbourhood_income,full_address
        else:
            print("Soup not available. Failed to fetch the page.")
            return pd.DataFrame()




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

# def fetch_transport(postcode,url):
#     print(postcode)

    # web_helper.click_show_more_restaurants()




if __name__ == "__main__":
    # Usage example
    postcode="TS14AW"
    url = f"https://crystalroof.co.uk/report/postcode/{postcode}/demographics"
    demo_df=fetch_demographics(url)
    url=f"https://crystalroof.co.uk/report/postcode/{postcode}/amenities"
    fetch_amenities(postcode,url,demo_df)
    url=f"https://crystalroof.co.uk/report/postcode/{postcode}/transport"
    fetch_transport(postcode,url)
    # Usage example

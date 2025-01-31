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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback
from selenium.common.exceptions import TimeoutException, NoSuchElementException


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
        options.add_argument("--log-level=3")  # Suppress logging
        options.add_argument("--disable-logging")  # Disable all logging
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
            
            show_more_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]/button'))
            )
            # show_more_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]/button')
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
        print("--------- in restraunts -------------------------------")
        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]')
        # /html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[6]
        # time.sleep(1000)
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

        # print(soup.prettify())
        # restaurant_list = soup.find('ul', class_='f4_a h6_a h6_d h6_g')
                                                    #  gb_a h8_a h8_d h8_g
        # restaurant_list = soup.find('ul', class_='gb_a h8_a h8_d h8_g')
        # if restaurant_list:
        #     data = []
        #     for item in restaurant_list.find_all('li', class_='h8_b'):
        #         span = item.find('span', class_='h8_c').find_next('span')
        #         name = span.get_text(strip=True)
        #         distance = span.find('span', class_='hr_a').get_text(strip=True)
        # Find the unordered list containing restaurant data
        restaurant_list = soup.find('ul', attrs={'data-unordered-list': 'true'})
        # print("---------------------number of ---",restaurant_list,len(restaurant_list))
        if restaurant_list:
            data = []
            
            # Loop through each list item
            for item in restaurant_list.find_all('li', attrs={'data-unordered-item': 'true'}):
                # Extract restaurant name
                name_span = item.find('span', attrs={'data-amenity-item': 'true'})
                name = name_span.get_text(strip=True)

                # Extract distance
                distance_span = name_span.find('span', attrs={'data-color-ghost': 'true'})
                distance = distance_span.get_text(strip=True) if distance_span else "N/A"
                data.append({'Restaurant': name, 'Distance': distance})
            
            df_restaurants = pd.DataFrame(data)
            # print("restraimts ---------------------------------------------------",df_restaurants)
            return df_restaurants
        else:
            print("No restaurant list found.")
            return pd.DataFrame()  # Return an empty DataFrame if no data is found

    def get_pubs_data(self):
        """Extracts pub data from the page and returns it as a DataFrame."""
        # self.click_show_more_pubs()  # Clicks the 'Show more' button specific to pubs

        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]/div[5]')
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

        # pub_list = soup.find('ul', class_='gb_a h8_a h8_d h8_g')   #soup.find('ul', class_='f4_a h6_a h6_d h6_g')  # Adjust class names as needed based on page structure
        
        # if pub_list:
        #     data = []
        #     # for item in pub_list.find_all('li', class_='h6_b'):
        #     #     span = item.find('span', class_='h6_c').find_next('span')
        #     #     name = span.get_text(strip=True)
        #     #     distance = span.find('span', class_='hq_a').get_text(strip=True)
        #     for item in pub_list.find_all('li', class_='h8_b'):
        #         span = item.find('span', class_='h8_c').find_next('span')
        #         name = span.get_text(strip=True)
        #         distance = span.find('span', class_='hr_a').get_text(strip=True)
        pub_list = soup.find('ul', attrs={'data-unordered-list': 'true'})
        
        if pub_list:
            data = []
            
            # Loop through each list item
            for item in pub_list.find_all('li', attrs={'data-unordered-item': 'true'}):
                # Extract restaurant name
                name_span = item.find('span', attrs={'data-amenity-item': 'true'})
                name = name_span.get_text(strip=True)

                # Extract distance
                distance_span = name_span.find('span', attrs={'data-color-ghost': 'true'})
                distance = distance_span.get_text(strip=True) if distance_span else "N/A"

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
            borough_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Local Authority") or contains(text(), "Borough")]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", borough_button)
            time.sleep(1)
            borough_button.click()
            time.sleep(2)
            return False
        except Exception as e:
            print("Could not find the borough button:", traceback.format_exc())
            return True
            # time.sleep(20000)

    # def get_occupation_data(self,occupation_present):
    #     try:
    #         if occupation_present is False:
    #             occupation_text_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[3]')
    #             text_soup = BeautifulSoup(occupation_text_div.get_attribute('innerHTML'), 'html.parser')


    #             # Extract the paragraph text with class 'hv_a'
    #             location_text = text_soup.find('p', class_='h8_a').get_text(strip=True)  
    #             print("location text :________",location_text)

    #             show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[5]')
    #             print("show more div -----------------------------",show_more_div)
    #             # show_more_div = self.driver.find_element(By.XPATH, "//div[@id='__next']//main/article//div[.//h2[contains(text(), 'Occupations (NS-SEC)')]]")
    #             # //div[@id='__next']//main/article//div[.//h2[contains(text(), 'Occupations (NS-SEC)')]]
    #             # /html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[5]
    #             soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')
    #             print(soup.prettify())
    #             # Extract the occupation section
    #             occupation_section = soup.find('div', class_='hx_g')
    #             print("-----------------------------occupation ----------------------------",occupation_section)
    #             if occupation_section:
    #                 occupations = []
                    
    #                 # Find all rows for occupations
    #                 occupation_rows = occupation_section.find_all('div', class_='hx_h')
    #                 print("occupation rows lens --------------------:",len(occupation_rows))
    #                 for row in occupation_rows:
    #                     # Extract the occupation name, ignoring the inner div
    #                     print("row ----------------------",row)
    #                     occupation_name = row.find('span', class_='h9_a h9_b').find('span').get_text(strip=True)
    #                     # jc_a f_a
    #                     # Extract the percentage value (e.g., 49%, 28%)
    #                     percentage_value = row.find_all('span')[-1].get_text(strip=True)
                        
    #                     # Append the data to the list
    #                     occupations.append({
    #                         'Occupation': occupation_name,
    #                         'Percentage': percentage_value
    #                     })
                    
    #                 # Convert the list to a DataFrame for easier analysis
    #                 df_occupations = pd.DataFrame(occupations)

    #                 print("df_occupations_----_____________________________________:",df_occupations,"\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    #                 # time.sleep(10000)
    #                 return df_occupations,location_text
    #             else:
    #                 occupation_text_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[3]')
    #                 text_soup = BeautifulSoup(occupation_text_div.get_attribute('innerHTML'), 'html.parser')
    #                 # Extract the paragraph text with class 'hv_a'
    #                 location_text = text_soup.find('p', class_='h8_a').get_text(strip=True)  
    #                 return pd.DataFrame(),location_text
    #         else:
    #             print("No occupations section found.")
    #             return pd.DataFrame(),""

    #     except Exception as e:
    #         print(f"Error occurred while extracting occupations: {e}")
    #         self.close()
    #         return pd.DataFrame(),""

    def get_occupation_data(self, occupation_present):
        try:
            if not occupation_present:
                # Get location text
                location_text_xpath = '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[3]//p'
                location_text_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, location_text_xpath))
                )
                location_text = location_text_element.text.strip()
                print("Location text: ", location_text)

                # Click on "Show More" if necessary
                show_more_xpath = '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[5]'
                try:
                    show_more_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, show_more_xpath))
                    )
                    show_more_button.click()
                    time.sleep(2)  # Allow time for content to load
                except Exception as e:
                    print("Show More button not found or not clickable:", e)

                # Extract occupation data
                occupation_rows_xpath = '/html/body/div[2]/div[2]/main/article/div[2]/div[3]/div/div[4]/div/div[2]/div/div/div'
                occupation_rows = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, occupation_rows_xpath))
                )


                occupations = []
                for row in occupation_rows:
                    try:
                        # Extract occupation name and percentage
                        full_text = row.text.strip()
                        
                        # Split name and percentage correctly
                        parts = full_text.rsplit('\n', 1)  # Splitting from the right to ensure only last part is percentage
                        if len(parts) == 2:
                            occupation_name, percentage = parts
                        else:
                            occupation_name, percentage = full_text, ""

                        print(f"Extracted: {occupation_name} - {percentage}")  # Debugging line

                        occupations.append({'Occupation': occupation_name.strip(), 'Percentage': percentage.strip()})
                    except Exception as e:
                        print("Error extracting occupation data:", e)

                df_occupations = pd.DataFrame(occupations)
                print("Extracted Occupation Data:\n", df_occupations)

                return df_occupations, location_text


                # occupations = []
                # for row in occupation_rows:
                #     try:
                #         # Extract occupation name
                #         occupation_name_xpath = './/span[contains(@data-bar-chart-label, "true")]'
                #         occupation_name_element = row.find_element(By.XPATH, occupation_name_xpath)
                #         occupation_name = occupation_name_element.text.strip()

                #         # Extract percentage value
                #         percentage_xpath = './/span[contains(@data-bar-chart-value, "true")]'
                #         percentage_element = row.find_element(By.XPATH, percentage_xpath)
                #         percentage = percentage_element.text.strip()

                #         print(f"Extracted: {occupation_name} - {percentage}")  # Debugging line

                #         occupations.append({'Occupation': occupation_name, 'Percentage': percentage})
                #     except Exception as e:
                #         print("Error extracting occupation data:", e)

                # df_occupations = pd.DataFrame(occupations)
                # print("Extracted Occupation Data:\n", df_occupations)

                # return df_occupations, location_text
            else:
                print("No occupations section found.")
                return pd.DataFrame(), ""

        except Exception as e:
            print(f"Error occurred while extracting occupations: {e}")
            self.close()
            return pd.DataFrame(), ""
        
    # def clean_station_data(self,station):
    #     """ Helper function to clean and format station data """
    #     try:
    #         # Extract the station name (remove distance part if it's in the station name)
    #         station_name = station.split(" ")[0]  # e.g., "Devons" from "Devons Road 1.0"
            
    #         # Extract the distance (e.g., "Road 1.0")
    #         distance = " ".join(station.split(" ")[1:3])  # e.g., "1.0 miles"
            
    #         # Extract transport lines (this might need more handling if your data contains different formats)
    #         lines = [line.strip() for line in station.split(',') if line.strip()]
            
    #         return station_name, distance, lines
    #     except Exception as e:
    #         print(f"Error cleaning station data: {e}")
    #         return "", "", []

    def clean_station_data(self,station):
        """ Helper function to clean and format station data """
        try:
            # Split the string by spaces
            station_parts = station.split(" ")
            
            # Extract the station name (Join all parts except the last two as the station name)
            if len(station_parts) > 2:
                station_name = " ".join(station_parts[:-2])  # All parts except the last two
            else:
                station_name = station_parts[0]  # If there's only one part, treat it as station name
            
            # Extract the distance (last two parts, including "miles")
            distance = " ".join(station_parts[-2:])  # Get the last two parts (distance part)
            
            # Clean lines: here we want to remove any numeric and "miles" parts from the lines.
            lines = [station_name]  # Start with station name in the lines
            
            # If there are any other lines, process them. We'll assume they are part of the station's transport lines.
            # If there is more data (like other transport lines), they should follow the station name
            remaining_lines = " ".join(station_parts[0:-2]).strip()  # Exclude the last two parts (distance)
            
            # Check if remaining lines are not empty
            if remaining_lines and remaining_lines != station_name:
                lines.append(remaining_lines)
            return station_name, distance, lines
        
        except Exception as e:
            print(f"Error cleaning station data: {e}")
            return "", "", []    



    def get_transport_data(self):
        print("----------------------------------------------------------------------------------------------------------------------------------------------/////////////")
        
        # Assuming `self.driver` is initialized elsewhere
        
        # Wait for the connectivity section to load
        try:
            # Wait for the section containing Connectivity and Travel Zone to be present
            connectivity_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//main/article/div[2]/div[1]/div[3]/div'))
            )
            
            # Extract Connectivity to Public Transport
            try:
                connectivity_score_element = self.driver.find_element(
                    By.XPATH, '//*[text()="Connectivity to public transport"]/following-sibling::div//strong'
                )
                transport_score = connectivity_score_element.text.strip()
                print("Connectivity Score: ", transport_score)
            except Exception as e:
                print(f"Error extracting Connectivity Score: {e}")
                transport_score = "N/A"
            
            # Extract Travel Zone
            try:
                # Wait for the Travel Zone element to be present using the provided XPath
                travel_zone_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//main/article/div[2]/div[1]/div[3]/div/div[2]/div'))
                )

                # Extract the text and strip any excess whitespace
                travel_zone = travel_zone_element.text.strip()
                print(f"Travel Zone: {travel_zone}")
            except Exception as e:
                print(f"Error extracting Travel Zone: {e}")
                travel_zone = "N/A"

            # Return the data as a dictionary
            connectivity_data = {
                "connectivity to public transport": transport_score,
                "travel zone": travel_zone
            }

        except Exception as e:
            print(f"Error extracting connectivity information: {e}")
            connectivity_data = {"connectivity to public transport": "N/A", "travel zone": "N/A"}

        
        # Find all stations using XPath for station list (no class name)
        stations_data = []
        try:
            # Wait for the station list section to load
            station_list_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//main/article/div[2]/div[1]/div[5]'))
            )
            
            # Find all station list items (li elements)
            stations = station_list_div.find_elements(By.XPATH, './/li')
            
            for station in stations:
                try:
                    # Extract station name and distance
                    station_name_distance = station.find_element(By.XPATH, './/p').text.strip()  # Extract text from the <p> tag
                    
                    # Split the text into station name and distance (last part)
                    station_name, distance = station_name_distance.rsplit(' ', 1)  # Split only from the right

                    # Use regular expression to find the decimal number
                    match = re.search(r'\d+\.\d+', station_name)

                    # Check if a match is found and print it
                    if match:
                        decimal_number = match.group(0)
                        print(decimal_number)
                        distance=decimal_number+" miles"
                    
                    station_name= re.sub(r'\s\d+\.\d+', '', station_name)

                    # Extract transport lines (span elements with transport names)
                    lines_elements = station.find_elements(By.XPATH, './/span[not(contains(text(),"miles"))]')
                    lines = [line.text.strip() for line in lines_elements if line.text.strip()]
                    
                    # Print the cleaned details
                    print(f"Station: {station_name}, Distance: {distance}, Lines: {lines}")
                    
                    # Add cleaned data to list
                    stations_data.append({
                        "station_name": station_name,
                        "distance": distance,
                        "lines": ", ".join(lines)  # Join the lines into a single string
                    })
                    
                except Exception as e:
                    print(f"Error extracting station data: {e}")
            
        except Exception as e:
            print(f"Error extracting station list: {e}")

            
        # Create DataFrames for connectivity and stations data
        connectivity_df = pd.DataFrame([connectivity_data])
        stations_df = pd.DataFrame(stations_data, columns=['station_name', 'distance', 'lines'])
        
        # Debug print to show data
        print(connectivity_df.head())
        print(stations_df.head())
        
        return connectivity_df, stations_df

    # def get_transport_data(self):
    #     print("----------------------------------------------------------------------------------------------------------------------------------------------/////////////")
        
    #     # Assuming `self.driver` is initialized elsewhere
    #     occupation_text_div = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/article/div[2]/div[1]')
        
    #     # Extract connectivity information
    #     connectivity_data = {}
        
    #     try:
    #         # Connectivity Information
    #         connectivity_div = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/article/div[2]/div[1]/div[2]')
            
    #         # Extract Transport Score (Using position and text)
    #         transport_score = self.driver.find_element(By.XPATH, './/div[contains(text(), "Transport Score")]/following-sibling::div').text.strip()
    #         print("Connectivity Score: ", transport_score)
            
    #         # Extract Travel Zone (Using position and text)
    #         travel_zone = self.driver.find_element(By.XPATH, './/div[contains(text(), "Travel Zone")]/following-sibling::div').text.strip()
    #         print(f"Travel Zone: {travel_zone}")
            
    #         connectivity_data = {
    #             "connectivity to public transport": transport_score,
    #             "travel zone": travel_zone
    #         }
    #     except Exception as e:
    #         print(f"Error extracting connectivity information: {e}")
        
    #     # Find all stations using XPath for station list (no class name)
    #     stations_data = []
        
    #     try:
    #         # XPath to find the station list container (using its position)
    #         station_list_div = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/article/div[2]/div[1]/div[5]')
            
    #         # Find all station list items (li elements)
    #         stations = station_list_div.find_elements(By.XPATH, './/li')
            
    #         for station in stations:
    #             try:
    #                 # Extract station name (find <p> tag directly under each <li>)
    #                 station_name = station.find_element(By.XPATH, './/p').text.strip()
                    
    #                 # Extract distance (assuming it's under a <span> or <div>)
    #                 distance = station.find_element(By.XPATH, './/span | .//div').text.strip()
                    
    #                 # Extract transport lines (looking for <span> or <div> within <li>)
    #                 lines = station.find_elements(By.XPATH, './/span | .//div')
    #                 lines_str = ", ".join([line.text.strip() for line in lines]) if lines else "Unknown"
                    
    #                 # Print the station details
    #                 print(f"Station: {station_name}, Distance: {distance}, Lines: {lines_str}")
                    
    #                 # Add station data to the list
    #                 stations_data.append({
    #                     "station_name": station_name,
    #                     "distance": distance,
    #                     "lines": lines_str
    #                 })
    #             except Exception as e:
    #                 print(f"Error extracting station data: {e}")
            
    #     except Exception as e:
    #         print(f"Error extracting station list: {e}")
        
    #     # Create DataFrames for connectivity and stations data
    #     connectivity_df = pd.DataFrame([connectivity_data])
    #     stations_df = pd.DataFrame(stations_data, columns=['station_name', 'distance', 'lines'])
        
    #     # Debug print to show data
    #     print("connectivity -----------------------------------------------------",connectivity_df.head())
    #     print(stations_df.head())
        
    #     return connectivity_df, stations_df

    # def get_transport_data(self):
    #     print("----------------------------------------------------------------------------------------------------------------------------------------------/////////////")
    #     occupation_text_div = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/main/article/div[2]/div[1]')
    #     soup = BeautifulSoup(occupation_text_div.get_attribute('innerHTML'), 'html.parser')
    #     # Initialize dictionary to hold the extracted information
    #     # connectivity_data = {}
    #     # stations_data = []
    #     # # Check if the 'Connectivity to public transport' section exists
    #     # connectivity_div = soup.find('div', class_='es_a')
    #     # transport_score=""
    #     # travel_zone=""
    #     # if connectivity_div:
    #     #     # Extracting connectivity rating
    #     #     connectivity_info = connectivity_div.find('div', class_='ig_a dz_a dz_d es_b')
    #     #     if connectivity_info:
    #     #         transport_text = connectivity_info.find('p', class_='hu_a dz_e').text.strip()
    #     #         transport_score = connectivity_info.find('div', class_='hs_a es_c').text.strip()
    #     #         print(f"{transport_text}: {transport_score}")
            
    #     #     # Extracting travel zone
    #     #     travel_zone_info = connectivity_div.find('div', class_='ig_a dz_a es_g')
    #     #     if travel_zone_info:
    #     #         travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
    #     #         travel_zone = travel_zone_info.find('div', class_='hs_a').text.strip()
    #     #         print(f"{travel_text}: {travel_zone}")
            
    #     #         # Adding connectivity information to dictionary

    #     #     connectivity_data = {
    #     #         "connectivity to public transport": transport_score,
    #     #         "travel zone": travel_zone
    #     #     }
    #     # else:
    #     #     print("Connectivity to public transport information is not available.")

    #     # # Find all the station details
    #     # stations = []
    #     # # Find all the station details and group them by station name
    #     # for station in soup.find_all('li', class_='er_c'):
    #     #     station_name = station.find('p', class_='er_e').text.strip()
    #     #     distance = station.find('span', class_='er_f').text.strip()
    #     #     # lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary
    #     #     # Extract lines
    #     #     lines = [span.text.strip() for span in station.find_all('span', class_='er_j')]
    #     #     s = ""
    #     #     if len(lines) > 1:
    #     #         for i, line in enumerate(lines):
    #     #             s += line
    #     #             if i < len(lines) - 1:
    #     #                 s += ","
    #     #     else:
    #     #         s = lines[0]
    #     #     print(s)
    #     #     # Add to the stations_data dictionary
    #     #     stations_data[station_name] = {"distance": distance, "lines": s}

    #     # # Create DataFrame for connectivity
    #     # connectivity_df = pd.DataFrame([connectivity_data])

    #     # # Create DataFrame for stations
    #     # stations_df = pd.DataFrame.from_dict(stations_data, orient='index')
    #     # # Display extracted stations
    #     # for name, dist in stations:
    #     #     print(f"Station: {name}, Distance: {dist}")
    #     connectivity_data = {}
    #     stations_data = []

    #     # Check if the 'Connectivity to public transport' section exists
    #     connectivity_div = soup.find('div', class_='e8_a')
    #     transport_score=""
    #     travel_zone=""
    #     if connectivity_div:
    #         # Extracting connectivity rating
    #                 # price_blocks = soup.find_all('div', class_=lambda x: x and 'bn' in x and 'de' in x and 'e1' in x,
    #                 #                 attrs={'data-baseweb': 'block'}) ii_a d7_a d7_d ez_b
    #                 # it_a eg_a eg_b e8_b
    #         connectivity_info = connectivity_div.find('div', class_=lambda x: x and 'it_a' in x and 'eg_a' in x)
    #         if connectivity_info:
    #             # transport_text = connectivity_info.find('p', class_='hv_a d7_e').text.strip()
    #             transport_score = connectivity_info.find('div', class_='h2_a e8_c').text.strip()
    #             print("####################################in scraper @##########################################################s")
    #             # print(f"{transport_text}: {transport_score}")
            
    #         # Extracting travel zone
    #         travel_zone_info = connectivity_div.find('div', class_='it_a eg_a e8_g')
    #         if travel_zone_info:
    #             # travel_text = travel_zone_info.find('p', class_='hu_a dz_e').text.strip()
    #             travel_zone = travel_zone_info.find('div', class_='h2_a').text.strip()
    #             print(f"Travel Zone: {travel_zone}")

    #             # Adding connectivity information to dictionary
    #             connectivity_data = {
    #                 "connectivity to public transport": transport_score,
    #                 "travel zone": travel_zone
    #             }
    #     else:
    #         print("Connectivity to public transport information is not available.")

    #     # Find all the station details and group them by station name
    #     for station in soup.find_all('li', class_='e7_c'):
    #         # station_name = station.find('p', class_='er_e').text.strip()
    #         station_name = station.find('p', class_='e7_e').contents[0].strip()
    #         # Use regex to capture everything before the numeric value
    #         # match = re.match(r'^(.*?)(?=\s*\d+(\.\d+)?\s*miles?)', station_name)

    #         # Get the matched group if it exists
    #         # station_name = match.group(1).strip() if match else ""
    #         distance = station.find('span', class_='e7_f').text.strip()
    #         # lines = [line.text.strip() for line in station.find_all('span', class_='line_class')]  # Adjust class as necessary
    #         # Extract lines
    #         lines = [span.text.strip() for span in station.find_all('span', class_='e7_j')]
    #         s = ""
    #         if len(lines) > 1:
    #             for i, line in enumerate(lines):
    #                 s += line
    #                 if i < len(lines) - 1:
    #                     s += ","
    #         else:
    #             s = lines[0]
    #         print(s)
    #         # Add to the stations_data dictionary
    #         stations_data.append({
    #             "station_name": station_name,
    #             "distance": distance,
    #             "lines": s
    #         })

    #     # Create DataFrame for connectivity
    #     connectivity_df = pd.DataFrame([connectivity_data])

    #     # Create DataFrame for stations
    #     stations_df = pd.DataFrame(stations_data, columns=['station_name', 'distance', 'lines'])

    #     # connectivity_df = pd.DataFrame([connectivity_data])
    #     # stations_df = pd.DataFrame(stations_data)

    #     print(connectivity_df.head)
    #     print(stations_df.head)
    #     return connectivity_df,stations_df

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
        print("demographics -----------------------------------------------------------------------------------------------")
        try:
            """Extracts demographic data and converts it into a pandas DataFrame."""
            data = []
            # print(self.soup)
            # demographic_divs = self.soup.find_all('div', class_='hu_g')
            demographic_divs = self.soup.find_all('div', attrs={'data-bar-chart-item': True})

            print("demographic divs ----------------------------------",len(demographic_divs))
            # print(demographic_divs[0])
            for entry in demographic_divs:
                # print("--------------------------------------------------------------------------------------",entry)
                # label = entry.find('span', class_='hh_j').get_text(strip=True)
                # percentage = entry.find('span', class_='hx_a').find_all('span')[-1].get_text(strip=True)
                # label = entry.find('span', class_='hx_a').find('span').get_text(strip=True)
                # percentage = entry.find('span', class_='hh_j').find_all('span')[-1].get_text(strip=True)

                label_container = entry.find('span', attrs={'data-bar-chart-label': True})
                label = label_container.find('span').get_text(strip=True)
                # Extract percentage
                percentage = entry.find('span', attrs={'data-bar-chart-value': True}).get_text(strip=True)
            
                data.append({'Demographics': label, 'Percentage': percentage})
                # print("##########################################################",label,"--------------",percentage)
                # break

            # Convert to DataFrame and clean Percentage column
            self.df_demographic = pd.DataFrame(data)
            print(self.df_demographic)
            print("------------------------------------------------------------------------------------------------------------------")
            print("------------------------------------------------------",self.df_demographic)
            print("------------------------------------------------------------------------------------------------------------------")
            self.df_demographic['Percentage'] = self.df_demographic['Percentage'].replace('%', '', regex=True).astype(float)
        except Exception as e:
            print("Exceprino",traceback.format_exc())
            return pd.DataFrame()

    def display_data(self):
        """Displays the demographic data."""
        print("_________________________________________")
        print(self.df_demographic)

        return self.df_demographic





class HouseholdIncomeScraper:
    def __init__(self, url):
        self.house_income=WebDriverHelper(url)
        self.house_income.load_page()
        self.driver = self.house_income.driver
        
    
    # Method to fetch and parse HTML
    # def fetch_page(self):
    #     try:
    #         response = requests.get(self.url)
    #         response.raise_for_status()  # Check if the request was successful
    #         self.soup = BeautifulSoup(response.text, 'html.parser')
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error occurred while fetching the webpage: {e}")
    #         self.soup = None
    
    def separate_local(self,text):
        # Use regex to find a pattern of a word followed by 'local'
        # Use regex to find a word followed by 'local'
        updated_text = re.sub(r'(\w+)(local)', r'\1 \2', text)
        return updated_text
    # Method to scrape neighbourhood, borough, and London income data


    def get_neighbourhood_income(self):
        try:
            # Locate the main income section using the provided XPath
            income_section = self.driver.find_element(By.XPATH, '//main/article/div[2]/div[1]/div/div[4]/div')
            
            # Find all income items (divs that represent individual data points) using XPath
            income_items = income_section.find_elements(By.XPATH, './/div[@data-bar-chart-item="true"]')

            # Initialize lists to store extracted data
            areas = []
            incomes = []

            # Loop through all the income items
            for item in income_items:
                # Extract the area name (located inside a span within the div with data-bar-chart-item="true")
                area_name_element = item.find_element(By.XPATH, './/span[@data-bar-chart-label="true"]/span[1]')
                area_name = area_name_element.text.strip() if area_name_element else "No area name"

                # Extract the income value (second span within the div with data-bar-chart-item="true")
                income_value_element = item.find_element(By.XPATH, './/span[@data-bar-chart-value="true"]')
                income_value = income_value_element.text.strip() if income_value_element else "No income value"

                # Append extracted data to the lists
                areas.append(area_name)
                incomes.append(income_value)

            # Create and return a DataFrame from the extracted data
            data = {'Area': areas, 'Income': incomes}
            return pd.DataFrame(data)

        except Exception as e:
            print(f"Error occurred while extracting neighbourhood income: {e}")
            return pd.DataFrame()



    # def get_neighbourhood_income(self):
    #     if not self.soup:
    #         return pd.DataFrame()

    #     try:
    #         # Locate the main section containing income data
    #         income_section = self.soup.find('div', class_='hx_p')
    #         if not income_section:
    #             print("No income section found.")
    #             return pd.DataFrame()

    #         # Initialize lists to store extracted data
    #         areas = []
    #         incomes = []

    #         # Find all income items
    #         income_items = income_section.find_all('div', class_='hx_h')
    #         for item in income_items:
    #             # Extract the area name
    #             area_name_element = item.find('span', class_='h9_a h9_b')
    #             area_name = area_name_element.get_text(strip=True) if area_name_element else "No area name"

    #             # Extract the income value
    #             income_value_element = item.find('span', {'data-bar-chart-value': 'true'})
    #             income_value = income_value_element.get_text(strip=True) if income_value_element else "No income value"

    #             # Append to lists
    #             areas.append(area_name)
    #             incomes.append(income_value)

    #         # Create a DataFrame from the extracted data
    #         data = {'Area': areas, 'Income': incomes}
    #         return pd.DataFrame(data)

    #         # income_section = self.soup.find('div', class_='hx_p')
    #         # print("-- in income neigbbiourtbhod -----------------------------------------------------------------",income_section)
    #         # if income_section:
    #         #     # Extract Neighbourhood income and value
    #         #     neighbourhood_data = income_section.find('div', class_='hx_h')
    #         #     neighbourhood_name = neighbourhood_data.find('span', class_='h9a h9_b').get_text(strip=True)
    #         #     neighbourhood_value = neighbourhood_data.find_all('span')[-1].get_text(strip=True)

    #         #     # Extract Kingston upon Thames borough income and value
    #         #     borough_data = income_section.find_all('div', class_='hx_h')[1]
    #         #     borough_name = borough_data.find('span', class_='h9a h9_b').get_text(strip=True)
    #         #     print(borough_name)
    #         #     borough_name=self.separate_local(borough_name)
    #         #     print("-----------------------------London Name:",borough_name)
    #         #     borough_value = borough_data.find_all('span')[-1].get_text(strip=True)

    #         #     # Extract London income and value
    #         #     london_data = income_section.find_all('div', class_='hx_h')[2]
    #         #     london_name = london_data.find('span', class_='h9a h9_b').get_text(strip=True)
    #         #     print("-----------------------------London Name:",london_name)
    #         #     london_value = london_data.find_all('span')[-1].get_text(strip=True)

    #         #     # Extract comparison text
    #         #     comparison_section = self.soup.find('p', class_='h8_a')
    #         #     comparison_text = comparison_section.get_text(strip=True) if comparison_section else "No comparison data found"

    #         #     # Prepare data
    #         #     data = {
    #         #         'Area': [neighbourhood_name, borough_name, london_name, 'Comparison Text'],
    #         #         'Income': [neighbourhood_value, borough_value, london_value, comparison_text]
    #         #     }
    #         #     print(data)
    #         #     df_neighbourhood_income = pd.DataFrame(data)
    #         #     return df_neighbourhood_income
    #         # else:
    #         #     print("No income section found.")
    #         #     return pd.DataFrame()
    #     except Exception as e:
    #         print(f"Error occurred while extracting neighbourhood income: {e}")
    #         return pd.DataFrame()

    # Method to scrape household income and rating
    # def get_household_income(self):
    #     if not self.soup:
    #         return pd.DataFrame()

    #     try:
    #         # Search for the section that contains the household income information, flexible for class 'gd_a gd_f' or 'gd_a gd_e'
    #         # income_estimate_section = self.soup.find('div', class_=['gd_a', 'gd_f', 'gd_e'])
    #         income_estimate_section = self.soup.find('div', class_=['gw_a', 'gw_f', 'gk_e'])

    #         if income_estimate_section:
    #             # Extract the income estimate by looking for the span containing the relevant value
    #             income_value_element = income_estimate_section.find('span', class_='gq_a')
    #             income_value = income_value_element.get_text(strip=True) if income_value_element else "No income data found"

    #             # Extract the income rating (if available)
    #             income_rating_element = income_estimate_section.find('span', class_='h5_a')
    #             income_rating = income_rating_element.get_text(strip=True) if income_rating_element else "No rating found"

    #             # Prepare the data
    #             data = {
    #                 'income': income_value,
    #                 'rating': income_rating
    #             }

    #             # Convert the data into a DataFrame
    #             df_household_income = pd.DataFrame([data])
    #             return df_household_income
    #         else:
    #             print("No household income section found.")
    #             return pd.DataFrame()

    #     except Exception as e:
    #         print(f"Error occurred while extracting household income: {e}")
    #         return pd.DataFrame()


    # Method to scrape household income and rating
    # def get_household_income(self):
    #     if not self.soup:
    #         return pd.DataFrame()
    #     try:
    #         income_section = self.driver.find_element(By.XPATH, 'html/body/div[2]/div[2]/main/article/div[2]/div[1]/div/div[3]')
            
    #         if income_section:
    #             # Parse the inner HTML using BeautifulSoup
    #             soup = BeautifulSoup(income_section.get_attribute('innerHTML'), 'html.parser')

    #             # Locate the income value
    #             income_value_element = soup.find('p', {'data-tile-value': 'true'})
    #             income_value = income_value_element.find('span').get_text(strip=True) if income_value_element else "No income data found"

    #             # Locate the income rating
    #             income_rating_element = soup.find('div', {'data-tile-score': 'true'})
    #             income_rating = income_rating_element.find('span').get_text(strip=True) if income_rating_element else "No rating found"

    #             # Prepare the data
    #             data = {
    #                 'income': income_value,
    #                 'rating': income_rating
    #             }

    #             # Convert the data into a DataFrame
    #             df_household_income = pd.DataFrame([data])
    #             return df_household_income
    #         else:
    #             print("No household income section found.")
    #             return pd.DataFrame()

    #     except Exception as e:
    #         print(f"Error occurred while extracting household income: {e}")
    #         return pd.DataFrame()
        
    def get_household_income(self):
        try:
            # Define XPath for the household income section
            income_section_xpath = '//main/article/div[2]/div[1]/div/div[3]/div'

            # Wait for the section to be present
            income_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, income_section_xpath))
            )

            # Extract household income value
            income_value_xpath = f"{income_section_xpath}//p[@data-tile-value='true']/span"
            income_value_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, income_value_xpath))
            )
            income_value = income_value_element.text.strip() if income_value_element else "No income data found"

            # Extract household income rating
            income_rating_xpath = f"{income_section_xpath}//div[@data-tile-score='true']/span"
            income_rating_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, income_rating_xpath))
            )
            income_rating = income_rating_element.text.strip() if income_rating_element else "No rating found"

            # Debugging prints
            print(f"Extracted Income: {income_value}")
            print(f"Extracted Rating: {income_rating}")

            # Store in a DataFrame
            data = {
                'income': [income_value],
                'rating': [income_rating]
            }
            df_household_income = pd.DataFrame(data)

            return df_household_income

        except Exception as e:
            print(f"Error extracting household income: {e}")
            return pd.DataFrame()



    def get_address(self):
        if not self.driver:
            return ""

        try:
            # Use XPath to locate the navigation element
            address_nav_xpath = "//main/article/div[2]/div[1]/div/div[2]/div/nav"
            address_nav = self.driver.find_element(By.XPATH, address_nav_xpath)

            # Extract text from all <li> elements within the navigation
            address_components = [
                li.text.strip() for li in address_nav.find_elements(By.TAG_NAME, "li")
            ]
            full_address = ", ".join(address_components)  # Join components with a comma
            return full_address

        except NoSuchElementException:
            print("No address navigation found.")
            return ""
        except Exception as e:
            print(f"Error occurred while extracting address: {e}")
            return ""



    # def get_address(self):
    #     if not self.soup:
    #         return ""

    #     try:
    #         # Find the navigation section by targeting the <nav> tag directly ij_a dk_a dc_b
    #         address_nav = self.soup.find('nav', class_='ij_a dk_a dc_b')
    #         if address_nav:
    #             # Extract the address components from the <li> elements
    #             address_components = [
    #                 li.get_text(strip=True) for li in address_nav.find_all('li')
    #             ]
    #             full_address = ', '.join(address_components)  # Join components with a comma
    #             return full_address
    #         else:
    #             print("No address navigation found.")
    #             return ""
    #     except Exception as e:
    #         print(f"Error occurred while extracting address: {e}")
    #         return ""
        
    # Method to call both scraping methods and combine results
    def scrape_income_data(self):
        # self.fetch_page()

        # if self.soup:
        try:
            df_neighbourhood_income = self.get_neighbourhood_income()
            df_household_income = self.get_household_income()
            full_address = self.get_address()
            print("##################################################################",full_address)
            # Combine the DataFrames    
            # combined_df = pd.concat([df_neighbourhood_income, df_household_income], ignore_index=True)
            return df_household_income,df_neighbourhood_income,full_address
        # else:
        except Exception as e:
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
    # fetch_transport(postcode,url)
    # Usage example

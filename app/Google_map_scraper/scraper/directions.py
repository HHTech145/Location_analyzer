
# from time import sleep
# from .base import Base
# from .scroller import Scroller
import threading
import undetected_chromedriver as uc
# from .settings import DRIVER_EXECUTABLE_PATH
# from .communicator import Communicator
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

DRIVER_EXECUTABLE_PATH ="D:/work/automation/free_map_tools/final/Location_analyzer/app/Google_map_scraper/chromedriver.exe"

class Directions:
    def __init__(self):
        self.driver=self.init_driver()

    def init_driver(self):
            options = uc.ChromeOptions()
            # if self.headlessMode:
            options.headless = False

            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_argument('--incognito')
            options.add_experimental_option("prefs", prefs)

            # Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

            try:
                if DRIVER_EXECUTABLE_PATH is not None:
                    self.driver = uc.Chrome(
                        driver_executable_path=DRIVER_EXECUTABLE_PATH, options=options)
                    # 51.03874808377282, 0.8538329627877123
                    # Location location = new Location(latitude, longitude, altitude);
                    # params = {
                    #         "latitude": 51.03874808377282,
                    #         "longitude": 0.8538329627877123,
                    #         "accuracy": 1
                    #     }
                        
                    # self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

                else:
                    self.driver = uc.Chrome(options=options)
                return self.driver

            except NameError:
                self.driver = uc.Chrome(options=options)

    # get directions
    def click_directions(self):
        sleep(5)
        # button = self.driver.find_element(By.XPATH, "//button[@data-value='Directions']")
        # Locate the button using its class or other attributes
        try:
            button = self.driver.find_element(By.CLASS_NAME, "g88MCb")
            # directions = self.driver.find_element(
                # By.XPATH,"/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[4]/div[1]/button")
            button.click()
            sleep(5)
        except Exception as e:
            print("in directions click error ",e)


    # find place
    def find(self,postcode):
        sleep(6)
        # find = self.driver.find_element(
        # By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[1]/div[2]/div[1]/div/input")
        # find.send_keys(postcode)
        # Locate the input field using a reliable locator
        input_field = self.driver.find_element(By.CSS_SELECTOR, "input.tactile-searchbox-input")
        input_field.send_keys(postcode)
        input_field.send_keys(Keys.ENTER)
        sleep(5)
        # self.driver
        # search = self.driver.find_element(
        # By.XPATH, "/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[1]/div[2]/button[1]")
        # search.click()

        # get transportation details
    def kilometers(self):
        # Wait for the desired element to load
        try:
            # Locate the specific div (use more specific attributes as needed)
            # div_element = self.driver.find_element(By.CLASS_NAME, "m6QErb")
            div_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'm6QErb') and contains(@class, 'XiKgde')]"))
            )
            # customization_blocks = meal_item.find_all('div', class_=lambda x: x and 'd1' in x and 'cd' in x )

            # Get the HTML content of the div
            div_html = div_element.get_attribute("outerHTML")
            # print(div_html)
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(div_html, 'html.parser')


            # Find all divs with the "UgZKXd" class
            divs = soup.find_all('div', class_='UgZKXd')

            results = []

                # Process each div
            # Process each div
            for div in divs:
                # Safely find the span and its aria-label
                travel_mode_span = div.find('span', class_='Os0QJc google-symbols')
                travel_mode = travel_mode_span['aria-label'] if travel_mode_span and travel_mode_span.has_attr('aria-label') else None

                if travel_mode and travel_mode != "Transit":  # Exclude Transit
                    # Safely find and extract text from other elements
                    time_div = div.find('div', class_='Fk3sm')
                    time = time_div.text.strip() if time_div else "N/A"

                    distance_div = div.find('div', class_='ivN21e')
                    distance = distance_div.text.strip() if distance_div else "N/A"

                    route_h1 = div.find('h1')
                    route = route_h1.text.strip() if route_h1 else "N/A"

                    results.append({'travel_mode': travel_mode, 'time': time, 'distance': distance, 'route': route})
                else:
                    results.append({'travel_mode': '', 'time': '', 'distance': '', 'route': ''})

            # Output the filtered results
            for result in results:
                print(result)

            

            # # Extract required details
            # details = {
            #     "time": soup.find('div', class_='Fk3sm').text.strip(),
            #     "distance": soup.find('div', class_='ivN21e').text.strip(),
            #     "route": soup.find('h1', class_='VuCHmb').text.strip(),
            #     "note": soup.find('span', class_='JxBYrc').text.strip() if soup.find('span', class_='JxBYrc') else None
            # }

            # # Print the extracted details
            # print(details)
            return results[0]

        except Exception as e:
            print(f"An error occurred: {e}")


    def process(self,url,postcode):
        # url="https://www.google.co.uk/maps/place/Central+Bedfordshire+College+-+Dunstable+Campus/data=!4m7!3m6!1s0x48764f03d1ab3ad7:0x5ad239e4e08889a1!8m2!3d51.890093!4d-0.5188035!16s%2Fm%2F02q32ds!19sChIJ1zqr0QNPdkgRoYmI4OQ50lo?authuser=0&hl=en&rclk=1"
        self.driver.get(url)
        self.click_directions()
        # postcode="LU5 6GZ"
        self.find(postcode)
        details=self.kilometers()
        # self.driver.quit()
        return details



# # Usage
# if __name__ == "__main__":
    # direction_obj=Directions()
    # url="https://www.google.co.uk/maps/place/Central+Bedfordshire+College+-+Dunstable+Campus/data=!4m7!3m6!1s0x48764f03d1ab3ad7:0x5ad239e4e08889a1!8m2!3d51.890093!4d-0.5188035!16s%2Fm%2F02q32ds!19sChIJ1zqr0QNPdkgRoYmI4OQ50lo?authuser=0&hl=en&rclk=1"
    # direction_obj.driver.get(url)
    # direction_obj.click_directions()
    # postcode="LU5 6GZ"
    # direction_obj.find(postcode)
    # direction_obj.kilometers()
    # details=direction_obj.process(url,postcode)






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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
# from database.data_json import JsonDataHandler
from datetime import datetime 
import logging
import traceback
import re 


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("uber_eats_scraper.log"),
        logging.StreamHandler()
    ]
)

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


    def click_on_date(self):
        date_button = WebDriverWait(self.driver, 100).until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[4]/div/div[2]/div/div/div/div[1]/input'))
        )
        date_button.click()
        sleep(10)

    # def click_on_order(self):
    #     sleep(5)
    #     date_button = WebDriverWait(self.driver, 100).until(
    #         EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]/div/div/table/tbody/tr[4]'))
    #         # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]/div/div/table/tbody/tr[3]/td[1]
    #     )
    #     date_button.click()
    #     sleep(10)


    def click_on_order(self,order_number): #/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[7]/div/div/table/tbody/tr[2]
        # order_number=3
        # sleep()
        # logging.info("Attempting to click on order number %s", order_number)
        # date_button = WebDriverWait(self.driver, 100).until( #/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[7]/div/div/table/tbody/tr[2]/td[1]
        #     EC.visibility_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[7]/div/div/table/tbody/tr[{order_number}]'))
        #     # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]/div/div/table/tbody/tr[3]/td[1]
        # )
        # date_button.click()
        # sleep(2)

        logging.info("Attempting to click on order number %s", order_number)
        try:
            date_button = WebDriverWait(self.driver, 100).until(
                EC.visibility_of_element_located(
                    (By.XPATH,f"//div[@data-tracking-name='element-visibility-wrapper']//table/tbody/tr[{order_number}]")

                                # "//div[@data-tracking-name='element-visibility-wrapper']//table/tbody/tr[{order_number}]"
                                # '/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]/div/div/table/tbody/tr[{order_number}]'

                )
            ) #          /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]
            date_button.click()
            logging.info("Clicked on order number %s", order_number)
            sleep(2)
        except Exception as e:
            logging.error("Error clicking on order number %s: %s", order_number, e)

    def check_active_order(self):
        try:
            sleep(5)
            # Locate the div containing the order count text 
            order_status_div = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[6]") 
            print("orders status:",order_status_div.text)
            logging.info("Order status text: %s", order_status_div.text)
            # Check if the div text contains the word "Orders" to determine if there are any active orders
            # if "0 Order" in order_status_div.text or "No live orders" in order_status_div.text:
            #     print("No active orders.")
            #     logging.info("No active orders.")
            #     return False  
            # else:
            #     logging.info("There is an active order.")
            #     print("There is an active order.")
            return True

        except Exception as e:
            logging.error("Error checking active order: %s", e)
            print("An error occurred:", e) 

    def extract_date_time(self,date_time_str):
        # Insert a space before the time part
        corrected_str = date_time_str[:9] + ' ' + date_time_str[9:]

        # Define the format
        date_time_format = "%m/%d/%Y %I:%M %p"

        try:
            # Parse the date and time
            date_time_obj = datetime.strptime(corrected_str, date_time_format)

            # # Extract date and time
            # date = date_time_obj.date()
            # time = date_time_obj.time()

            return date_time_obj
        except ValueError as e:
            print("Error parsing date and time:", e)
            return None, None

    def enhance_fulfilment(self,input_string):
        logging.info("Original fulfilment string: %s", input_string)
        # input_string = text #"DeliveryUber Eats"

        # Find the index where the second word starts
        split_index = input_string.index("Uber")

        # Separate the parts
        first_part = input_string[:split_index]
        second_part = input_string[split_index:]

        print("First part:", first_part)
        print("Second part:", second_part)
        logging.info("Enhanced fulfilment: %s %s", first_part, second_part)
        return first_part+" "+second_part

    def extract_pounds(self,input_string):
        # Remove the pound symbol and convert to float
        amount = float(input_string.replace('\u00a3', '').strip())
        return amount
                
    def get_order_information(self): # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[7]
        sleep(5)
        logging.info("Extracting order information...")
        try:    
            show_more_div = self.driver.find_element(By.XPATH, '//div[@data-tracking-name="element-visibility-wrapper"]')

                                                                # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8/]
            # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]
            # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]

            # print(show_more_div)
            soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')
            print(soup)

            orders = []
            # Locate all rows that contain order data
            rows = soup.find_all('tr', {'data-testid': 'ordersRevamped-row'})

            # Loop through each row and extract data
            for row in rows:
                cells = row.find_all('td')
                order_place_Date_time =cells[5].get_text(strip=True)
                delivery_date_time =cells[6].get_text(strip=True)
                # print(cells)
                try:
                    if len(cells) >0:  # Ensure there are enough columns in the row
                        
                        order_data = {
                            "Order ID": cells[0].get_text(strip=True),
                            "Store Details": cells[2].get_text(strip=True),
                            "Order placed time": order_place_Date_time,
                            "Delivery Time": delivery_date_time,
                            "Customer": cells[8].get_text(strip=True),
                            "Fulfilment": cells[10].get_text(strip=True),
                            "Courier": cells[12].get_text(strip=True),
                            "Subtotal": cells[14].get_text(strip=True)
                        }
                        orders.append(order_data)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    continue
            logging.info("Extracted order data: %s", orders)
            # Print extracted orders
            # for order in orders:
            #     print(order)
            return orders
        except Exception as e:
            logging.error("Error extracting order information: %s", traceback.format_exc())

    def get_contact_Details(self):
        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[4]/div')
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')
        # Extract phone number
        phone_number = soup.find("div", {"data-baseweb": "typo-monolabelmedium"}).text.strip()

        # Extract code
        code = soup.find("span", text="Code").find_next_sibling("span").text.strip()

        # Print extracted contact details
        print("Phone Number:", phone_number)
        print("Code:", code)


    def click_on_customization(self,count):
        # /html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[1]/ul[1]
        # /html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[1]/ul[1]/li/div[1]/div[2]/svg
        logging.info("Attempting to click the customization detail view...")
        try: 
            # First, wait for the close button to be present in the DOM
            close_button = WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[1]/ul[{count}]'))
            )
            
            # Then wait for it to be visible and clickable
            close_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of(close_button)
            )

            close_button.click()
            sleep(2)
            logging.info("Closed the order detail view.")
        
        except TimeoutException:
            logging.error("Timeout: Could not find or click the close button within the allotted time.")
        
        except NoSuchElementException:
            logging.error("NoSuchElementException: The close button is not present on the page.")
    
        except Exception as e:
                logging.error(f"Unexpected error when attempting to close the order detail view: {e}")



    def get_meal_Detais(self):
        logging.info("Extracting meal details...")
        try:
            show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[1]')
            soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')

            ul_elements = soup.find_all('ul', {'data-baseweb': 'accordion'})
            print("ul elements length:", len(ul_elements))
            meal_details = []
            count=0 
            if len(ul_elements)>0:
                for ul in ul_elements:
                    
                    meal_item = ul.select_one('li')

                    if meal_item:
                        meal_name = meal_item.select_one('div[data-baseweb="typo-labelmedium"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelmedium"]') else "N/A"
                        meal_price = meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]').get_text(strip=True) if meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]') else "N/A"
                        quantity = meal_item.select_one('div[data-baseweb="typo-labelsmall"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelsmall"]') else "N/A"
                        # Find the element by role attribute
                        button_element = meal_item.find('div', {'role': 'button'})

                        # Get the value of the 'aria-expanded' attribute
                        try:
                            aria_expanded_value = button_element.get('aria-expanded', None)
                            print("aria_expanded_value:",aria_expanded_value)
                            # if aria_expanded_value =="false":
                            #     self.click_on_customization(count)
                            #     sleep(2)
                            
                        except Exception as e:
                            print(e)
                        count=count+1
                        customizations = []
                        seen_customizations = set()
                        # print(meal_item.prettify())
                        # customization_blocks = meal_item.select_one('div[data-baseweb="block"]')
                        customization_blocks = meal_item.find_all('div', class_=lambda x: x and 'd1' in x and 'cd' in x ,
                                            attrs={'data-baseweb': 'block'})
                        
                        
                        # meal_item.select('div.d1.p1.cd[data-baseweb="block"]')
                        # print(customizations,"length:",len(customization_blocks))
                        # if customizations:


                        for customization in customization_blocks:
                            question = customization.select_one('p[data-baseweb="typo-paragraphsmall"]')

                            question_text = question.get_text(strip=True) if question else ''
                            # print(customization)``

                            if question_text:
                                if not question_text.startswith("Note: "):
                                    # Initialize options with price
                                    print(customization)
                                    option_with_prices = []
                                    # options = customization.select('div[data-baseweb="block"]')  # Select each option block
                                    options=customization.find_all('div', class_=lambda x: x and 'cu' in x and 'af' in x ,
                                            attrs={'data-baseweb': 'block'})
                                    # print(options)
                                    for option in options:
                                        option_name = option.select_one('div[data-baseweb="typo-labelmedium"]').get_text(strip=True) if option.select_one('div[data-baseweb="typo-labelmedium"]') else None
                                        print("option name :",option_name)
                                            # Check for price element and set to 0.00 if not found
                                        try:
                                            price_element = option.select_one('p[data-baseweb="typo-monoparagraphmedium"]')
                                            option_price = self.extract_pounds(price_element.get_text(strip=True)) if price_element else "0.00"\
                                                
                                            
                                            option_with_prices.append({
                                                'option': option_name,
                                                'price': option_price
                                            })
                                            print(price_element,option_price)
                                        except Exception as e:
                                            print(e)
                                    print(option_with_prices)
                                    # Only add if unique and not already seen, and option list is not empty
                                    if (question_text, tuple([opt['option'] for opt in option_with_prices])) not in seen_customizations and option_with_prices:
                                        customizations.append({
                                            'customization': question_text,
                                            'options': option_with_prices
                                        })
                                        seen_customizations.add((question_text, tuple([opt['option'] for opt in option_with_prices])))

                        meal_details.append({
                            'meal_name': meal_name,
                            'meal_price': self.extract_pounds(meal_price),
                            'quantity': quantity,
                            'customizations': customizations
                        })

            # Find all meal blocks
            # Print the entire soup for debugging
            # print("Soup content:", soup.prettify())
            # Find all relevant meal blocks specifically targeting the right structure 
            # class="ag ai am pt pv pw ob e9 cf ps "
            meal_blocks = soup.find_all('div', attrs={'class': 'ag ai am pa pb pc nq e9 cf pd'})  
            print("Number of meal blocks:", len(meal_blocks))
            
            # if len(meal_blocks)==0:
            #     meal_blocks = soup.find_all('div', attrs={'class': 'ag ai am pb pd pe nq e9 cf pa'}) #"ag ai am pe pf pg nv e9 cf ph
            # print("Number of meal blocks:", len(meal_blocks))
            # if len(meal_blocks)==0:
            #     meal_blocks = soup.find_all('div', attrs={'data-baseweb': 'block'})
            #     print("Number of meal blocks:", len(meal_blocks))
            if len(meal_blocks)==0:
                # meal_blocks = soup.find_all('div', class_=lambda x: x and 'ag' in x and 'ai' in x and 'am' in x,
                #                             attrs={'data-baseweb': 'block'})
                meal_blocks = soup.find_all('div', 
                            class_=re.compile(r'^\s*ag\s+ai\s+am\s+.*'), 
                            attrs={'data-baseweb': 'block'})
                print("Number of meal blocks:", len(meal_blocks))

            print("Number of meal blocks:", len(meal_blocks))
            # meal_blocks = soup.find_all('div', attrs={'data-baseweb': 'block'})

            # print("Number of meal blocks:", len(meal_blocks))

            if len(meal_blocks)>0:
                for meal_item in meal_blocks:
                    # Extract meal name, price, and quantity with default values if elements are missing
                    meal_name = meal_item.select_one('div[data-baseweb="typo-labelmedium"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelmedium"]') else "N/A"
                    meal_price = meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]').get_text(strip=True) if meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]') else "N/A"
                    quantity = meal_item.select_one('div[data-baseweb="typo-labelsmall"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelsmall"]') else "N/A"

                    # Append meal details to the list
                    meal_details.append({
                        'meal_name': meal_name,
                        'meal_price': self.extract_pounds(meal_price),
                        'quantity': quantity,
                        'customizations': []  # Add customizations handling if available in the HTML structure
                    })

            #     # Print meal details to verify
            #     print("Meal Details:", meal_details)
                    
            print("___________________________________________________________")
            # print(meal_details)

            # Print meal details to verify
            print("Meal Details:", meal_details)
            logging.info("Extracted meal details: %s", meal_details)
            return meal_details
        except Exception as e:
            logging.error("Error extracting meal details: %s", traceback.format_exc())


    # def get_meal_Detais(self):
    #     show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[1]')
    #     soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')


    #     ul_elements = soup.find_all('ul', {'data-baseweb': 'accordion'})
    #     print("ul elements length:",len(ul_elements))
    #     meal_details = []
    #     # Loop over each ul element
    #     for ul in ul_elements:
    #         # Find the li element containing meal details within the ul
    #         meal_item = ul.select_one('li')

    #         if meal_item:
    #             # Extract meal name, price, and quantity
    #             meal_name = meal_item.select_one('div[data-baseweb="typo-labelmedium"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelmedium"]') else "N/A"
    #             meal_price = meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]').get_text(strip=True) if meal_item.select_one('p[data-baseweb="typo-monoparagraphmedium"]') else "N/A"
    #             quantity = meal_item.select_one('div[data-baseweb="typo-labelsmall"]').get_text(strip=True) if meal_item.select_one('div[data-baseweb="typo-labelsmall"]') else "N/A"

    #             # Initialize list for customization options
    #             customizations = []
                
    #             # Find all customization question blocks within the meal item
    #             customization_blocks = meal_item.select('div[data-baseweb="block"]')


    #             for customization in customization_blocks:
    #                 question = customization.select_one('p[data-baseweb="typo-paragraphsmall"]')
    #                 if question:
    #                     print(question.get_text(strip=True))
    #                     # print(question.text())


    #                 if question and question.get_text(strip=True) == 'Choose your Flavour..':
    #                     # options = customization.select('div[data-baseweb="block"].pq.pr.ce.hi.ps.cu.af')
    #                     # flavours = [option.get_text(strip=True) for option in options if option.get_text(strip=True)]
    #                     # print(customization)
    #                     # option = customization.select_one('div[data-baseweb="typo-labelmedium"]')
    #                     # customizations.append({
    #                     #     'customization': question.get_text(strip=True),
    #                     #     'option': flavours
    #                     # })
    #                     options = customization.select('div.dy.bn.bp.de.df')  # Select divs with class for each flavor option
    #                     flavours = [option.get_text(strip=True) for option in options if option.get_text(strip=True)]
    #                     customizations.append({
    #                         'customization': question.get_text(strip=True),
    #                         'option': flavours
    #                     })
    #                 else:
    #                     option = customization.select_one('div[data-baseweb="typo-labelmedium"]')
    #                     if option:
    #                         customizations.append({
    #                             'customization': question.get_text(strip=True) if question else '',
    #                             'option': option.get_text(strip=True)
    #                         })               
    #             # # Loop through each customization block to extract questions and options
    #             # for customization in customization_blocks:
    #             #     question = customization.select_one('p[data-baseweb="typo-paragraphsmall"]')
    #             #     option = customization.select_one('div[data-baseweb="typo-labelmedium"]')
                    
    #             #     if question and option:
    #             #         customizations.append({
    #             #             'customization': question.get_text(strip=True),
    #             #             'option': option.get_text()
    #             #         })
                
    #             # Add extracted meal details to the meal_details list
    #             meal_details.append({
    #                 'meal_name': meal_name,
    #                 'meal_price': meal_price,
    #                 'quantity': quantity,
    #                 'customizations': customizations
    #             })
    #     print("___________________________________________________________")
    #     print(meal_details)

    #     # Remove duplicates in customizations for each meal
    #     for meal in meal_details:
    #         unique_customizations = {tuple(item.items()) for item in meal['customizations']}
    #         meal['customizations'] = [dict(item) for item in unique_customizations]

    #     # Print meal details to verify
    #     print("Meal Details:", meal_details)
            

    def get_order_details(self):
        sleep(5)
        logging.info("Attempting to retrieve order details...")
        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]')

        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')
        # print("Soup content:", soup.prettify())
        # Extract customer details
        # customer_name = soup.find('div', class_="bn bo bp df c7").get_text(strip=True)
        # order_count = soup.find('div', class_="bn bo e1 df cu").get_text(strip=True)

        # print(customer_name,order_count)

        order_steps = []
        for step in soup.select('ol[data-baseweb="progress-steps"] li'):
            # Extract the time
            time = step.select_one('div[data-baseweb="typo-labelmedium"]').get_text(strip=True)
            
            # Extract the description
            description = step.select_one('p[data-baseweb="typo-paragraphmedium"]').get_text(strip=True)
            
            # Add to the list of order steps
            order_steps.append({'time': time, 'description': description})
        
        print("order_Steps:\n",order_steps)
        logging.info("Order steps retrieved successfully.")
        logging.debug(f"Order Steps: {order_steps}")
        return order_steps


    def get_price_details(self):
        logging.info("Attempting to retrieve price details...")
        # Parse the HTML
        show_more_div = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/ul/li/div[2]/div/div[2]')
        soup = BeautifulSoup(show_more_div.get_attribute('innerHTML'), 'html.parser')
        # soup = BeautifulSoup(html, 'html.parser')
        # print("Soup content:", soup.prettify())
        # List to store price details
        price_details = []

        # Find all price blocks based on shared class patterns and data-baseweb attribute
        price_blocks = soup.find_all('div', class_=lambda x: x and 'bn' in x and 'de' in x and 'e1' in x,
                                    attrs={'data-baseweb': 'block'})

        # Extract price information
        for block in price_blocks:
            # Try to find the description and amount using <p> tags first
            description = block.find('p', attrs={'data-baseweb': 'typo-paragraphmedium'})
            amount = block.find('p', attrs={'data-baseweb': 'typo-monoparagraphmedium'})
            
            # If <p> tags were not found, look for <div> tags for "Net payout"
            if not description:
                description = block.find('div', attrs={'data-baseweb': 'typo-labellarge'})
            if not amount:
                amount = block.find('div', attrs={'data-baseweb': 'typo-monolabellarge'})

            # If both description and amount are found, add to price details
            if description and amount:
                price_details.append({
                    'description': description.get_text(strip=True),
                    'amount': self.extract_pounds(amount.get_text(strip=True))
                })

        # Print the extracted price details
        print("Price Details:", price_details)
        for detail in price_details:
            print(f"{detail['description']}: {detail['amount']}")

        logging.info("Price details retrieved successfully.")
        logging.debug(f"Price Details: {price_details}")
        
        return price_details
    
    # def click_on_close_detail(self):
    #     print("im in close _-----------------------------------------------------")
    #     logging.info("Attempting to close the order detail view...")
    #     close_button = WebDriverWait(self.driver, 100).until(
    #         EC.visibility_of_element_located((By.XPATH, f'/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[2]/button'))
    #         # /html/body/div[1]/div/div/div[1]/div/div[2]/div[2]/div[2]/div[8]/div/div/table/tbody/tr[3]/td[1]
    #     )
    #     close_button.click()
    #     sleep(2)
    #     logging.info("Closed the order detail view.")


    def click_on_close_detail(self):
        logging.info("Attempting to close the order detail view...")

        try:
                        # Assuming 'driver' is your WebDriver instance
            action = ActionChains(self.driver)
            action.send_keys(Keys.ESCAPE).perform()
        except Exception as e:
            print(e)
        # try:
        #     # First, wait for the close button to be present in the DOM
        #     close_button = WebDriverWait(self.driver, 100).until(
        #         EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div[2]/div[2]/button'))
        #     )
        #     # Then wait for it to be visible and clickable
        #     close_button = WebDriverWait(self.driver, 10).until(
        #         EC.visibility_of(close_button)
        #     )

        #     close_button.click()
        #     sleep(2)
        #     logging.info("Closed the order detail view.")
        
        # except TimeoutException:
        #     logging.error("Timeout: Could not find or click the close button within the allotted time.")
        
        # except NoSuchElementException:
        #     logging.error("NoSuchElementException: The close button is not present on the page.")
    
        # except Exception as e:
        #         logging.error(f"Unexpected error when attempting to close the order detail view: {e}")

    def controller(self,orders):
        for i in range(len(orders)):
            print(orders[i])
            print(i)
            order_id=orders[i]['Order ID']
            logging.info(f"Processing order {order_id} ({i+1}/{len(orders)})")
            try:
                self.click_on_order(order_number=2+i)
                order_steps=self.get_order_details()
                meal_details=self.get_meal_Detais()
                price_details=self.get_price_details()
                # json_handler.add_order(order_id, orders[i],order_steps,meal_details,price_details)
                sleep(2)
                self.click_on_close_detail()
                logging.info(f"Inserted order {order_id} into database.")
                # order_id="71039"
                print("________inserting into database")
                # json_handler.insert_order_into_database(order_id)
            except Exception as e:
                logging.error(f"Error processing order {order_id}: {traceback.format_exc()}")
        # json_handler.close_database() 
            

if __name__ == "__main__":
    # json_handler = JsonDataHandler('orders.json')

    db_config = {
        'host': '87.117.234.167',
        'user': 'py_isb',
        'password': '7iIG3.X/T(ObjTK8',
        'database': 'py_uber'
    }
    # Path to your JSON file
    json_file_path = "orders.json"

    # Example usage
    # json_handler = JsonDataHandler(json_file_path,db_config)    

    # print(json_handler)
    # url = 'https://merchants.ubereats.com/manager/orders'
    url="https://merchants.ubereats.com/manager/orders"
    driver_manager = WebDriverManager(url)
    while(1):
        try:
            active_status=driver_manager.check_active_order()
            logging.info(f"Checking for active orders...,{active_status}")
            if active_status:
                # sleep(2000)
                # json_handler = JsonDataHandler(json_file_path,db_config) 
                # print(json_handler)
                # logging.info(f"Database connection and status {json_handler}")
                orders=driver_manager.get_order_information()
                driver_manager.controller(orders)
                # driver_manager.click_on_order(order_number=3)
                # driver_manager.get_contact_Details()
                # driver_manager.get_order_details()
                # meal_details=driver_manager.get_meal_Detais()a
                # driver_manager.get_price_details()
                sleep(5)
            # driver_manager.driver.refresh()
            driver_manager.driver.execute_script("document.body.style.zoom='50%'")
            print("there is a refresh !!!!!!!!")
            logging.info("Refreshed the page.")
            sleep(10)
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {traceback.format_exc()}")
            print(e)
            continue
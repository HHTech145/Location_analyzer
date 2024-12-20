"""
This module contain the code for backend,
that will handle scraping process
"""

from time import sleep
from .base import Base
from .scroller import Scroller
import threading
import undetected_chromedriver as uc
from .settings import DRIVER_EXECUTABLE_PATH
# from .communicator import Communicator
from selenium.webdriver.common.by import By

class Backend(Base):
    

    def __init__(self, searchquery, outputformat,  healdessmode,output_file_name):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        outputpath: directory path where file will be stored after scraping
        headlessmode: it's value can be 0 and 1, 0 means unchecked box and 1 means checked

        """
        self.output_file_name=output_file_name

        self.searchquery = searchquery  # search query that user will enter
        
        # it is a function used as api for transfering message form this backend to frontend

        self.headlessMode = healdessmode

        self.init_driver()
        self.scroller = Scroller(driver=self.driver,output_file_name=self.output_file_name)



    def init_driver(self):
        options = uc.ChromeOptions()
        if self.headlessMode:
                options.headless = True

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

        except NameError:
            self.driver = uc.Chrome(options=options)
        
        
        

        # Communicator.show_message("Opening browser...")
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)



    def mainscraping(self):

        try:
            print("Execute First scraper.py --------------------------------------------------------------")
            querywithplus = "+".join(self.searchquery.split())

            """
            link of page variable contains the link of page of google maps that user wants to scrape.
            We have make it by inserting search query in it
            """

            link_of_page = f"https://www.google.co.uk/maps/search/{querywithplus}/"
            latitude="51.3119881"
            longitude="-0.6884529"
            zoom=0
            url = f"https://www.google.co.uk/maps/search/{querywithplus}/@{latitude},{longitude},{zoom}z?hl=en"
            # 51.3119881,-0.6884529,21635
            # ==========================================

            self.openingurl(url=link_of_page)
            print(url)
            sleep(10)
            # element=self.driver.find_element(By.CLASS_NAME, "searchboxinput")
            # element.send_keys(querywithplus)
            # element = self.driver.find_element(By.XPATH, '//*[@id="root"]/main/div[1]/div/div[1]/button')
            # element.click()
            # sleep(5)


            # Communicator.show_message("Working start...")

            sleep(1)

            self.scroller.scroll()
            

        except Exception as e:
            """
            Handling all errors.If any error occurs like user has closed the self.driver and if 'no such window' error occurs
            """
            # Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")


        finally:
            try:
                # Communicator.show_message("Closing the driver")
                self.driver.close()
                self.driver.quit()
            except:  # if browser is always closed due to error
                pass

            # Communicator.end_processing()
            # Communicator.show_message("Now you can start another session")




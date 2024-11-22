from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

from dataclasses import dataclass, asdict, field
import pandas as pd
import os
import asyncio
import sys
@dataclass
class Business:
    """Holds business data"""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None
    url: str = None

@dataclass
class BusinessList:
    """Holds a list of Business objects and provides methods for saving data"""
    business_list: list[Business] = field(default_factory=list)
    save_at: str = 'output'

    def dataframe(self):
        """Transforms business_list to a pandas dataframe"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_excel(self, filename):
        """Saves pandas dataframe to Excel (xlsx) file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """Saves pandas dataframe to CSV file"""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)


# class GoogleMapsScraper:
#     """Class for scraping business data from Google Maps"""

#     @staticmethod
#     def extract_coordinates_from_url(url: str) -> tuple[float, float]:
#         """Helper function to extract coordinates from URL"""
#         coordinates = url.split('/@')[-1].split('/')[0]
#         return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

#     @staticmethod
#     async def scrape(search_list,total):
#         """Main method to scrape business data for a given list of search queries"""
#         business_list = BusinessList()
#         print("in play wright ________________________________________",type(search_list),search_list)
#         # Use async_playwright() instead of sync_playwright()
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)
#             page = await browser.new_page()
#             print("in ____opening page --------------------------")

#             await page.goto("https://www.google.com/maps", timeout=60000)
#             await page.wait_for_timeout(5000)  # wait for dev phase, can remove in production
            
#             for search_for_index, search_for in enumerate(search_list):
#                 print(search_for)
#                 print(f"-----\n{search_for_index} - {search_for}".strip())

#                 await page.locator('//input[@id="searchboxinput"]').fill(search_for)
#                 await page.wait_for_timeout(3000)
#                 await page.keyboard.press("Enter")
#                 await page.wait_for_timeout(5000)

#                 await page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

#                 previously_counted = 0
#                 while True:
#                     await page.mouse.wheel(0, 10000)
#                     await page.wait_for_timeout(3000)

#                     locator = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]')
#                     # print("Locator:",locator.count())
#                     if await locator.count() >= total:
#                         listings = await locator.all()
#                         listings = listings[:total] 
#                         # listings = await locator.all()[:total]
#                         listings = [listing.locator("xpath=..") for listing in listings]
#                         print(f"Total Scraped: {len(listings)}")
#                         break
#                     else:
#                         if await locator.count() == previously_counted:
#                             listings = await locator.all()
#                             print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
#                             break
#                         else:
#                             previously_counted = await locator.count()
#                             print(f"Currently Scraped: {previously_counted}")

#                 for listing in listings:
#                     try:
#                         await listing.click()
#                         await page.wait_for_timeout(5000)

#                         name_xpath = '//div[contains(@class, "fontHeadlineSmall")]'
#                         address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
#                         website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
#                         phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
#                         reviews_span_xpath = '//span[@role="img"]'

#                         business = Business()
#                         # business.name = await listing.locator(name_xpath).all()[0].inner_text() if await listing.locator(name_xpath).count() > 0 else ""
#                         count = await listing.locator(name_xpath).count()  # Await count first
#                         if count > 0:
#                             all_listings = await listing.locator(name_xpath).all()
#                             business.name = await all_listings[0].inner_text()
#                         else:
#                             business.name = ""

#                         # Updating business.address, business.website, and business.phone_number
#                         address_count = await page.locator(address_xpath).count()
#                         if address_count > 0:
#                             address_elements = await page.locator(address_xpath).all()
#                             business.address = await address_elements[0].inner_text()
#                         else:
#                             business.address = ""

#                         website_count = await page.locator(website_xpath).count()
#                         if website_count > 0:
#                             website_elements = await page.locator(website_xpath).all()
#                             business.website = await website_elements[0].inner_text()
#                         else:
#                             business.website = ""

#                         phone_count = await page.locator(phone_number_xpath).count()
#                         if phone_count > 0:
#                             phone_elements = await page.locator(phone_number_xpath).all()
#                             business.phone_number = await phone_elements[0].inner_text()
#                         else:
#                             business.phone_number = ""

#                         # Updating reviews average and count
#                         if await listing.locator(reviews_span_xpath).count() > 0:
#                             reviews_elements = await listing.locator(reviews_span_xpath).all()
#                             reviews_info = await reviews_elements[0].get_attribute("aria-label")
#                             business.reviews_average = float(reviews_info.split()[0].replace(",", ".").strip())
#                             business.reviews_count = int(reviews_info.split()[2].replace(',', '').strip())
#                         else:
#                             business.reviews_average = ""
#                             business.reviews_count = ""

#                         # Business URL and coordinates
#                         business.url = page.url
#                         business_list.business_list.append(business)
#                     except Exception as e:
#                         print(f'Error occurred: {e}')

#             await browser.close()

#         return business_list



def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    """Helper function to extract coordinates from URL"""
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

class GoogleMapsScraper:
    """Class for scraping business data from Google Maps"""

    # @staticmethod
    # def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    #     """Helper function to extract coordinates from URL"""
    #     coordinates = url.split('/@')[-1].split('/')[0]
    #     return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

    @staticmethod
    def scrape(search_list, total=20):
        """Main method to scrape business data for a given list of search queries"""
        business_list = BusinessList()
        print("search_list",search_list)
        with sync_playwright() as p:
            print("in playwirght ____________________________________________________")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            print("_ in opening page -----------------------------------------")
            page.goto("https://www.google.com/maps", timeout=60000)
            # wait is added for dev phase. can remove it in production
            page.wait_for_timeout(5000)
            
            for search_for_index, search_for in enumerate(search_list):
                print(search_for)
                print(f"-----\n{search_for_index} - {search_for}".strip())

                page.locator('//input[@id="searchboxinput"]').fill(search_for)
                page.wait_for_timeout(3000)

                page.keyboard.press("Enter")
                page.wait_for_timeout(5000)

                # scrolling
                page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

                # this variable is used to detect if the bot
                # scraped the same number of listings in the previous iteration
                previously_counted = 0
                while True:
                    page.mouse.wheel(0, 10000)
                    page.wait_for_timeout(3000)

                    if (
                        page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).count()
                        >= total
                    ):
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()[:total]
                        listings = [listing.locator("xpath=..") for listing in listings]
                        print(f"Total Scraped: {len(listings)}")
                        break
                    else:
                        # logic to break from loop to not run infinitely
                        # in case arrived at all available listings
                        if (
                            page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            == previously_counted
                        ):
                            listings = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).all()
                            print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                            break
                        else:
                            previously_counted = page.locator(
                                '//a[contains(@href, "https://www.google.com/maps/place")]'
                            ).count()
                            print(
                                f"Currently Scraped: ",
                                page.locator(
                                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                                ).count(),
                            )

                business_list = BusinessList()

                # scraping
                for listing in listings:
                    try:
                        listing.click()
                        page.wait_for_timeout(5000)

                        name_xpath = '//div[contains(@class, "fontHeadlineSmall")]'
                        address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                        website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                        phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                        reviews_span_xpath = '//span[@role="img"]'

                        business = Business()

                        if listing.locator(name_xpath).count() > 0:
                            business.name = listing.locator(name_xpath).all()[0].inner_text()
                        else:
                            business.name = ""
                        if page.locator(address_xpath).count() > 0:
                            business.address = page.locator(address_xpath).all()[0].inner_text()
                        else:
                            business.address = ""
                        if page.locator(website_xpath).count() > 0:
                            business.website = page.locator(website_xpath).all()[0].inner_text()
                        else:
                            business.website = ""
                        if page.locator(phone_number_xpath).count() > 0:
                            business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text()
                        else:
                            business.phone_number = ""
                        if listing.locator(reviews_span_xpath).count() > 0:
                            business.reviews_average = float(
                                listing.locator(reviews_span_xpath).all()[0]
                                .get_attribute("aria-label")
                                .split()[0]
                                .replace(",", ".")
                                .strip()
                            )
                            business.reviews_count = int(
                                listing.locator(reviews_span_xpath).all()[0]
                                .get_attribute("aria-label")
                                .split()[2]
                                .replace(',','')
                                .strip()
                            )
                        else:
                            business.reviews_average = ""
                            business.reviews_count = ""
                        
                        business.latitude, business.longitude = extract_coordinates_from_url(page.url)
                        business.url=page.url
                        business_list.business_list.append(business)
                    except Exception as e:
                        print(f'Error occured: {e}')
                
                #########
                # output
                #########
                # business_list.save_to_excel(f"google_maps_data_{search_for}".replace(' ', '_'))
                # print(type(business_list))
                # print(business_list.pd.dataframe)
                # df=pd.DataFrame(business_list)
                # After scraping and appending business data
                business_dicts = [asdict(business) for business in business_list.business_list]


                # Convert to DataFrame
                df = pd.DataFrame(business_dicts)
                df_universities = df[['name', 'address', 'url']]
                print(df_universities,df_universities.columns)
                # print(df_universities.to_json())  # Output as JSON
                # print(df.head)
                
                # business_list.save_to_csv(f"google_maps_data_{search_for}".replace(' ', '_'))

            browser.close()


        
        return business_list
    

# from scraper import GoogleMapsScraper


def main():
    # Input parameters as strings
    search_list = ["Universities near Plasnewydd, CF24 3BJ"] 
    total = 10  # Number of listings to scrape

    # Scrape business data
    s= GoogleMapsScraper.scrape(search_list, total)
    print(s)
    # business_list = GoogleMapsScraper.scrape(search_list, total)

    # Save data to files
    # business_list.save_to_excel("google_maps_data")
    # business_list.save_to_csv("google_maps_data")

if __name__ == "__main__":
    main()
    # GoogleMapsScraper.scrape(sys.argv[1],tota/l=20)

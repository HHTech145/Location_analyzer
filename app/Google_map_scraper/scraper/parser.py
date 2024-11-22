from bs4 import BeautifulSoup
from .error_codes import ERROR_CODES
# from .communicator import Communicator
from .datasaver import DataSaver
from .base import Base
from .common import Common
from .directions import Directions

class Parser(Base):

    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
        "location": """Copy address""",
        "phone": """Copy phone number""",
        "website": """Open website""",
        }

    def init_data_saver(self):
        self.data_saver = DataSaver()
    
    def parse(self,web_url):
        """Our function to parse the html"""

        """This block will get element details sheet of a business. 
        Details sheet means that business details card when you click on a business in 
        serach results in google maps"""


        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")""")
        try:
            """If that information sheet is founded in try block, this block will run and find the contact details"""
            rating, totalReviews, address, websiteUrl, phone = (
                None,
                None,
                None,
                None,
                None,
            )  # by default they will be none

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(
                html, "html.parser"
            )  # soup of information  sheet of that place

            try:
                rating = soup.find("span", class_="ceNzKf").get("aria-label")

            except:  # if a business does not has rating
                rating = None

            try:
                totalReviews = list(soup.find("div", class_="F7nice").children)
                totalReviews = totalReviews[1].get_text(
                    strip=True
                )

            except:
                totalReviews = None

            name = soup.select_one(selector=".tAiQdd h1.DUwDvf").text.strip()

            allInfoBars = soup.find_all("button", class_="CsEnBe")

            for infoBar in allInfoBars:
                data_tooltip = infoBar.get("data-tooltip")
                text = infoBar.find('div', class_='rogA2c').text

                """Below three conditons are used to comapre fetched links to compare them with
                those links that we have write in start"""

                if data_tooltip == self.comparing_tool_tips["location"]:
                    address = text.strip()

                elif data_tooltip == self.comparing_tool_tips["website"]:
                    try:
                        websiteUrl = infoBar.parent.get("href")
                    except:
                        websiteUrl = None

                elif data_tooltip == self.comparing_tool_tips["phone"]:
                    phone = text.strip()

                else:
                    pass

            data = {
                "name": name,
                "Phone": phone,
                "address": address,
                "url": web_url,
                "reviews_count": totalReviews,
                "Rating": rating,
            }

            self.finalData.append(data)

        except Exception as e:  # some resuts have no information , so we dont want them in our pretty cleaned list
            print(f"Error occured while parsing a location. Error is: {str(e)}.", ERROR_CODES['ERR_WHILE_PARSING_DETAILS'] )
            # Communicator.show_error_message(f"Error occured while parsing a location. Error is: {str(e)}.", ERROR_CODES['ERR_WHILE_PARSING_DETAILS'] )
            

    def main(self, allResultsLinks,output_file_name):
        print("Execute second parser.py -------------------------------------------------------------length:",len(allResultsLinks),allResultsLinks[0])
        # Communicator.show_message("Scrolling is done. Now going to scrape each location")
        try:
            count=0
            for resultLink in allResultsLinks:
                count=count+1
                if count<20:
                    if Common.close_thread_is_set():
                        self.driver.quit()
                        return

                    self.openingurl(url=resultLink)
                    self.parse(web_url=resultLink)
                else:
                    break

        except Exception as e:
            print(f"Error occured while parsing the locations. Error: {str(e)}")
            # Communicator.show_message(f"Error occured while parsing the locations. Error: {str(e)}")
            
        finally:
            self.add_directions(output_file_name)
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData,output_file_name=output_file_name)

    def add_directions(self,output_file_name):
        direction_obj=Directions()
        print(output_file_name,output_file_name.split(' '))
        # Split the string by spaces
        split_str = output_file_name.split()

        # Extract the last two components and concatenate them
        postcode = split_str[-2] + " " + split_str[-1]

        print("######################################## Final Data #######################################################################",type(self.finalData))
        # print(self.finalData,self.finalData[0])
        try:
            for i in range(len(self.finalData)):
                print(len(self.finalData))
                print("count______________________",i,self.finalData[i])
                direction_obj=Directions()
                details=direction_obj.process(url=self.finalData[i]['url'],postcode=postcode)
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",details,details.get('distance'))
                self.finalData[i]['distance']= details['distance']
                self.finalData[i]['time'] = details['time']
                # print(self.f)
                direction_obj.driver.quit()
                direction_obj = None
            print(self.finalData)
        except Exception as e:
            print(e)
            print("####################################################################################################################################")
        print("###################################################################     end    ################################################################")
       

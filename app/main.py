import pandas as pd
import pickle
from datetime import datetime, timedelta
import traceback
import os, sys 
# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#import database class 
from database.database_handler import PostcodeDataHandler
#############

from free_map_tool import WebScraper
from prediction import PredictionModel
from plot import PredictionsPlotter
from crystal import Crystal,WebDriverHelper,HouseholdIncomeScraper
#json class 
from data_json import JsonDataHandler
import json 
####
import re 
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn 

#
# for parallel processing 
from concurrent.futures import ThreadPoolExecutor
import asyncio
import nest_asyncio
import subprocess

import pandas as pd
from io import StringIO


nest_asyncio.apply()
#Load Google maps scraper 
from google_maps_scraper.manager import XLSXHandler

from dataclasses import dataclass, asdict, field
# Load the environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

#headers
# CORS middleware (adjust settings as per your security requirements)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust based on your security needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to add the ngrok-skip-browser-warning header
# @app.middleware("http")
# async def add_ngrok_skip_header(request, call_next):
#     print("_____________________ skip browser warning ngrok _____________________________")
#     response = await call_next(request)
#     response.headers["ngrok-skip-browser-warning"] = "true"
#     return response



executor = ThreadPoolExecutor()

#add file
print(os.getcwd())
# Mount static files route for accessing HTML files
output_dir = 'plots'

print("___________output_dir___________",output_dir)
app.mount("/files", StaticFiles(directory=output_dir), name="files")


# Define a Pydantic model for input data
class PostcodeRequest(BaseModel):
    postcode: str

def load_and_update_excel(new_df,file_path,sheet_name):
    # Load the existing Excel file


    # Read the existing Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Create a mask for existing postcodes
    existing_postcodes = df['postcode'].values  # Replace 'postcode' with the actual column name
    new_rows = new_df[~new_df['postcode'].isin(existing_postcodes)]  # Keep only new postcodes

    # Append only new rows
    if not new_rows.empty:
        df = pd.concat([df, new_rows], ignore_index=True)
        # Save the updated DataFrame back to the Excel file
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        print("New rows added successfully!")
    else:
        print("No new rows to add; all postcodes already exist.")

def start_scraper(postcode):

    url = 'https://www.freemaptools.com/find-uk-postcodes-inside-radius.htm#google_vignette'
    radius=1.61
    directory_path = os.path.join(os.getcwd(),'downloaded_csv')
    # Usage
    scraper = WebScraper(url=url, directory_path=directory_path)

    # To perform web actions for a specific postcode
    scraper.perform_web_actions(postcode=postcode,radius=radius)

    # To extract demographics
    average_data = scraper.extract_demographics()  
    print(average_data,type(average_data))
    # Convert to DataFrame
    df = pd.DataFrame([average_data])
    # handler.add_postcode_info(postcode, 1.61, 1000)
    return df

# def check_data(postcode,file_path,sheet_name):
#     print(os.getcwd())
#     print("in check data ",file_path)
#     df = pd.read_excel(file_path, sheet_name=sheet_name)
#     print(df)

#     # Create a mask for existing postcodes
#     # existing_postcodes = df['postcode'].values  # Replace 'postcode' with the actual column name
#     # exists = df['postcode'].isin([postcode]).any()  # Keep only new postcodes

#     # new_df=pd.DataFrame()
#     # # Append only new rows
#     # if exists:
#     #     new_df=df[df['postcode']==postcode]
#     #     return new_df
#     # else:
#     for i in range(5):
#         try:
#             # Attempt to scrape data for the postcode
#             df = start_scraper(postcode)
#             print(df)
            
#             # Add the postcode to the dataframe
#             df['postcode'] = postcode
            
#             # Load and update Excel with the new dataframe
#             load_and_update_excel(df, file_path, sheet_name)
            
#             # If df is not empty, return it and break the loop
#             if not df.empty:
#                 return df  # Exit after a successful run

#         except Exception as e:
#             # Log the exception
#             print(f"Attempt {i+1}: Exception occurred - {e}")
            
#             # If it's the last attempt, re-raise the exception
#             if i == 4:
#                 raise
def check_data(postcode,file_path,sheet_name):
    print(os.getcwd())
    print("in check data ",file_path)
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(df)

    # Create a mask for existing postcodes
    # existing_postcodes = df['postcode'].values  # Replace 'postcode' with the actual column name
    exists = df['postcode'].isin([postcode]).any()  # Keep only new postcodes

    new_df=pd.DataFrame()
    # Append only new rows
    if exists:
        new_df=df[df['postcode']==postcode]
        return new_df
    else:
        for i in range(5):
            try:
                # Attempt to scrape data for the postcode
                df = start_scraper(postcode)
                print(df)
                
                # Add the postcode to the dataframe
                df['postcode'] = postcode
                
                # Load and update Excel with the new dataframe
                load_and_update_excel(df, file_path, sheet_name)
                
                # If df is not empty, return it and break the loop
                if not df.empty:
                    return df  # Exit after a successful run

            except Exception as e:
                # Log the exception
                print(f"Attempt {i+1}: Exception occurred - {e}")
                
                # If it's the last attempt, re-raise the exception
                if i == 4:
                    raise

    
def run_prediction(start_date,end_date,df,postcode):

    df['Year']=2024
    df['Week']=34
    df['Month']=9

    model = PredictionModel(
    model_path = os.path.join(os.path.dirname(__file__), 'models','xgboost_model_without_crystal_radius_1.61.pkl'), 
    average_df=df,
    postcode=postcode
        )
    min_prediction,average_prediction,max_prediction=model.generate_predictions(start_date,end_date)
    return min_prediction,average_prediction,max_prediction

#Crystal Roof fetching

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
    return df_restaurants,df_pubs

    # web_helper.store_data_as_json(postcode=postcode,restaurant_data=df_restaurants,pub_data=df_pubs,demo_df=demo_df)


def fetch_affluence(url):
        # Example usage:
    # url = 'https://crystalroof.co.uk/report/postcode/IP265NP/affluence'  # Replace with the actual URL

    # Create an instance of the scraper
    scraper = HouseholdIncomeScraper(url)

    # Call the scrape_income_data method to get the combined DataFrame
    df_household_income,df_neighbourhood_income ,full_address= scraper.scrape_income_data()
    print(df_household_income)
    return df_household_income,df_neighbourhood_income,full_address

def fetch_occupation(url):
    try:
        # Example usage
        # url = 'https://example.com'  # Replace with the actual URL
        web_helper = WebDriverHelper(url)
        web_helper.load_page()
        web_helper.click_on_borough_button()

        df_occupations,location_text = web_helper.get_occupation_data()
        print(df_occupations,location_text) 
        return df_occupations,location_text   
    except Exception as e:
        print(e)

def fetch_transport(url):
    try:
        # Example usage
        # url = 'https://example.com'  # Replace with the actual URL
        web_helper = WebDriverHelper(url)
        web_helper.load_page()

        connectivity_df,stations_df = web_helper.get_transport_data()
        print(connectivity_df,stations_df) 
        return connectivity_df,stations_df   
    except Exception as e:
        print(e)


# def fetch_unviersities_data(full_Address):
    
#     # Split the string by commas and remove any leading/trailing whitespace
#     parts = [part.strip() for part in full_Address.split(',')]
#     result = ', '.join(parts[-2:])

#     # Input parameters as strings
#     search_list = [f"Universisites near {result}"]
#     total = 20  # Number of listings to scrape

#     # Scrape business data
#     business_list = GoogleMapsScraper.scrape(search_list, total)
#     business_dicts = [asdict(business) for business in business_list.business_list]

#     # Convert to DataFrame
#     df = pd.DataFrame(business_dicts)

#     # Save data to files
#     business_list.save_to_excel("google_maps_data")

#     univeristies_df= df['name','address','url']

#     return univeristies_df
#     # business_list.save_to_csv("google_maps_data")


# def fetch_universities_data(address):
#     # Split the string by commas and remove any leading/trailing whitespace
#     parts = [part.strip() for part in address.split(',')]
#     result = ', '.join(parts[-2:])

#     # Input parameters as strings
#     search_list = [f"Universisites near {result}"]
#     total = 20  # Number of listings to scrape

#     print("--------------------------in fetch unversities data ---------------------------------------------------------------------------------------")
#     business_list=asyncio.run(GoogleMapsScraper.scrape(search_list, total))

#     business_dicts = [asdict(business) for business in business_list.business_list]

#     # Convert to DataFrame
#     df = pd.DataFrame(business_dicts)

#     # Save data to files
#     # business_list.save_to_excel("google_maps_data")

#     df_universities= df['name','address','url']
#     return df_universities

# Helper function to call fetch_universities_data


# def fetch_universities_data(address):
#     # Split the string by commas and remove any leading/trailing whitespace
#     parts = [part.strip() for part in address.split(',')]
#     result = ', '.join(parts[-2:])

#     # Input parameters as strings
#     search_list = [f"Universisites near {result}"]
#     total = 20  # Number of listings to scrape

#     # Run scraper.py in a subprocess and capture output
#     result = subprocess.run(
#         ["python", "google_maps.py", search_list],
#         stdout=subprocess.PIPE,
#         text=True
#     )
#     df_universities = pd.read_json(result.stdout)
#     print(df_universities)
#     print("------in fetch universities data------")
    # business_list = GoogleMapsScraper.scrape(search_list, total)

    # business_dicts = [asdict(business) for business in business_list.business_list]

    # Convert to DataFrame
    # df = pd.DataFrame(business_dicts)

    # Select required columns
    # df_universities = df[['name', 'address', 'url']]
    # return df_universities



def run_plot(demo_df,df_restaurants,df_pubs,df_household_income,df_neighbourhood_income, full_address,df_occcupation,occupation_location_text,connectivity_df,stations_df,df_universities,postcode):
    # postcode_info_path =os.path.join(os.path.dirname(__file__), os.environ.get('demographic_file_path'))
    postcode_info_path = os.environ.get('demographic_file_path') #'demographic_data/updated_outer_demog_sales_data_radius_1.xlsx'
    folder_path = os.environ.get('prediction_results_path') #'results'
    # folder_path = os.path.join(os.path.dirname(__file__), 'results')
    output_file_name = f"{os.environ.get('plots_output_path')}/{postcode}.html"
    # output_file_name = os.path.join(os.path.dirname(__file__), os.environ.get('plots_output_path'), f"{postcode}.html")
    # output_file_name = 'predictions_plot_with_postcode_info_radius_sec.html'

    plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    
    plotter.run(demo_df,df_restaurants,df_pubs,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text,connectivity_df,stations_df,df_universities,postcode)



def save_data_to_database(postcode):
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "htech_ai",
        "password": "Htech786##",
        "database": "test_db"  # Assuming you have a database to connect to
    }

    # Path to your JSON file
    json_file_path = "D:/work/automation/free_map_tools/final/Location_analyzer/app/postcode_data.json"

    # Example usage
    postcode_handler = PostcodeDataHandler(db_config, json_file_path)
    # postcode = "AL10 9AY"  # Replace with the actual postcode you want to search
    postcode_handler.insert_into_database(postcode)
    postcode_handler.close_database()    

# def validate_uk_postcode(postcode):
#     # Define the regex pattern for UK postcodes
#     pattern = r"^(GIR 0AA|(?:[A-PR-UWYZ][A-HK-Y0-9]?[0-9A-HJKS-UW]?[0-9]? ?[0-9][ABD-HJLNP-UW-Z]{2}))$"
    
#     # Match the pattern against the provided postcode (converted to uppercase)
#     match = re.match(pattern, postcode.upper())
    
#     # Return True if the postcode is valid, otherwise False
#     return bool(match)


def fetch_universities(full_address,postcode):
    try:
        # df_universities=XLSXHandler.laod_xlsx(postcode)
        df_universities = XLSXHandler().load_xlsx(postcode)
        print(df_universities)
        # print(df_universities.head)
        if not df_universities.empty:
            df_universities=df_universities[['name','address','url']]
            return df_universities
        else:

            parts = [part.strip() for part in full_address.split(',')]
            result = ', '.join(parts[-2:])

            # Input parameters as strings
            search_list = f"Universisites near {result}"
            # total = 20  # Number of listings to scrape    
            # The script you want to run
            script_path = "google_maps.py"
            # Run the subprocess with the virtual environment's Python interpreter
            result = subprocess.run(
                ['python', script_path, search_list],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            df_universities = XLSXHandler().load_xlsx(postcode)
            return df_universities
    except Exception as e:
        print(traceback.format_exc())

# Define the endpoint
@app.get("/process_postcode/")
async def process_postcode(postcode: str):
    # response=add_ngrok_skip_header()
    postcode = postcode
    print("in postcode ")
    json_file = 'postcode_data.json'

    # Initialize handler
    handler = JsonDataHandler(json_file)
    # Define file path and sheet name
    # file_path = os.environ.get('demographic_file_path')
    file_path = os.path.join(os.path.dirname(__file__), 'demographic_data', 'updated_outer_demog_sales_data_radius_1.xlsx')
    if os.path.exists(file_path):
        print("True")
        print("file_path:",file_path)
    print("file path ",file_path)
    sheet_name = 'Sheet1'

    # Check and update data
    try:
        # if validate_uk_postcode(postcode):
        postcode=postcode.upper()
        loop = asyncio.get_event_loop()

        # Run scraper and predictions in a separate thread using ThreadPoolExecutor
        # try:
        df = await loop.run_in_executor(executor, check_data, postcode, file_path, sheet_name)
        print("__________________________________))))))))))))))))))))__________________________________",df)
        
        start_date = "05/01/2023"
        end_date = "05/28/2024"
        min_prediction,average_prediction,max_prediction=await loop.run_in_executor(executor, run_prediction, start_date, end_date, df, postcode)
        #update json 
        print("___________ average prediction",average_prediction,type(average_prediction))
        handler.add_postcode_info(postcode=postcode, radius=1.61, min_prediction=min_prediction,average_prediction=average_prediction,max_prediction=max_prediction)
        handler.add_demographics(postcode,df)
        # Fetch data from Crystal
        postcode_crystal = re.sub(r"\s+", "", postcode, flags=re.UNICODE)
        url_demographics = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/demographics"
        demo_df = await loop.run_in_executor(executor, fetch_demographics, url_demographics)
        # handler.add_ethnicity(postcode, demo_df)

        url_amenities = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/amenities"
        df_restaurants, df_pubs = await loop.run_in_executor(executor, fetch_amenities, postcode, url_amenities, demo_df)
        # handler.add_nearby_restaurants(postcode, df_restaurants)
        # handler.add_nearby_pubs(postcode, df_pubs)
        # handler.add_crystal_data(postcode, ethnicity_data=demo_df, restaurants=df_restaurants, pubs=df_pubs)
        # print(handler.to_json())
        url_affluence= f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/affluence'
        df_household_income,df_neighbourhood_income,full_address = await loop.run_in_executor(executor, fetch_affluence, url_affluence)
        print(df_household_income,df_neighbourhood_income)

        # df_universities = fetch_universities_data(full_address)
        # print(df_universities)
        # df_universities =  fetch_universities_data(full_address)
        # print(df_universities)


        # parts = [part.strip() for part in full_address.split(',')]
        # result = ', '.join(parts[-2:])

        # # Input parameters as strings
        # search_list = f"Universisites near {result}"
        # total = 20  # Number of listings to scrape

        # # Run scraper.py in a subprocess and capture output
        # # result = subprocess.run(
        # #     ["D:/work/automation/free_map_tools/final/Location_analyzer/venv/Scripts/python", "google_maps.py", search_list],
        # #     stdout=subprocess.PIPE,
        # #     text=True
        # # )


        # # Specify the path to the Python executable in your virtual environment
        # # venv_python_path = r"D:/work/automation/free_map_tools/final/Location_analyzer/venv/Scripts/python"
        
        # # The script you want to run
        # script_path = "google_maps.py"
        
        

        # # Run the subprocess with the virtual environment's Python interpreter
        # result = subprocess.run(
        #     ['python', script_path, search_list],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True
        # )
        # # df_universities=XLSXHandler.laod_xlsx(postcode)
        # df_universities = XLSXHandler().load_xlsx(postcode)
        # print(df_universities.head)

        # df_universities=df_universities[['name','address','url']]

        #############################################################################################################################################

        # df_universities=fetch_universities(full_address,postcode)

                # df_universities=XLSXHandler.laod_xlsx(postcode)









        df_universities = XLSXHandler().load_xlsx(postcode)
        print(df_universities)
        # print(df_universities.head)
        if df_universities is not None:
            df_universities=df_universities[['name','address','url']]
            # return df_universities
        else:

            parts = [part.strip() for part in full_address.split(',')]
            result = ', '.join(parts[-2:])

            # Input parameters as strings
            search_list = f"Universisites near {result}"
            # total = 20  # Number of listings to scrape    
            # The script you want to run
            script_path = "google_maps.py"
            # Run the subprocess with the virtual environment's Python interpreter
            result = subprocess.run(
                ['python', script_path, search_list],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            df_universities = XLSXHandler().load_xlsx(postcode)





            # return df_universities

####################################################################################

        # df_universities= pd.DataFrame(columns=['name', 'address', 'url'])
            # Check if result is successful before parsing
        # if result.returncode == 0:
        #     # Replace `result.stdout` with your actual JSON string from the output
        #     result_stdout = result.stdout.strip()  # Remove any trailing newlines or extra spaces
        #     print(result_stdout)
        #     # Try loading JSON directly
        #     try:
        #         # Convert the string to a dictionary first
        #         json_data = json.loads(result_stdout)
        #         print("---------------------------------------------------",json_data)
        #         # Now load it into a DataFrame
        #         df_universities = pd.DataFrame(json_data)
        #         print(df_universities)
        #     except json.JSONDecodeError as e:
        #         print("JSON decode error:", e)
        #         # print("Output received:", result_stdout)
        #     # df_universities = pd.read_json(result.stdout)
        #     print(df_universities)
        # else:
        #     print("Subprocess failed:", result.stderr)

        # search_list = ["restaurant near me"]
        # total = 10  # Number of listings to scrape

        # business_list = await loop.run_in_executor(asyncio.run(GoogleMapsScraper.scrape(search_list, total)))
        # print(business_list)

        ###### occupation #########################
        url_occupation= f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/affluence?tab=occupation'
        df_occcupation,occupation_location_text = await loop.run_in_executor(executor, fetch_occupation, url_occupation)
        print(df_occcupation,occupation_location_text)

        ###### transport #########################
        url_transport= f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/transport'
        connectivity_df,stations_df = await loop.run_in_executor(executor, fetch_transport, url_transport)
        print(connectivity_df,stations_df)        
        #Save crystal data to json 
        handler.add_crystal_data(postcode, demo_df, df_restaurants, df_pubs,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text,connectivity_df,stations_df)
        print( "________________________________in main _______________________________________",full_address)

        # Generate plot
        await loop.run_in_executor(executor, run_plot, demo_df, df_restaurants, df_pubs,df_household_income,df_neighbourhood_income,full_address,df_occcupation,occupation_location_text,connectivity_df,stations_df,df_universities,postcode)

        # save data 
        save_data_to_database(postcode=postcode)
        ####################


        # Return file URL
        file_url = f"https://decent-probably-lacewing.ngrok-free.app/files/{postcode}.html"
        return file_url
        # else:
        #     print(f"{postcode} is not a valid UK postcode.")
            # return(f"{postcode} is not a valid UK postcode.")        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(traceback.format_exc()))


# Define the endpoint for average prediction from database 
@app.get("/get_average_prediction/")
async def get_average_prediction(postcode: str):
    postcode=postcode.upper()
    print("____in get_average_prediction__")
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "htech_ai",
        "password": "Htech786##",
        "database": "test_db"  # Assuming you have a database to connect to
    }

    # Path to your JSON file
    json_file_path = "D:/work/automation/free_map_tools/final/Location_analyzer/app/postcode_data.json"

    # Example usage
    postcode_handler = PostcodeDataHandler(db_config, json_file_path)

    json_data=postcode_handler.get_average_prediction_from_db(postcode=postcode)
    print(json_data)
    return json_data
    


# Define the endpoint
# @app.get("/process_postcode/")
# async def process_postcode(postcode: str):
#     postcode = postcode
#     # postcode = re.sub(r"\s+", "", postcode, flags=re.UNICODE)
    
#     # Define file path and sheet name
#     file_path = os.environ.get('demographic_file_path')
#     sheet_name = 'Sheet1'
    
#     # Check and update data
#     try:
#         df = check_data(postcode, file_path, sheet_name)
#         #run prediction
#         start_date="01/01/2024"
#         end_date="12/28/2024"
#         run_prediction(start_date=start_date,end_date=end_date,df=df,postcode=postcode)
#         #run on crystal 
#         postcode_crystal=re.sub(r"\s+", "", postcode, flags=re.UNICODE)#"TS14AW"
#         url = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/demographics"
#         demo_df=fetch_demographics(url)
#         url=f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/amenities"
#         df_restaurants,df_pubs=fetch_amenities(postcode,url,demo_df)
            
#         # Generate plot
#         run_plot(demo_df,df_restaurants,df_pubs,postcode)
        
#         # return {"message": "Data processed successfully", "postcode": postcode}
#             # Return a URL to access the HTML file
#         file_url=f"https://d99a-154-192-9-100.ngrok-free.app/files/{postcode}.html"
#         return file_url
#         # file_url = f"http://127.0.0.1:8000/{os.environ.get('plots_output_path')}/{postcode}.html"
#         # print(file_url)
#         # return {"url": file_url}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Run the server
# Command: uvicorn main:app --reload



if __name__ == "__main__":
    # Run the app using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
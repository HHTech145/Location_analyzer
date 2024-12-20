import pandas as pd

import pandas as pd
import pickle
from datetime import datetime, timedelta
import traceback
import os, sys 
# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#import database class 
# from database.database_handler import PostcodeDataHandler
#############

# from free_map_tool import WebScraper
# from prediction import PredictionModel
# from plot import PredictionsPlotter
from crystal_data_collector import Crystal,WebDriverHelper,HouseholdIncomeScraper
#json class 
from data_json import JsonDataHandler
import json 
####
import re 
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn 
# for parallel processing 
from concurrent.futures import ThreadPoolExecutor
import asyncio
import nest_asyncio
import subprocess

executor = ThreadPoolExecutor()


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
        try:
            web_helper.click_on_borough_button()
            df_occupations,location_text = web_helper.get_occupation_data()
            print(df_occupations,location_text) 
            return df_occupations,location_text   
        except Exception as e:
            df_occupations=pd.DataFrame()
            location_text=""
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

# Process one postcode
async def process_postcode(postcode: str, handler):
    try:
        postcode = postcode.upper()
        postcode_crystal = re.sub(r"\s+", "", postcode, flags=re.UNICODE)

        # Construct the URLs for the required data
        url_demographics = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/demographics"
        demo_df = fetch_demographics(url_demographics)  # Removed await

        url_amenities = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/amenities"
        df_restaurants, df_pubs = fetch_amenities(postcode, url_amenities, demo_df)  # Removed await

        url_affluence = f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/affluence'
        df_household_income, df_neighbourhood_income, full_address = fetch_affluence(url_affluence)  # Removed await

        url_occupation = f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/affluence?tab=occupation'
        df_occupation, occupation_location_text = fetch_occupation(url_occupation)  # Removed await

        url_transport = f'https://crystalroof.co.uk/report/postcode/{postcode_crystal}/transport'
        connectivity_df, stations_df = fetch_transport(url_transport)  # Removed await

        # Adding collected data to the handler (e.g., for storing in JSON)
        handler.add_crystal_data(
            postcode=postcode,
            full_address=full_address,
            ethnicity_data=demo_df,
            restaurants_data=df_restaurants,
            pubs_data=df_pubs,
            household_income_data=df_household_income,
            neighbourhood_income_data=df_neighbourhood_income,
            occupation_data=df_occupation,
            occupation_location_text=occupation_location_text,
            connectivity_data=connectivity_df,
            stations_data=stations_df
        )
    except Exception as e:
        print(f"Error processing postcode {postcode}: {e}")

        
async def process_multiple_postcodes(postcodes: list, handler, max_concurrent: int = 20):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def semaphore_task(postcode):
        async with semaphore:
            await process_postcode(postcode, handler)

    tasks = [semaphore_task(postcode) for postcode in postcodes]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Load the data and filter the postcodes for England
    csv_file = 'postcodes.csv'  # Adjust the filename if needed
    data = pd.read_csv(csv_file)
    england_postcodes = data[data['Country'] == 'England']['Postcode'].tolist()  # Convert to list

    # Initialize the JsonDataHandler for storing data
    json_file = "crystal_data.json"
    handler = JsonDataHandler(json_file)

    # Run the async processing for multiple postcodes, with a concurrency limit of 20
    asyncio.run(process_multiple_postcodes(england_postcodes, handler, max_concurrent=20))
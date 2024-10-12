import pandas as pd
import pickle
from datetime import datetime, timedelta

from free_map_tool import WebScraper
from prediction import PredictionModel
from plot import PredictionsPlotter
from crystal import Crystal,WebDriverHelper
import re 
import os 

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
# Load the environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

#add file

# Mount static files route for accessing HTML files
output_dir = os.environ.get('plots_output_path', './output')
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
    radius=1
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
    return df

def check_data(postcode,file_path,sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Create a mask for existing postcodes
    # existing_postcodes = df['postcode'].values  # Replace 'postcode' with the actual column name
    exists = df['postcode'].isin([postcode]).any()  # Keep only new postcodes

    new_df=pd.DataFrame()
    # Append only new rows
    if exists:
        new_df=df[df['postcode']==postcode]
        return new_df
    else:
        df=start_scraper(postcode)
        print(df)
        df['postcode']=postcode
        load_and_update_excel(df,file_path,sheet_name)
        return df
    
def run_prediction(start_date,end_date,df,postcode):

    df['Year']=2024
    df['Week']=34
    df['Month']=9

    model = PredictionModel(
    model_path= os.environ.get('xg_boost_model_path'),#'models/xgboost_model_without_crystal_ver_1.pkl',
    average_df=df,
    postcode=postcode
        )
    model.generate_predictions(start_date,end_date)

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


def run_plot(demo_df,df_restaurants,df_pubs,postcode):
    postcode_info_path = os.environ.get('demographic_file_path') #'demographic_data/updated_outer_demog_sales_data_radius_1.xlsx'
    folder_path = os.environ.get('prediction_results_path') #'results'
    output_file_name = f"{os.environ.get('plots_output_path')}/{postcode}.html"
    # output_file_name = 'predictions_plot_with_postcode_info_radius_sec.html'

    plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    plotter.run(demo_df,df_restaurants,df_pubs,postcode)


# Define the endpoint
@app.get("/process_postcode/")
async def process_postcode(postcode: str):
    postcode = postcode
    # postcode = re.sub(r"\s+", "", postcode, flags=re.UNICODE)
    
    # Define file path and sheet name
    file_path = os.environ.get('demographic_file_path')
    sheet_name = 'Sheet1'
    
    # Check and update data
    try:
        df = check_data(postcode, file_path, sheet_name)
        #run prediction
        start_date="01/01/2024"
        end_date="12/28/2024"
        run_prediction(start_date=start_date,end_date=end_date,df=df,postcode=postcode)
        #run on crystal 
        postcode_crystal=re.sub(r"\s+", "", postcode, flags=re.UNICODE)#"TS14AW"
        url = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/demographics"
        demo_df=fetch_demographics(url)
        url=f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/amenities"
        df_restaurants,df_pubs=fetch_amenities(postcode,url,demo_df)
            
        # Generate plot
        run_plot(demo_df,df_restaurants,df_pubs,postcode)
        
        # return {"message": "Data processed successfully", "postcode": postcode}
            # Return a URL to access the HTML file
        file_url=f"https://85b5-154-192-8-85.ngrok-free.app/files/{postcode}.html"
        return file_url
        # file_url = f"http://127.0.0.1:8000/{os.environ.get('plots_output_path')}/{postcode}.html"
        # print(file_url)
        # return {"url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
# Command: uvicorn main:app --reload




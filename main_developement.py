import pandas as pd
import pickle
from datetime import datetime, timedelta

from test_2 import WebScraper
from prediction import PredictionModel
from plot import PredictionsPlotter
from crystal import Crystal,WebDriverHelper
import re 
import os 

from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()



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
    
def run_prediction(start_date,end_date):

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


if __name__ == "__main__":
    file_path = os.environ.get('demographic_file_path') #'demographic_data/updated_outer_demog_sales_data_radius_1.xlsx'  # Update with your file path
    sheet_name = 'Sheet1'  # Update with your sheet name if needed
    postcode = "N19 5RD"

  
    df=check_data(postcode,file_path,sheet_name)



    # # Display the DataFrame
    # print(df)
    
    # df['postcode']=postcode

    # #update deomgraphics 
    # load_and_update_excel(df,file_path,sheet_name)

    # df['Year']=2024
    # df['Week']=34
    # df['Month']=9

    # model = PredictionModel(
    # model_path='free_map_tools/models/xgboost_model_without_crystal_ver_1.pkl',
    # average_df=df,
    # postcode=postcode
    #     )
    # model.generate_predictions(start_date="01/01/2021", end_date="12/28/2026")
    start_date="01/01/2024"
    end_date="12/28/2024"
    run_prediction(start_date=start_date,end_date=end_date)

    #plot

    # # Usage
    # postcode_info_path = 'free_map_tools/demographic_data/updated_outer_demog_sales_data_radius_1.xlsx'
    # folder_path = 'free_map_tools/results'
    # output_file_name = 'free_map_tools/predictions_plot_with_postcode_info_radius_2.html'

    # plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    # plotter.run()


    postcode_crystal=re.sub(r"\s+", "", postcode, flags=re.UNICODE)#"TS14AW"
    url = f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/demographics"
    demo_df=fetch_demographics(url)
    url=f"https://crystalroof.co.uk/report/postcode/{postcode_crystal}/amenities"
    df_restaurants,df_pubs=fetch_amenities(postcode,url,demo_df)
    # postcode_info_path = 'demographic_data/updated_outer_demog_sales_data_radius_1.xlsx'
    # folder_path = 'results'
    # output_file_name = f"plots/{postcode}.html"

    # plotter = PredictionsPlotter(postcode_info_path, folder_path, output_file_name)
    # plotter.create_plot_for_crystal(demo_df,df_restaurants,df_pubs)    
    run_plot(demo_df,df_restaurants,df_pubs,postcode)
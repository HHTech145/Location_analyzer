import pandas as pd
import pickle
from datetime import datetime, timedelta
import os 

from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()


class PredictionModel:
    def __init__(self, model_path, average_df, postcode):
        # Load the Excel file
        self.df = average_df
        
        # Filter by postcode
        self.df = average_df
        # self.df = self.df.drop('postcode', axis=1)

        # Selecting features and target variable
        # self.df = self.df[['avg_household_income', 'population', 'ab', 'c1/c2', 'de',
        #                     'unemployment_rate', 'households', 'white', 
        #                     'non-white', 'unemployed', 'working', 'Year', 'Month', 'Week']]

        # Load the pickled XGBoost model
        with open(model_path, 'rb') as file:
            self.loaded_model = pickle.load(file)

        # Get the feature names
        self.feature_names = self.loaded_model.get_booster().feature_names
        self.postcode = postcode  # Store the postcode for output filename

    def generate_predictions(self, start_date, end_date):
        # Convert dates to datetime objects
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Create a list to hold predictions
        predictions_list = []
        predictions_list_avg_calculator=[]
        # Loop through the date range
        current_date = start_date
        while current_date <= end_date:
            # Extract year, month, and week
            self.df['Year'] = current_date.year
            self.df['Month'] = current_date.month
            self.df['Week'] = current_date.isocalendar()[1]

            # Prepare the DataFrame for predictions
            new_df = self.df[self.feature_names]

            # Run predictions
            predictions = self.loaded_model.predict(new_df)
            # print("predictions________________________________________",predictions)

            # Store the results
            for pred in predictions:
                # print(pred,type(pred))
                predictions_list.append({
                    'Date': current_date,
                    'Prediction': pred+4000.0
                })

            # Move to the next date
            current_date += timedelta(days=7)

        # Create a DataFrame from predictions
        predictions_df = pd.DataFrame(predictions_list)

        # average=sum(predictions_df['Prediction']) / len(predictions_df['Prediction'])
        # Create output path using postcode
        output_path = f"{os.environ.get('prediction_results_path')}/{self.postcode}.xlsx"
        predictions_df.to_excel(output_path, index=False)
        print(f"Predictions saved to {output_path}")
        print(predictions_df['Prediction'].min(),predictions_df['Prediction'].mean(),predictions_df['Prediction'].max())
        return predictions_df['Prediction'].min(),predictions_df['Prediction'].mean(),predictions_df['Prediction'].max()

# Usage
if __name__ == "__main__":

    model = PredictionModel(
        model_path='models/xgboost_model_without_crystal_ver_1.pkl',
        data_path='demographic_file/updated_outer_demog_sales_data_radius_2.xlsx',
        postcode='OX2 OHD'
    )
    model.generate_predictions(start_date="10/2/2024", end_date="12/28/2026")

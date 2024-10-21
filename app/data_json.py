import os
import json
import traceback

class JsonDataHandler:
    def __init__(self, json_file):
        self.json_file = json_file
        self.postcodes = self.load_json()

    # Load existing JSON data from file or create an empty dictionary if the file doesn't exist or is invalid
    def load_json(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as f:
                    data = f.read().strip()  # Ensure the file isn't just whitespace
                    if data:
                        return json.loads(data)  # Use loads to avoid empty file error
            except json.JSONDecodeError:
                print("Error: Invalid JSON data, initializing with an empty dictionary.")
                return {}  # Return empty dict if the JSON is invalid
        return {}

    # Save the current postcodes data back to the JSON file
    def save_json(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.postcodes, f, indent=4)

    # Add a new postcode or update existing postcode data
    def add_postcode_info(self, postcode, radius=None, prediction=None):
        # Remove leading/trailing spaces from postcode for uniformity
        postcode = postcode.strip()
        
        # Check if postcode already exists, if not, create a new entry
        if postcode not in self.postcodes:
            self.postcodes[postcode] = {
                'radius': None,  # Single value, not a list
                'prediction': None,  # Single value, not a list
                'demographics': {},
                'crystal': {
                    'ethnicity': {},
                    'restaurants': {},
                    'pubs': {}
                }
            }
        
        # Update the single values for radius and prediction
        if radius is not None:
            self.postcodes[postcode]['radius'] = radius
        
        if prediction is not None:
            self.postcodes[postcode]['prediction'] = prediction
        
        # Save changes to JSON
        self.save_json()

    # Add demographic data by converting pandas Series to Python types
    def add_demographics(self, postcode, df):
        # Ensure postcode exists
        postcode = postcode.strip()
        if postcode not in self.postcodes:
            self.add_postcode_info(postcode, None, None)

        # Add demographic data by converting pandas Series to Python types
        self.postcodes[postcode]['demographics'] = {
            'population': int(df['population'].iloc[0]),  # Convert to int
            'households': int(df['households'].iloc[0]),  # Convert to int
            'avg_household_income': int(df['avg_household_income'].iloc[0]),  # Convert to int
            'unemployment_rate': float(df['unemployment_rate'].iloc[0]),  # Convert to float
            'working': float(df['working'].iloc[0]),  # Convert to float
            'unemployed': float(df['unemployed'].iloc[0]),  # Convert to float
            'ab': float(df['ab'].iloc[0]),  # Convert to float
            'c1/c2': float(df['c1/c2'].iloc[0]),  # Convert to float
            'de': float(df['de'].iloc[0])  # Convert to float
        }

        # Save changes to JSON
        self.save_json()

    def add_crystal_data(self, postcode, ethnicity_data, restaurants, pubs):
        try:
            # Ensure postcode exists and strip any extra whitespace
            postcode = postcode.strip()
            print("*********************************************************_)___________________________________________________",postcode,self.postcodes[postcode])
            if postcode not in self.postcodes:
                self.add_postcode_info(postcode, None, None)

            # Initialize crystal data if it doesn't exist
            if 'crystal' not in self.postcodes[postcode]:
                self.postcodes[postcode]['crystal'] = {
                    'ethnicity': {},
                    'restaurants': {},
                    'pubs': {}
                }

            # Access crystal data directly
            current_crystal_data = self.postcodes[postcode]['crystal']

            # Add ethnicity data
            if ethnicity_data is not None and not ethnicity_data.empty:
                ethnicity_list = {row['Demographics']: row['Percentage'] for _, row in ethnicity_data.iterrows()}
                current_crystal_data['ethnicity'].update(ethnicity_list)

            # Add restaurant data as a dictionary
            if restaurants is not None and not restaurants.empty:
                restaurant_dict = {row['Restaurant']: row['Distance'] for _, row in restaurants.iterrows()}
                current_crystal_data['restaurants'].update(restaurant_dict)

            # Add pub data as a dictionary
            if pubs is not None and not pubs.empty:
                pub_dict = {row['Pub']: row['Distance'] for _, row in pubs.iterrows()}
                current_crystal_data['pubs'].update(pub_dict)
            # Save changes to JSON
            self.save_json()

        except Exception as e:
            print(f"Error occurred while adding crystal data for postcode {postcode}: {str(e)}")
            print(traceback.format_exc())  # Log the traceback for debugging




# Example usage
if __name__ == "__main__":
    # Example JSON file name
    json_file = 'postcode_data.json'

    # Initialize handler
    # handler = JsonDataHandler(json_file)

    # # Example DataFrame (replace with actual pandas DataFrame)
    # import pandas as pd

    # df = pd.DataFrame({
    #     'postcode': ['UB1 3DA'],
    #     'population': [49249],
    #     'households': [16072],
    #     'avg_household_income': [42900],
    #     'unemployment_rate': [0.1263],
    #     'working': [0.75],
    #     'unemployed': [0.24],
    #     'ab': [0.14],
    #     'c1/c2': [0.51],
    #     'de': [0.33]
    # })

    # # Add postcode information
    # handler.add_postcode_info('UB1 3DA', radius=1.61, prediction=1000)

    # # Add demographic data
    # handler.add_demographics('UB1 3DA', df)

    # # Add crystal data (ethnicity, restaurants, pubs)
    # ethnicity_data = {
    #     "White British": 95.0,
    #     "Mixed": 2.5,
    #     "Bangladeshi": 0.6
    # }
    # restaurants = [
    #     {"name": "Graze Kitchen Company", "distance": "0.3 miles"},
    #     {"name": "The Orange Tree Restaurant", "distance": "0.5 miles"}
    # ]
    # pubs = [
    #     {"name": "Wenvoe Arms", "distance": "1.0 miles"},
    #     {"name": "Barry Rugby Club", "distance": "1.0 miles"}
    # ]

    # handler.add_crystal_data('UB1 3DA', ethnicity_data=ethnicity_data, restaurants=restaurants, pubs=pubs)

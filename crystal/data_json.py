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
    # Add or update postcode info
    def add_postcode_info(self, postcode):
        postcode = postcode.strip()
        
        # Check if postcode already exists, if not, create a new entry
        if postcode not in self.postcodes:
            self.postcodes[postcode] = {
                'crystal': {
                    'ethnicity': {},
                    'restaurants': {},
                    'pubs': {},
                    'income': {},
                    'occupation': {},
                    'transport': {'connectivity': {}, 'stations': []}
                }
            }
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


    def add_crystal_data(self, postcode, full_address=None, **kwargs):
        try:
            print(f"Adding crystal data for postcode: {postcode}")

            # Ensure postcode exists and initialize crystal data
            postcode = postcode.strip()
            if postcode not in self.postcodes:
                self.add_postcode_info(postcode)

            if 'crystal' not in self.postcodes[postcode]:
                self.postcodes[postcode]['crystal'] = {
                    'ethnicity': {},
                    'restaurants': {},
                    'pubs': {},
                    'income': {},
                    'occupation': {},
                    'transport': {'connectivity': {}, 'stations': []}
                }

            current_crystal_data = self.postcodes[postcode]['crystal']

            # Update full address if provided
            if full_address:
                self.postcodes[postcode]['address'] = full_address

            # Call specific category functions based on kwargs
            if 'ethnicity_data' in kwargs:
                self.add_ethnicity_data(current_crystal_data, kwargs['ethnicity_data'])
            if 'restaurants_data' in kwargs:
                self.add_restaurants_data(current_crystal_data, kwargs['restaurants_data'])
            if 'pubs_data' in kwargs:
                self.add_pubs_data(current_crystal_data, kwargs['pubs_data'])
            if 'household_income_data' in kwargs:
                self.add_household_income_data(current_crystal_data, kwargs['household_income_data'])
            if 'neighbourhood_income_data' in kwargs:
                self.add_neighbourhood_income_data(current_crystal_data, kwargs['neighbourhood_income_data'])
            if 'occupation_data' in kwargs:
                self.add_occupation_data(current_crystal_data, kwargs['occupation_data'], kwargs.get('occupation_location_text'))
            if 'connectivity_data' in kwargs or 'stations_data' in kwargs:
                self.add_transport_data(current_crystal_data, kwargs.get('connectivity_data'), kwargs.get('stations_data'))

            # Save to JSON
            self.save_json()

        except Exception as e:
            print(f"Error occurred while adding crystal data for postcode {postcode}: {str(e)}")
            print(traceback.format_exc())

    def add_household_income_data(self, crystal_data, household_income_data):
        if household_income_data is not None and not household_income_data.empty:
            crystal_data['income']['average_income'] = household_income_data['income'][0]
            crystal_data['income']['rating'] = household_income_data['rating'][0]

    def add_neighbourhood_income_data(self, crystal_data, neighbourhood_income_data):
        if neighbourhood_income_data is not None and not neighbourhood_income_data.empty:
            neighbourhood_income_dict = {row['Area']: row['Income'] for _, row in neighbourhood_income_data.iterrows()}
            crystal_data['income'].update(neighbourhood_income_dict)

    def add_ethnicity_data(self, crystal_data, ethnicity_data):
        if ethnicity_data is not None and not ethnicity_data.empty:
            ethnicity_list = {row['Demographics']: row['Percentage'] for _, row in ethnicity_data.iterrows()}
            crystal_data['ethnicity'].update(ethnicity_list)

    def add_restaurants_data(self, crystal_data, restaurants_data):
        if restaurants_data is not None and not restaurants_data.empty:
            restaurant_dict = {row['Restaurant']: row['Distance'] for _, row in restaurants_data.iterrows()}
            crystal_data['restaurants'].update(restaurant_dict)

    def add_pubs_data(self, crystal_data, pubs_data):
        if pubs_data is not None and not pubs_data.empty:
            pub_dict = {row['Pub']: row['Distance'] for _, row in pubs_data.iterrows()}
            crystal_data['pubs'].update(pub_dict)

    def add_occupation_data(self, crystal_data, occupation_data, occupation_location_text=None):
        if occupation_data is not None and not occupation_data.empty:
            occupation_dict = {row['Occupation']: row['Percentage'] for _, row in occupation_data.iterrows()}
            crystal_data['occupation'].update(occupation_dict)
        if occupation_location_text:
            crystal_data['occupation']['occupation_location_text'] = occupation_location_text

    def add_transport_data(self, crystal_data, connectivity_data=None, stations_data=None):
        if 'transport' not in crystal_data:
                crystal_data['transport'] ={'connectivity':{},'stations':{}}
        if connectivity_data is not None and not connectivity_data.empty:
            connectivity_dict = {
                'connectivity to public transport': connectivity_data.iloc[0]['connectivity to public transport'],
                'travel zone': connectivity_data.iloc[0]['travel zone']
            }
            crystal_data['transport']['connectivity'] = connectivity_dict
        if stations_data is not None and not stations_data.empty:
            station_data_list = []
            for _, row in stations_data.iterrows():
                station_data = {
                    'station_name': row['station_name'],
                    'distance': row['distance'],
                    'lines': row['lines']
                }
                station_data_list.append(station_data)
            crystal_data['transport']['stations'] = station_data_list



        # def add_crystal_data(self, postcode, ethnicity_data, restaurants, pubs, df_household_income, df_neighbourhood_income, full_address, df_occupation, occupation_location_text,connectivity_df,stations_df):
        #     try:
        #         print("______________________________________________in add crsyal json _____________________________________________________________________________________")
        #         # Ensure postcode exists and strip any extra whitespace
        #         postcode = postcode.strip()

        #         # Ensure the postcode entry exists
        #         if postcode not in self.postcodes:
        #             self.add_postcode_info(postcode, None, None)

        #         # Initialize crystal data if it doesn't exist
        #         if 'crystal' not in self.postcodes[postcode]:
        #             self.postcodes[postcode]['crystal'] = {
        #                 'ethnicity': {},
        #                 'restaurants': {},
        #                 'pubs': {},
        #                 'income': {},      # Initialize income here
        #                 'occupation': {},  # Initialize occupation here
        #                 'transport':{'connectivity':{},'stations':{}}
        #             }

        #         # Access crystal data directly
        #         current_crystal_data = self.postcodes[postcode]['crystal']

        #         # Initialize the 'income' key if it doesn't exist
        #         if 'income' not in current_crystal_data:
        #             current_crystal_data['income'] = {}

        #         # Initialize the 'occupation' key if it doesn't exist
        #         if 'occupation' not in current_crystal_data:
        #             current_crystal_data['occupation'] = {}

        #         # Add ethnicity data
        #         if ethnicity_data is not None and not ethnicity_data.empty:
        #             ethnicity_list = {row['Demographics']: row['Percentage'] for _, row in ethnicity_data.iterrows()}
        #             current_crystal_data['ethnicity'].update(ethnicity_list)

        #         # Add restaurant data as a dictionary
        #         if restaurants is not None and not restaurants.empty:
        #             restaurant_dict = {row['Restaurant']: row['Distance'] for _, row in restaurants.iterrows()}
        #             current_crystal_data['restaurants'].update(restaurant_dict)

        #         # Add pub data as a dictionary
        #         if pubs is not None and not pubs.empty:
        #             pub_dict = {row['Pub']: row['Distance'] for _, row in pubs.iterrows()}
        #             current_crystal_data['pubs'].update(pub_dict)

        #         # Add household income data
        #         print("df household income ",df_household_income)
        #         if df_household_income is not None and not df_household_income.empty:
        #             current_crystal_data['income']['average_income']=df_household_income['income'][0]
        #             current_crystal_data['income']['rating']=df_household_income['rating'][0]
        #             # income_dict = {row['income']: row['rating'] for _, row in df_household_income.iterrows()}
        #             # current_crystal_data['income'].update(income_dict)

        #         # Add neighborhood income data
        #         if df_neighbourhood_income is not None and not df_neighbourhood_income.empty:
        #             neighbourhood_income_dict = {row['Area']: row['Income'] for _, row in df_neighbourhood_income.iterrows()}
        #             current_crystal_data['income'].update(neighbourhood_income_dict)

        #         # Add occupation data
        #         if df_occupation is not None and not df_occupation.empty:
        #             occupation_dict = {row['Occupation']: row['Percentage'] for _, row in df_occupation.iterrows()}
        #             current_crystal_data['occupation'].update(occupation_dict)
        #             current_crystal_data['occupation']['occupation_location_text'] = occupation_location_text

        #         self.postcodes[postcode]['address'] = full_address


        #         if 'transport' not in current_crystal_data:
        #             current_crystal_data['transport'] ={'connectivity':{},'stations':{}}
        #         #add transport data 
        #         print(connectivity_df,stations_df)
        #         if connectivity_df is not None and not connectivity_df.empty:
        #             connectivity_dict = {
        #                 'connectivity to public transport': connectivity_df.iloc[0]['connectivity to public transport'],
        #                 'travel zone': connectivity_df.iloc[0]['travel zone']
        #             }
        #             print(connectivity_dict)
        #             current_crystal_data['transport']['connectivity']=connectivity_dict



        #         if stations_df is not None and not stations_df.empty:
        #             station_data_list = []
        
        #             # Iterate over each row in stations_df to populate station details
        #             for _, row in stations_df.iterrows():
        #                 station_data = {
        #                     'station_name': row['station_name'],  # Assuming the station name is the index of the DataFrame
        #                     'distance': row['distance'],
        #                     'lines': row['lines']
        #                 }
        #                 station_data_list.append(station_data)
                    
        #             print("_______________________________________________________________",station_data_list)    
        #                 # Add station data to `current_crystal_data`
        #             # Ensure 'transport' key exists in current_crystal_data



        #             current_crystal_data['transport']['stations']= station_data_list #update(station_data_list)
        #                 # Save changes to JSON

        #         self.save_json()
        #         print(self.postcodes[postcode],self.postcodes[postcode]['address'])
        #         for key, value in current_crystal_data.items() :
        #             print (key, value)

        #     except Exception as e:
        #         print(f"Error occurred while adding crystal data for postcode {postcode}: {str(e)}")
        #         print(traceback.format_exc())  # Log the traceback for debugging



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

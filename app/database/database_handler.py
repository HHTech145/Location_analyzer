from database.connector import Database
import json
import traceback

class PostcodeDataHandler:
    def __init__(self, db_config, json_file_path):
        self.db = Database(**db_config)
        self.json_file_path = json_file_path
        self.postcode_data = self.read_json()

    def read_json(self):
        """Read the JSON file and return the data."""
        with open(self.json_file_path, 'r') as json_file:
            return json.load(json_file)

    def get_postcode_info(self, postcode):
        postcode=postcode.strip()
        # print("__",postcode)    
        # print(self.postcode_data[postcode])
        # print("_______________________")
        # print("Available postcodes in JSON:", list(self.postcode_data.keys()))
        """Retrieve information for the given postcode from the loaded JSON data."""

        # Search for the postcode in the JSON data
        try:
            if postcode in self.postcode_data:
                postcode_info = self.postcode_data[postcode]  # Assuming postcode is the key
                # print("postcode_info____",postcode_info)
                demographics = postcode_info.get('demographics', {})
                crystal_data = postcode_info.get('crystal', {})

                # Extract additional information (radius, prediction, address) from the JSON
                radius = postcode_info.get('radius')
                prediction = postcode_info.get('prediction')
                address = postcode_info.get('address')
                min_prediction=postcode_info.get('min_prediction')
                max_prediction=postcode_info.get('max_preidiction')

                return postcode, radius, prediction, address, min_prediction,max_prediction,demographics, crystal_data
            else:
                raise ValueError(f"Postcode {postcode} not found in JSON data.")
        except Exception as e:
            print("No postcoe in json file")
            print(traceback.format_exc())

    def insert_into_database(self, postcode):
        try:
            """Insert extracted data for the given postcode into the database."""
            postcode_info = self.get_postcode_info(postcode)

            # Unpack postcode_info
            postcode, radius, prediction, address,min_prediction,max_prediction,demographics, crystal_data = postcode_info

            # Insert into postcodes table only if it doesn't exist
            # if not self.db.postcode_exists(postcode):
            self.db.insert_or_update_postcodes(postcode, radius, prediction, address,min_prediction,max_prediction)

            # Insert demographic data
            self.db.insert_or_update_postcode_area_demographics(
                postcode, 
                demographics['population'],
                demographics['households'],
                demographics['avg_household_income'],
                demographics['unemployment_rate'],
                demographics['working'],
                demographics['unemployed'],
                demographics['ab'],
                demographics['c1/c2'],
                demographics['de']
            )

            # Insert ethnicity data as JSON
            ethnicity_data = crystal_data.get('ethnicity', {})
            if ethnicity_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_ethnicity(postcode, ethnicity_data)

            # Insert occupation data
            occupation_data = crystal_data.get('occupation', {})
            if occupation_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_occupation(postcode, occupation_data)

            # Insert restaurants data
            restaurants_data = crystal_data.get('restaurants', {})
            if restaurants_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_restaurants(postcode, restaurants_data)

            # Insert pubs data
            pubs_data = crystal_data.get('pubs', {})
            if pubs_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_pubs(postcode, pubs_data)

            # Insert income data as JSON
            income_data = crystal_data.get('income', {})
            if income_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_income(postcode, income_data)

            # Insert income data as JSON
            transport_data = crystal_data.get('transport', {})
            if transport_data:  # Ensure data exists before inserting
                self.db.insert_or_update_crystal_transport(postcode, transport_data)
        except Exception as e:
            print(traceback.format_exc())

    def get_average_prediction_from_db(self,postcode):
        """Extract data for the given postcode into the database."""
        try:
            postcode_info = self.get_postcode_info(postcode)
            if postcode_info:

                # Unpack postcode_info
                postcode, radius, prediction, address,min_prediction,max_prediction,demographics, crystal_data = postcode_info

                s={'prediction_data':{'postcode':postcode,'radius':radius,'min_prediction':min_prediction,'max_prediction':max_prediction,'avg_prediction':prediction}}
                print(s)
                return s
            else:
                s={'Warning:':'kindly process the postcode first then run the API.'}
                return s
        except Exception as e:
            print(traceback.format_exc())

    def if_postcode_exists(self,postcode):
        postcode=postcode.strip()
        """Retrieve information for the given postcode from the loaded JSON data."""

        # Search for the postcode in the JSON data
        try:
            if postcode in self.postcode_data:
                return True
            else:
                False
        except Exception as e:
            print(traceback.format_exc())

    def close_database(self):
        """Close the database connection."""
        self.db.close()

if __name__ == "__main__":
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
    postcode = "AL10 9AY"  # Replace with the actual postcode you want to search
    postcode_handler.insert_into_database(postcode)
    postcode_handler.close_database()

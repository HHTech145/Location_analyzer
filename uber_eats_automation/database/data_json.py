import os,sys
import json
import traceback
import re 
# Add the app directory to sys.path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connector import Database


class JsonDataHandler:
    def __init__(self, json_file,db_config):
        self.db = Database(**db_config)
        self.json_file = json_file
        self.orders = self.load_json()

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

    # Save the current orders data back to the JSON file
    def save_json(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.orders, f, indent=4)

    # Add a new order
    def add_order(self, order_id, order_details, order_time_details=None, order_meal_details=None, order_price_details=None):
        # order_details['Order placed time']=
        order_details['Order placed time'] = re.sub(r"(\d{4})(\d)", r"\1 \2", order_details['Order placed time'])
        order_details['Delivery Time'] = re.sub(r"(\d{4})(\d)", r"\1 \2", order_details['Delivery Time'])
        
        self.orders[order_id] = {
            'order_details': order_details,
            'order_time_details': order_time_details if order_time_details is not None else {},
            'order_meal_details': order_meal_details if order_meal_details is not None else {},
            'order_price_details': order_price_details if order_price_details is not None else {}
        }
        self.save_json()  # Save after adding the new order

    # Example method to retrieve an order by ID
    def get_order(self, order_id):
        return self.orders.get(order_id, None)
    # Insert or update an order into the database

    def insert_order_into_database(self, order_id):
        print("__in insert _________________")
        order_data = self.get_order(order_id)
        
        if not order_data:
            print(f"Order ID {order_id} not found in JSON data.")
            return

        # Insert order details, time details, meal details, and price details using database methods
        try:
            # Insert or update order details
            order_details = order_data.get('order_details', {})
            print(order_details)
            self.db.insert_update_orders(order_details)

            # Insert or update order time details
            # order_time_details = order_data.get('order_time_details', [])
            # self.db.insert_or_update_order_time_details(order_id, order_time_details)

            # Insert or update order meal details
            order_meal_details = order_data.get('order_meal_details', [])
            self.db.insert_order_meals_with_customizations(order_id, order_meal_details)

            # Insert or update order price details
            order_price_details = order_data.get('order_price_details', [])
            self.db.insert_update_order_price_details(order_id, order_price_details)

            print(f"Order {order_id} inserted or updated in the database successfully.")
        
        except Exception as e:
            print(f"Failed to insert order {order_id} into the database: {e}")
            traceback.print_exc()

    def close_database(self):
        """Close the database connection."""
        self.db.close()


# Usage example
if __name__ == "__main__":
    # json_handler = JsonDataHandler('orders.json')

    db_config = {
        "host": "localhost",
        "user": "htech_ai",
        "password": "Htech786##",
        "database": "uber_eats_db"  # Assuming you have a database to connect to
    }

    # Path to your JSON file
    json_file_path = "orders.json"

    # Example usage
    json_db_handler = JsonDataHandler(db_config, json_file_path)    

    order_id="71795"
    json_db_handler.insert_order_into_database()

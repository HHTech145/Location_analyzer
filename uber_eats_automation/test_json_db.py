import pandas as pd
import pickle
from datetime import datetime, timedelta
import traceback
import os, sys 
# Add the app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#import database class 
from database.data_json import JsonDataHandler


def save_data_to_database():
    # Database configuration
    # db_config = {
    #     "host": "localhost",
    #     "user": "htech_ai",
    #     "password": "Htech786##",
    #     "database": "uber_eats_db"  # Assuming you have a database to connect to
    # }

    db_config = {
        'host': '87.117.234.167',
        'user': 'py_isb',
        'password': '7iIG3.X/T(ObjTK8',
        'database': 'py_uber'
    }

# db = Database(host="87.117.234.167", user="py_isb", password="7iIG3.X/T(ObjTK8",port=80,database="py_uber")
    # Path to your JSON file
    json_file_path = "orders.json"

    # Example usage
    json_db_handler = JsonDataHandler(json_file_path,db_config)    

    order_id="6F0EE"
    print("________")
    json_db_handler.insert_order_into_database(order_id)
    json_db_handler.close_database() 

if __name__ == "__main__":
    save_data_to_database()
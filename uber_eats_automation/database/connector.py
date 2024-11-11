import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import traceback
class Database:
    def __init__(self, host="localhost", user="root", password="", port="",database=None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port=port
        self.connection = None
        self.connect()

    def connect(self):
        try:
            if self.database:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            else:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
            if self.connection.is_connected():
                print("Connection successful!")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_database(self, db_name):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created successfully!")
        except Error as e:
            print(f"Error creating database: {e}")
        finally:
            cursor.close()

    def initialize_database(self, db_name):
        try:
            self.connection.database = db_name
            print(f"Database '{db_name}' selected.")
        except Error as e:
            print(f"Error selecting database: {e}")

    def create_tables(self):
        try:
            cursor = self.connection.cursor()
            sql_statements = [
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(10) PRIMARY KEY,
                    store_details VARCHAR(255),
                    order_placed VARCHAR(255),
                    delivery VARCHAR(255),
                    customer VARCHAR(255),
                    fulfilment VARCHAR(255),
                    courier VARCHAR(255),
                    subtotal DECIMAL(10, 2)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS order_meals (
                    meal_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id VARCHAR(10),
                    meal_name VARCHAR(255),
                    price DECIMAL(10, 2),
                    quantity INT,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
                );
                """,  # Removed the extra closing parenthesis here
                """
                CREATE TABLE IF NOT EXISTS meal_customizations (
                    customization_id INT AUTO_INCREMENT PRIMARY KEY,
                    meal_id INT,
                    customization_name VARCHAR(255),
                    customization_details VARCHAR(255),
                    customization_price DECIMAL(10, 2) DEFAULT 0,
                    FOREIGN KEY (meal_id) REFERENCES order_meals(meal_id) ON DELETE CASCADE
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS order_price_details (
                    price_detail_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id VARCHAR(10),
                    description ENUM('Subtotal', 'Special Offer', 'Estimated Payout') NOT NULL,
                    amount DECIMAL(10, 2),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
                );
                """
            ]
            
            for sql in sql_statements:
                cursor.execute(sql)
            
            self.connection.commit()
            print("Tables created successfully.")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()  # Optional: Rollback in case of any error
        finally:
            cursor.close()


    def insert_update_orders(self, order_details):
        try:
            cursor = self.connection.cursor()
            sql = """
                INSERT INTO orders (order_id, store_details, order_placed,
                                        delivery, customer, fulfilment, courier, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    store_details = VALUES(store_details),
                    order_placed = VALUES(order_placed),
                    delivery = VALUES(delivery),
                    customer = VALUES(customer),
                    fulfilment = VALUES(fulfilment),
                    courier = VALUES(courier),
                    subtotal = VALUES(subtotal)
            """ 
            values = (
                order_details['Order ID'],
                order_details['Store Details'],
                order_details['Order placed time'],
                order_details['Delivery Time'],
                order_details['Customer'],
                order_details['Fulfilment'],
                order_details['Courier'],
                order_details['Subtotal']  # Ensure subtotal is a proper decimal, remove currency symbol if necessary
            )
            cursor.execute(sql, values)
            self.connection.commit()
            print("Order details inserted or updated successfully.")
        
        except mysql.connector.Error as err:
            print(f"Error: orders id isnertion-- {err}")
        
        finally:
            cursor.close()


    def insert_update_order_price_details(self, order_id, order_price_details):
        try:
            cursor = self.connection.cursor()

            for detail in order_price_details:
                description = detail['description']
                amount = detail['amount']

                # Check if record exists
                cursor.execute("""
                    SELECT COUNT(*) FROM order_price_details 
                    WHERE order_id = %s AND description = %s
                """, (order_id, description))
                exists = cursor.fetchone()[0]

                if exists:
                    # Update if exists
                    sql = """
                        UPDATE order_price_details 
                        SET amount = %s 
                        WHERE order_id = %s AND description = %s
                    """
                    cursor.execute(sql, (amount, order_id, description))
                else:
                    # Insert if not exists
                    sql = """
                        INSERT INTO order_price_details (order_id, description, amount)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (order_id, description, amount))

            # Commit all changes after loop
            self.connection.commit()
            print("Order price details inserted/updated successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection.rollback()  # Rollback on error
        
        finally:
            cursor.close()


    # def insert_update_order_price_details(self, order_id, order_price_details):
    #     try:
    #         cursor = self.connection.cursor()

    #         # Iterate over each price detail in order_price_details JSON array
    #         for detail in order_price_details:
    #             description = detail['description']
    #             amount = detail['amount']
                
    #             # Insert or update each entry in the order_price_details table
    #             sql = """
    #                 INSERT INTO order_price_details (order_id, description, amount)
    #                 VALUES (%s, %s, %s)
    #                 ON DUPLICATE KEY UPDATE
    #                     amount = VALUES(amount)
    #             """
    #             cursor.execute(sql, (order_id, description, amount))

    #         # Commit the transaction after all inserts/updates
    #         self.connection.commit()
    #         print("Order price details inserted/updated successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error: {err}")
    #         self.connection.rollback()  # Rollback on error
        
    #     finally:
    #         cursor.close()


    def insert_order_meals_with_customizations(self, order_id, order_meal_details):
        try:
            cursor = self.connection.cursor()

            for meal in order_meal_details:
                meal_name = meal['meal_name']
                meal_price = meal['meal_price']
                quantity = int(meal['quantity'])

                # Check if the meal exists for this order
                cursor.execute("""
                    SELECT meal_id FROM order_meals
                    WHERE order_id = %s AND meal_name = %s
                """, (order_id, meal_name))
                meal_record = cursor.fetchone()

                if meal_record:
                    # Update meal if it exists
                    meal_id = meal_record[0]
                    cursor.execute("""
                        UPDATE order_meals SET price = %s, quantity = %s
                        WHERE meal_id = %s
                    """, (meal_price, quantity, meal_id))
                else:
                    # Insert new meal if it doesn't exist
                    meal_sql = """
                        INSERT INTO order_meals (order_id, meal_name, price, quantity)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(meal_sql, (order_id, meal_name, meal_price, quantity))
                    meal_id = cursor.lastrowid

                # Process customizations
                for customization in meal.get('customizations', []):
                    customization_name = customization['customization']
                    options = customization['options']

                    for option in options:
                        name = option['option']
                        price = option['price']

                        # Check if the customization exists for this meal
                        cursor.execute("""
                            SELECT customization_id FROM meal_customizations
                            WHERE meal_id = %s AND customization_name = %s AND customization_details = %s
                        """, (meal_id, customization_name, name))
                        customization_record = cursor.fetchone()

                        if customization_record:
                            # Update customization if it exists
                            customization_id = customization_record[0]
                            cursor.execute("""
                                UPDATE meal_customizations SET customization_price = %s
                                WHERE customization_id = %s
                            """, (price, customization_id))
                        else:
                            # Insert new customization if it doesn't exist
                            customization_sql = """
                                INSERT INTO meal_customizations (meal_id, customization_name, customization_details, customization_price)
                                VALUES (%s, %s, %s, %s)
                            """
                            cursor.execute(customization_sql, (meal_id, customization_name, name, price))

            self.connection.commit()
            print("Order meals and customizations inserted/updated successfully.")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print(traceback.format_exc())
            self.connection.rollback()
        
        finally:
            cursor.close()


    # def insert_order_meals_with_customizations(self, order_id, order_meal_details):
    #     try:
    #         cursor = self.connection.cursor()

    #         # Iterate over each meal in order_meal_details
    #         for meal in order_meal_details:
    #             meal_name = meal['meal_name']
    #             meal_price = meal['meal_price']
    #             quantity = int(meal['quantity'])

    #             # Insert meal into order_meals table and get meal_id
    #             meal_sql = """
    #                 INSERT INTO order_meals (order_id, meal_name, price, quantity)
    #                 VALUES (%s, %s, %s, %s)
    #             """
    #             cursor.execute(meal_sql, (order_id, meal_name, meal_price, quantity))
    #             meal_id = cursor.lastrowid  # Get the last inserted meal_id for customizations

    #             # Process each customization for the meal
    #             for customization in meal['customizations']:
    #                 customization_name = customization['customization']
    #                 options = customization['options']
    #                 for i in options:

    #                     name= i['option']
    #                     price=i['price']

    #                     # Join options into a comma-separated string
    #                     # options_str = ', '.join(options)

    #                     # Insert the customization with the joined options
    #                     customization_sql = """
    #                         INSERT INTO meal_customizations (meal_id, customization_name, customization_details, customization_price)
    #                         VALUES (%s, %s, %s, %s)
    #                     """
    #                     cursor.execute(customization_sql, (meal_id, customization_name, name, price))

    #         # Commit all inserts if successful
    #         self.connection.commit()
    #         print("Order meals and customizations inserted successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error: {err}")
    #         print(traceback.format_exc())
    #         self.connection.rollback()  # Rollback on error
        
    #     finally:
    #         cursor.close()

    # def insert_or_update_order_details(self, order_details):
    #     print("insert orders ---------------------------------------------")
    #     try:
    #         cursor = self.connection.cursor()
    #         sql = """
    #             INSERT INTO order_details (order_id, store_details, order_placed,
    #                                     delivery, customer, fulfilment, courier, subtotal)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    #             ON DUPLICATE KEY UPDATE 
    #                 store_details = VALUES(store_details),
    #                 order_placed = VALUES(order_placed),
    #                 delivery = VALUES(delivery),
    #                 customer = VALUES(customer),
    #                 fulfilment = VALUES(fulfilment),
    #                 courier = VALUES(courier),
    #                 subtotal = VALUES(subtotal)
    #         """ 
    #         values = (
    #             order_details['Order ID'],
    #             order_details['Store Details'],
    #             order_details['Order placed time'],
    #             order_details['Delivery Time'],
    #             order_details['Customer'],
    #             order_details['Fulfilment'],
    #             order_details['Courier'],
    #             order_details['Subtotal']  # Ensure subtotal is a proper decimal, remove currency symbol if necessary
    #         )
    #         cursor.execute(sql, values)
    #         self.connection.commit()
    #         print("Order details inserted or updated successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error: orders id isnertion-- {err}")
        
    #     finally:
    #         cursor.close()
    # def insert_or_update_order_time_details(self, order_id, time_details):
    #     print("Inserting or updating order time details...")
    #     try:
    #         cursor = self.connection.cursor()
    #         sql = """
    #             INSERT INTO order_time_details (order_id, time_details)
    #             VALUES (%s, %s)
    #             ON DUPLICATE KEY UPDATE 
    #                 time_details = VALUES(time_details)
    #         """
    #         values = (order_id, json.dumps(time_details))  # Convert time details to JSON string
    #         cursor.execute(sql, values)
    #         self.connection.commit()
    #         print("Order time details inserted or updated successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error inserting/updating order time details: {err}")
        
    #     finally:
    #         cursor.close()

    # def insert_or_update_order_meal_details(self, order_id, meal_price_details):
    #     print("Inserting or updating order meal details...")
    #     try:
    #         cursor = self.connection.cursor()
    #         sql = """
    #             INSERT INTO order_meal_details (order_id, meal_price_details)
    #             VALUES (%s, %s)
    #             ON DUPLICATE KEY UPDATE 
    #                 meal_price_details = VALUES(meal_price_details)
    #         """
    #         values = (order_id, json.dumps(meal_price_details))  # Convert meal price details to JSON string
    #         cursor.execute(sql, values)
    #         self.connection.commit()
    #         print("Order meal details inserted or updated successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error inserting/updating order meal details: {err}")
        
    #     finally:
    #         cursor.close()

    # def insert_or_update_order_price_details(self, order_id, order_price_details):
    #     print("Inserting or updating order price details...")
    #     try:
    #         cursor = self.connection.cursor()
    #         sql = """
    #             INSERT INTO order_price_details (order_id, order_price_details)
    #             VALUES (%s, %s)
    #             ON DUPLICATE KEY UPDATE 
    #                 order_price_details = VALUES(order_price_details)
    #         """
    #         values = (order_id, json.dumps(order_price_details))  # Convert order price details to JSON string
    #         cursor.execute(sql, values)
    #         self.connection.commit()
    #         print("Order price details inserted or updated successfully.")
        
    #     except mysql.connector.Error as err:
    #         print(f"Error inserting/updating order price details: {err}")
        
    #     finally:
    #         cursor.close()

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    db = Database(host="87.117.234.167", user="py_isb", password="7iIG3.X/T(ObjTK8",port=80,database="py_uber")
    # db.create_database("py_uber")
    # Initialize the database (connect to it)
    db.initialize_database("py_uber")
    # Call the function to create tables
    # db.create_tables()
    # Close the connection
    db.close()
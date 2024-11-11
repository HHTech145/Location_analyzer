import mysql.connector
from mysql.connector import Error
import json


class Database:
    def __init__(self, host="localhost", user="root", password="", database=None):
        """
        Initialize the connection to the MySQL database.
        If a database is provided, it will connect to that database.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the MySQL server"""
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
        """Create a new database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created successfully!")
        except Error as e:
            print(f"Error creating database: {e}")
        finally:
            cursor.close()

    def initialize_database(self, db_name):
        """Select and initialize the database"""
        try:
            self.connection.database = db_name
            print(f"Database '{db_name}' selected.")
        except Error as e:
            print(f"Error selecting database: {e}")
            
    def create_tables(self):
        # Connect to MySQL database
        """Create tables using the initialized connection"""
        try:
            cursor = self.connection.cursor()

         # SQL statements to create tables
            sql_statements = [
                """
                CREATE TABLE IF NOT EXISTS postcodes (
                    postcode VARCHAR(10) PRIMARY KEY,
                    radius DECIMAL(5,2),
                    prediction DECIMAL(15,5),
                    address VARCHAR(255)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS postcode_area_demographics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    postcode VARCHAR(10) UNIQUE, 
                    population INT,
                    households INT,
                    avg_household_income DECIMAL(10,2),
                    unemployment_rate DECIMAL(4,4),
                    working DECIMAL(4,2),
                    unemployed DECIMAL(4,2),
                    ab DECIMAL(4,2),
                    c1_c2 DECIMAL(4,2),
                    de DECIMAL(4,2),
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_ethnicity (
                    postcode VARCHAR(10) PRIMARY KEY,
                    ethnicity JSON
                );  
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_restaurants (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    postcode VARCHAR(10) UNIQUE,
                    restaurants JSON,
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_pubs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    postcode VARCHAR(10) UNIQUE,
                    pubs JSON,
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_income (
                    postcode VARCHAR(10) PRIMARY KEY,
                    income JSON,
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_transport (
                    postcode VARCHAR(10) PRIMARY KEY,
                    transport JSON,
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS crystal_occupation (
                    postcode VARCHAR(10) PRIMARY KEY,
                    occupation JSON,
                    FOREIGN KEY (postcode) REFERENCES postcodes(postcode)
                );
                """
            ]
            # Execute all SQL statements
            for sql in sql_statements:
                cursor.execute(sql)
            
            # Commit changes
            self.connection.commit()
            print("Tables created successfully.")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
        finally:
            cursor.close()
    
    def postcode_exists(self, postcode):
        cursor = self.connection.cursor()
        """Check if the given postcode exists in the postcodes table."""
        query = "SELECT COUNT(*) FROM postcodes WHERE postcode = %s"

        cursor.execute(query, (postcode,))
        result = cursor.fetchone()
        return result[0] > 0  # Return True if exists, False otherwise

    def insert_or_update_postcodes(self, postcode, radius, prediction, address, min_prediction, max_prediction):
        print("__________________________________________________in postcode insert database ---------------------------------------------------------------------")
        """Insert or update data into the postcodes table"""
        try:
            cursor = self.connection.cursor()
            sql = """INSERT INTO postcodes (postcode, radius, prediction, address, min_prediction, max_prediction) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE radius = VALUES(radius), 
                                            prediction = VALUES(prediction), 
                                            address = VALUES(address), 
                                            min_prediction = VALUES(min_prediction), 
                                            max_prediction = VALUES(max_prediction)"""
            cursor.execute(sql, (postcode, radius, prediction, address, min_prediction, max_prediction))
            self.connection.commit()
            print(f"Upserted data into postcodes: {postcode}")
        except Error as e:
            print(f"Error inserting or updating postcodes: {e}")
        finally:
            cursor.close()

    def insert_or_update_postcode_area_demographics(self, postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de):
        """Insert or update data into the postcode_area_demographics table"""
        try:
            cursor = self.connection.cursor()
            sql = """INSERT INTO postcode_area_demographics 
                    (postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE population = VALUES(population), 
                                            households = VALUES(households), 
                                            avg_household_income = VALUES(avg_household_income), 
                                            unemployment_rate = VALUES(unemployment_rate), 
                                            working = VALUES(working), 
                                            unemployed = VALUES(unemployed), 
                                            ab = VALUES(ab), 
                                            c1_c2 = VALUES(c1_c2), 
                                            de = VALUES(de)"""
            cursor.execute(sql, (postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de))
            self.connection.commit()
            print(f"Upserted data into postcode_area_demographics: {postcode}")
        except Error as e:
            print(f"Error inserting or updating postcode_area_demographics: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_ethnicity(self, postcode, ethnicity_data):
        """Insert or update data into the crystal_ethnicity table"""
        try:
            cursor = self.connection.cursor()
            ethnicity_json = json.dumps(ethnicity_data)
            sql = """INSERT INTO crystal_ethnicity (postcode, ethnicity) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE ethnicity = VALUES(ethnicity)"""
            cursor.execute(sql, (postcode, ethnicity_json))
            self.connection.commit()
            print(f"Upserted data into crystal_ethnicity: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_ethnicity: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_restaurants(self, postcode, restaurants):
        """Insert or update data into the crystal_restaurants table"""
        try:
            cursor = self.connection.cursor()
            restaurants_json = json.dumps(restaurants)
            sql = """INSERT INTO crystal_restaurants (postcode, restaurants) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE restaurants = VALUES(restaurants)"""
            cursor.execute(sql, (postcode, restaurants_json))
            self.connection.commit()
            print(f"Upserted data into crystal_restaurants: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_restaurants: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_pubs(self, postcode, pubs):
        """Insert or update data into the crystal_pubs table"""
        try:
            cursor = self.connection.cursor()
            pubs_json = json.dumps(pubs)
            sql = """INSERT INTO crystal_pubs (postcode, pubs) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE pubs = VALUES(pubs)"""
            cursor.execute(sql, (postcode, pubs_json))
            self.connection.commit()
            print(f"Upserted data into crystal_pubs: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_pubs: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_income(self, postcode, income):
        """Insert or update data into the crystal_income table"""
        try:
            cursor = self.connection.cursor()
            income_json = json.dumps(income)
            sql = """INSERT INTO crystal_income (postcode, income) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE income = VALUES(income)"""
            cursor.execute(sql, (postcode, income_json))
            self.connection.commit()
            print(f"Upserted data into crystal_income: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_income: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_occupation(self, postcode, occupation):
        """Insert or update data into the crystal_occupation table"""
        try:
            cursor = self.connection.cursor()
            occupation_json = json.dumps(occupation)
            sql = """INSERT INTO crystal_occupation (postcode, occupation) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE occupation = VALUES(occupation)"""
            cursor.execute(sql, (postcode, occupation_json))
            self.connection.commit()
            print(f"Upserted data into crystal_occupation: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_occupation: {e}")
        finally:
            cursor.close()

    def insert_or_update_crystal_transport(self, postcode, transport):
        """Insert or update data into the crystal transport table"""
        try:
            cursor = self.connection.cursor()
            transport_json = json.dumps(transport)
            sql = """INSERT INTO crystal_transport (postcode, transport) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE transport = VALUES(transport)"""
            cursor.execute(sql, (postcode, transport_json))
            self.connection.commit()
            print(f"Upserted data into crystal_transport: {postcode}")
        except Error as e:
            print(f"Error inserting or updating crystal_transport: {e}")
        finally:
            cursor.close()

    # def insert_into_postcodes(self, postcode, radius, prediction, address):
    #     """Insert data into the postcodes table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM postcodes WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO postcodes (postcode, radius, prediction, address) 
    #                      VALUES (%s, %s, %s, %s)"""
    #             cursor.execute(sql, (postcode, radius, prediction, address))
    #             self.connection.commit()
    #             print(f"Inserted data into postcodes: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in postcodes: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into postcodes: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_postcode_area_demographics(self, postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de):
    #     """Insert data into the postcode_area_demographics table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM postcode_area_demographics WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO postcode_area_demographics 
    #                      (postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de) 
    #                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    #             cursor.execute(sql, (postcode, population, households, avg_household_income, unemployment_rate, working, unemployed, ab, c1_c2, de))
    #             self.connection.commit()
    #             print(f"Inserted data into postcode_area_demographics: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in postcode_area_demographics: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into postcode_area_demographics: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_crystal_ethnicity(self, postcode, ethnicity_data):
    #     """Insert data into the crystal_ethnicity table as JSON"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM crystal_ethnicity WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             # Convert Python dictionary to JSON string
    #             ethnicity_json = json.dumps(ethnicity_data)
    #             sql = """INSERT INTO crystal_ethnicity (postcode, ethnicity) 
    #                      VALUES (%s, %s)"""
    #             cursor.execute(sql, (postcode, ethnicity_json))
    #             self.connection.commit()
    #             print(f"Inserted data into crystal_ethnicity: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in crystal_ethnicity: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into crystal_ethnicity: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_crystal_restaurants(self, postcode, restaurants):
    #     """Insert data into the crystal_restaurants table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM crystal_restaurants WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO crystal_restaurants (postcode, restaurants) 
    #                      VALUES (%s, %s)"""
    #             cursor.execute(sql, (postcode, json.dumps(restaurants)))
    #             self.connection.commit()
    #             print(f"Inserted data into crystal_restaurants: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in crystal_restaurants: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into crystal_restaurants: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_crystal_pubs(self, postcode, pubs):
    #     """Insert data into the crystal_pubs table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM crystal_pubs WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO crystal_pubs (postcode, pubs) 
    #                      VALUES (%s, %s)"""
    #             cursor.execute(sql, (postcode, json.dumps(pubs)))
    #             self.connection.commit()
    #             print(f"Inserted data into crystal_pubs: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in crystal_pubs: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into crystal_pubs: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_crystal_income(self, postcode, income):
    #     """Insert data into the crystal_income table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM crystal_income WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO crystal_income (postcode, income) 
    #                      VALUES (%s, %s)"""
    #             cursor.execute(sql, (postcode, json.dumps(income)))  # Convert income data to JSON format
    #             self.connection.commit()
    #             print(f"Inserted data into crystal_income: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in crystal_income: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into crystal_income: {e}")
    #     finally:
    #         cursor.close()

    # def insert_into_crystal_occupation(self, postcode, occupation):
    #     """Insert data into the crystal_occupation table"""
    #     try:
    #         cursor = self.connection.cursor()
    #         # Check if the postcode already exists
    #         cursor.execute("SELECT COUNT(*) FROM crystal_occupation WHERE postcode = %s", (postcode,))
    #         if cursor.fetchone()[0] == 0:  # If postcode does not exist
    #             sql = """INSERT INTO crystal_occupation (postcode, occupation) 
    #                      VALUES (%s, %s)"""
    #             cursor.execute(sql, (postcode, json.dumps(occupation)))  # Convert occupation data to JSON format
    #             self.connection.commit()
    #             print(f"Inserted data into crystal_occupation: {postcode}")
    #         else:
    #             print(f"Data already exists for postcode in crystal_occupation: {postcode}")
    #     except Error as e:
    #         print(f"Error inserting into crystal_occupation: {e}")
    #     finally:
    #         cursor.close()

    def close(self):
        """Close the database connection"""
        if self.connection.is_connected():
            self.connection.close()
            print("Connection closed.")

# Example usage:

if __name__ == "__main__":
    db = Database(host="localhost", user="htech_ai", password="Htech786##")
    db.create_database("test_db")
    # Initialize the database (connect to it)
    db.initialize_database("test_db")
    # Call the function to create tables
    db.create_tables()
    # Close the connection
    db.close()
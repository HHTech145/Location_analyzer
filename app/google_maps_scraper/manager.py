# import os 
# import pandas as pd 

# class XLSXHandler:
#     def __init__(self):
#         self.folder_path="D:/work/automation/free_map_tools/final/Location_analyzer/app/output"

#     @staticmethod
#     def get_latest_csv_file(directory):
#         files = [f for f in os.listdir(directory) if f.endswith('.csv')]
#         if not files:
#             return None
#         full_paths = [os.path.join(directory, f) for f in files]
#         return max(full_paths, key=os.path.getmtime)
    

#     def check_postcode_in_files(self,postcode_with_space):
#         # Replace space with underscore in the postcode
#         postcode_with_underscore = postcode_with_space.replace(" ", "_")
        
#         # List all files in the folder
#         try:
#             files = os.listdir(self.folder_path)
#         except FileNotFoundError:
#             print(f"The folder {self.folder_path} was not found.")
#             return

#         # Check each file to see if the postcode (with underscores) is in the file name
#         matching_files = []
#         for file in files:
#             if postcode_with_underscore in file:
#                 matching_files.append(file)
        
#         # Return matching files
#         return matching_files
    
#     def laod_xlsx(self,postcode_with_space):
#         # File path string
#         # file_path = "google_maps_data_Universities_near_Walbrook,_EC2R_8DN.xlsx"

#         # Postcode to check (with space)
#         # postcode_with_space = "EC2R 8DN"

#         # Replace space with underscore
#         postcode_with_underscore = postcode_with_space.replace(" ", "_")

#         matching_files = self.check_postcode_in_files(postcode_with_underscore)

#         if matching_files:
#             df =pd.read_excel(matching_files[0])
#             return df


import os
import pandas as pd

class XLSXHandler:
    def __init__(self):
        self.folder_path = "D:/work/automation/free_map_tools/final/Location_analyzer/app/output"

    @staticmethod
    def get_latest_csv_file(directory):
        files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not files:
            return None
        full_paths = [os.path.join(directory, f) for f in files]
        return max(full_paths, key=os.path.getmtime)
    
    def check_postcode_in_files(self, postcode_with_space):
        # Replace space with underscore in the postcode
        postcode_with_underscore = postcode_with_space.replace(" ", "_")
        
        # List all files in the folder
        try:
            files = os.listdir(self.folder_path)
        except FileNotFoundError:
            print(f"The folder {self.folder_path} was not found.")
            return []

        # Check each file to see if the postcode (with underscores) is in the file name
        matching_files = []
        for file in files:
            if postcode_with_underscore in file:
                matching_files.append(file)
        
        # Return matching files
        return matching_files
    
    def load_xlsx(self, postcode_with_space):  # Fixed the typo here
        # Replace space with underscore
        postcode_with_underscore = postcode_with_space.replace(" ", "_")

        # Get matching files
        matching_files = self.check_postcode_in_files(postcode_with_underscore)

        if matching_files:
            # Load the first matching file into a DataFrame
            file_path = os.path.join(self.folder_path, matching_files[0])  # Get the full file path
            df = pd.read_excel(file_path)
            return df
        else:
            print(f"No matching files found for postcode {postcode_with_space}.")
            return None

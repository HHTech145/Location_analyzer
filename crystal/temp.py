import os
import shutil
import re

class TempCleaner:
    def __init__(self):
        """
        Initialize the TempCleaner object with the specified temp directory.
        
        :param temp_dir: Path to the temporary directory to clean
        """
        self.temp_dir = r"C:\Users\USER\AppData\Local\Temp"
        self.clean_temp_folders()
    
    def get_folder_size(self, folder_path):
        """
        Calculate the total size of a folder.
        
        :param folder_path: Path to the folder
        :return: Size in bytes
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # Skip if it's a broken symlink
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def format_size(self, size_in_bytes):
        """
        Format bytes into a human-readable format (KB, MB, GB).
        
        :param size_in_bytes: Size in bytes
        :return: Formatted size as a string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024

    def clean_tmp_folders(self):
        """
        Delete temporary folders matching the pattern 'tmp*',
        and print their sizes before deletion.
        """
        # pattern = re.compile(r"^tmp[a-z0-9]+$", re.IGNORECASE)
        pattern = re.compile(r"^tmp.*$", re.IGNORECASE)  # Match names starting with 'tmp'

        
        try:
            for folder_name in os.listdir(self.temp_dir):
                folder_path = os.path.join(self.temp_dir, folder_name)
                
                # Check if it matches the pattern and is a directory
                if os.path.isdir(folder_path) and pattern.match(folder_name):
                    try:
                        folder_size = self.get_folder_size(folder_path)
                        print(f"Folder: {folder_path}, Size: {self.format_size(folder_size)}")
                        
                        shutil.rmtree(folder_path)
                        print(f"Deleted: {folder_path}")
                    except Exception as e:
                        print(f"Failed to delete {folder_path}: {e}")
        except Exception as e:
            print(f"Error accessing the temp directory: {e}")
    
    def clean_chrome_temp_folders(self):
        """
        Delete Chrome temporary folders matching the pattern 'chrome_BITS_XXX_XXXXXXXX',
        and print their sizes before deletion.
        """
        pattern = re.compile(r"chrome_BITS_\d+_\d+")
        
        try:
            for folder_name in os.listdir(self.temp_dir):
                folder_path = os.path.join(self.temp_dir, folder_name)
                
                # Check if it matches the pattern and is a directory
                if os.path.isdir(folder_path) and pattern.match(folder_name):
                    try:
                        folder_size = self.get_folder_size(folder_path)
                        print(f"Folder: {folder_path}, Size: {self.format_size(folder_size)}")
                        
                        shutil.rmtree(folder_path)
                        print(f"Deleted: {folder_path}")
                    except Exception as e:
                        print(f"Failed to delete {folder_path}: {e}")
        except Exception as e:
            print(f"Error accessing the temp directory: {e}")

    def remove_tmp_files(self):
        """
        Delete all .tmp files in the specified directory and print their sizes before deletion.

        :param temp_dir: Path to the directory to clean
        """
        try:
            for file_name in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file_name)

                # Check if the file has a .tmp extension
                if os.path.isfile(file_path) and file_name.endswith('.tmp'):
                    try:
                        file_size = os.path.getsize(file_path)
                        print(f"File: {file_path}, Size: {self.format_size(file_size)}")
                        
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
        except Exception as e:
            print(f"Error accessing the temp directory: {e}")


    def clean_temp_folders(self):
        """
        This method will call both clean_tmp_folders and clean_chrome_temp_folders.
        """
        print("Starting to clean 'tmp' folders...")
        self.clean_tmp_folders()
        self.remove_tmp_files()
        print("Starting to clean 'chrome' temporary folders...")
        self.clean_chrome_temp_folders()
        


# Usage
if __name__ == "__main__":
    # Specify the temp directory path
    temp_directory = r"C:\Users\USER\AppData\Local\Temp"

    # Create an instance of the TempCleaner class, which will automatically start the cleaning process
    TempCleaner()

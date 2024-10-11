Location Analysis System
Overview
The Location Analysis System is designed to gather, analyze, and visualize demographic and amenities data based on UK postcodes. This system leverages web scraping, data processing, and machine learning to deliver insights that can assist businesses in selecting optimal locations for new branches or expanding operations.

Key Features
Postcode Data Retrieval: Automatically fetch demographic data for a given postcode.
Amenities Information: Gather nearby restaurant and pub details for a specific postcode radius.
Sales Prediction Model: Use demographic data to predict sales performance based on postal code.
Data Visualization: Generate HTML visualizations for analysis and presentation.
System Components
Web Scraper: Fetches demographic data and amenities details from various sources based on user-specified postcodes.
Prediction Model: Utilizes a trained machine learning model to predict potential sales.
Data Plotting: Creates visual representations of demographics, amenities, and sales predictions.
FastAPI Backend: Provides an API for interacting with the system and retrieving analysis results via HTTP requests.
Technology Stack
Python: Main programming language.
Pandas: For data manipulation.
FastAPI: API framework for efficient and rapid development.
Pickle: For saving and loading the prediction model.
BeautifulSoup & Selenium: For web scraping tasks.
dotenv: For environment variable management.
Machine Learning: XGBoost for predictions

Prerequisites
Python 3.8 or above
Required Python libraries (listed in requirements.txt)

FastAPI Documentation
Overview
The FastAPI component of the Location Analysis System provides a simple interface for interacting with the system through HTTP endpoints. Users can supply postcodes, receive demographic and amenities data, and run sales predictions via API requests.

Setting Up the FastAPI Server
Clone the Repository:

bash
Copy code
git clone https://github.com/your-username/location-analysis-system.git
cd location-analysis-system
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Set Environment Variables: Create a .env file in the root directory, specifying paths to your data and model files:

makefile
Copy code
xg_boost_model_path=models/xgboost_model.pkl
demographic_file_path=demographic_data/updated_outer_demog_sales_data.xlsx
prediction_results_path=results
plots_output_path=plots
Run the FastAPI Server:

bash
Copy code
uvicorn main:app --reload
By default, the server will run on http://127.0.0.1:8000. You should now see the server documentation available at http://127.0.0.1:8000/docs.

FastAPI Endpoint Documentation
1. /process_postcode/
Description: Fetch demographic data and amenities information for a specified postcode, and optionally run a sales prediction.
Method: GET
Parameters:
postcode (query parameter): The UK postcode for analysis (e.g., N19 5RD).
Example:
plaintext
Copy code
http://127.0.0.1:8000/process_postcode/?postcode=N19%205RD
Response:
Returns a JSON object containing demographic and amenities data for the specified postcode.
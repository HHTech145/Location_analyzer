 
# Location Analysis System

## Overview
The Location Analysis System is designed to gather, analyze, and visualize demographic and amenities data based on UK postcodes. This system leverages web scraping, data processing, and machine learning to deliver insights that can assist businesses in selecting optimal locations for new branches or expanding operations.

### Key Features
- **Postcode Data Retrieval**: Automatically fetch demographic data for a given postcode.
- **Amenities Information**: Gather nearby restaurant and pub details for a specific postcode radius.
- **Sales Prediction Model**: Use demographic data to predict sales performance based on postal code.
- **Data Visualization**: Generate HTML visualizations for analysis and presentation.
  
### System Components
1. **Web Scraper**: Fetches demographic data and amenities details from various sources based on user-specified postcodes.
2. **Prediction Model**: Utilizes a trained machine learning model to predict potential sales.
3. **Data Plotting**: Creates visual representations of demographics, amenities, and sales predictions.
4. **FastAPI Backend**: Provides an API for interacting with the system and retrieving analysis results via HTTP requests.

### Technology Stack
- **Python**: Main programming language.
- **Pandas**: For data manipulation.
- **FastAPI**: API framework for efficient and rapid development.
- **Pickle**: For saving and loading the prediction model.
- **BeautifulSoup & Selenium**: For web scraping tasks.
- **dotenv**: For environment variable management.
- **Machine Learning**: XGBoost for predictions.
  
### Folder Structure
```
📁 location-analysis-system
│
├── 📁 demographic_data            # Stores demographic data files
├── 📁 models                      # Pre-trained models for prediction
├── 📁 results                     # Results and output files
├── 📁 scripts                     # Python scripts for scraping and processing
└── 📄 main.py                     # Main FastAPI server file
└── 📄 README.md                   # Documentation
└── 📄 requirements.txt            # Dependencies
└── 📄 .env                        # Environment variables file
```

### Prerequisites
- Python 3.8 or above
- Required Python libraries (listed in `requirements.txt`)

---

# FastAPI Documentation

## Overview
The FastAPI component of the Location Analysis System provides a simple interface for interacting with the system through HTTP endpoints. Users can supply postcodes, receive demographic and amenities data, and run sales predictions via API requests.

## Setting Up the FastAPI Server
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/location-analysis-system.git
   cd location-analysis-system
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   Create a `.env` file in the root directory, specifying paths to your data and model files:
   ```
   xg_boost_model_path=models/xgboost_model.pkl
   demographic_file_path=demographic_data/updated_outer_demog_sales_data.xlsx
   prediction_results_path=results
   plots_output_path=plots
   ```

4. **Run the FastAPI Server**:
   ```bash
   uvicorn main:app --reload
   ```

   By default, the server will run on `http://127.0.0.1:8000`. You should now see the server documentation available at `http://127.0.0.1:8000/docs`.

## FastAPI Endpoint Documentation

### 1. `/process_postcode/`
- **Description**: Fetch demographic data and amenities information for a specified postcode, and optionally run a sales prediction.
- **Method**: `GET`
- **Parameters**:
  - `postcode` (query parameter): The UK postcode for analysis (e.g., `N19 5RD`).
- **Example**:
  ```plaintext
  http://127.0.0.1:8000/process_postcode/?postcode=N19%205RD
  ```
- **Response**:
  - Returns a JSON object containing demographic and amenities data for the specified postcode.
  
### 2. `/predict_sales/`
- **Description**: Use a trained model to predict potential sales for a given postcode based on demographic data.
- **Method**: `POST`
- **Request Body**:
  - JSON object with required fields:
    ```json
    {
      "postcode": "N19 5RD",
      "start_date": "01/01/2024",
      "end_date": "12/31/2024"
    }
    ```
- **Example with `curl`**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/predict_sales/" -H "Content-Type: application/json" -d "{"postcode": "N19 5RD", "start_date": "01/01/2024", "end_date": "12/31/2024"}"
  ```
- **Response**:
  - Returns predicted sales data in JSON format.

### 3. `/visualize/`
- **Description**: Generates an HTML visualization for demographics and sales predictions.
- **Method**: `POST`
- **Request Body**:
  - JSON object with required fields:
    ```json
    {
      "postcode": "N19 5RD"
    }
    ```
- **Response**:
  - Returns the path to the generated HTML file with visualizations.

---

### Future Enhancements
- **Additional Endpoints**: Plan to add endpoints for detailed amenities analysis and data storage.
- **Model Improvements**: Update the prediction model with more recent data for increased accuracy.
- **Database Integration**: Store demographic and prediction data in a database for faster retrieval.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any features you’d like to add or improve.

---

## Acknowledgments
- [FastAPI](https://fastapi.tiangolo.com/)
- [Selenium](https://selenium.dev/)
- [XGBoost](https://xgboost.readthedocs.io/)

---

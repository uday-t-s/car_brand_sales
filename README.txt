Car Brands Project
Files created in: /mnt/data/car_brands_project

Files:
- cars_data.csv : synthetic dataset (for demo)
- preprocess_data.py : script to retrain the model from cars_data.csv
- streamlit_app.py : Streamlit app to predict car brand
- dash_app.py : Dash alternative app
- car_brand_model.pkl : trained model + encoders (ready to use)
- config.toml : Streamlit theme configuration

How to run:
1) Install dependencies: pip install scikit-learn pandas joblib streamlit dash
2) Run the Streamlit app: streamlit run streamlit_app.py (from inside the project folder)
3) Or run Dash app: python dash_app.py

Note: This is a demo with synthetic data. Replace cars_data.csv with your real dataset and run preprocess_data.py to retrain the model.

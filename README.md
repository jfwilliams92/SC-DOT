# SC DOT Data - Exploration

This repo was built to explore SC DOT data. Please see <a href="https://medium.com/@jfw_4978/sc-dot-and-zillow-home-sales-1808562306e2">this</a> blog post for a detailed discussion.

## Files and Folders
- data - contains all the data necessary to run the Dash app and the Juptyer notebook data exploration
    - /shp_files - data downloaded from SC DOT GIS Website, in .dbf format
    - datadictionary.xlsx - SC DOT Data Dictionary
    - Sale_Counts_Zip.csv - Zillow home sales data by year-month and Zip Code
    - sc-zip-code-latitude-and-longitude.csv - Xref from Zip Code to lat/lon
- wrangling.py - functions to munge DOT data into a cohesive dataframe
- app.py - Dash app script
- traffic_analysis.ipynb - exploration of the SC DOT Data and the relationship with Zillow home sales data

## To run the Dash app in LOCAL mode
1. Clone or download this repository
2. Create a new environment (I use conda)
3. Sign up for a free mapbox key and store it in your environment as MAPBOX_KEY - www.mapbox.com
3. `pip install requirements.txt`
4. `python app.py`
5. Follow the link to see the app in local mode!
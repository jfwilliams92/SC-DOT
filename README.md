# SC DOT Data - Exploration

This repo was built to explore SC DOT data. Please see <a href="">this</a> blog post for a detailed discussion.

## Files and Folders
- data - contains all the data necessary to run the Dash app and the Juptyer notebook data exploration
    - /shp_files - data downloaded from SC DOT GIS Website, in .dbf format
    - datadictionary.xlsx - SC DOT Data Dictionary
    - Sale_Counts_Zip.csv - Zillow home sales data by year-month and Zip Code
    - sc-zip-code-latitude-and-longitude.csv - Xref from Zip Code to lat/lon
- wrangling.py - functions to munge DOT data into a cohesive dataframe
- app.py - Dash app script
- traffic_analysis.ipynb - exploration of the SC DOT Data and the relationship with Zillow home sales data

## To run the Dash app
1. Clone or download this repository
2. Create a new environment (I use conda)
3. `pip install requirements.txt`
4. `python app.py`
5. Follow the link to see the app in local mode!
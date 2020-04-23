# import required libraries

import pandas as pd
import numpy as np
from simpledbf import Dbf5
import os


def convert_lat_long(series, delimiter=':', precision=5):
    """Convert a series of lat or long strings into floating point representation.
    
    Args:
        series (pandas Series): a series of strings of lat/long, delimited by delimiter.
        delimiter (str): the string delimiter
        precision (int): the number of decimal places to round the result to
    Returns:
        converted (pandas Series): a series of floating points of lat/long, rounded
    
    """
    # expand=True turns the delimited series into a dataframe with multiple columns (rather than a column made of lists of splits)
    split = series.str.split(delimiter, expand=True).astype('float')
    multiplier = np.sign(split[0])
    hours = np.absolute(split[0])
    minutes = split[1] / 60.0
    seconds = split[2] / (60.0 * 60.0)
    converted = multiplier * (hours + minutes + seconds)
    
    return converted.round(precision)


def create_big_df():
    # read GIS dbf data into dataframes, one file for each year between 2009 and 2018
    shp_dfs = {}
    for root, dirs, files in os.walk("./data/shp_files"):
        for file in files:
            if file.endswith(".dbf"):
                # print(file.split('.')[0])
                dbf = Dbf5(os.path.join(root, file))
                df = dbf.to_dataframe()
                shp_dfs[file.split('.')[0]] = df

    # create a dictionary that will allow us to rename columns from key to value.
    # we won't map every column - only keep a subset
    col_mapping_dict = {
        **dict.fromkeys(['station', 'stationnu', 'stationnum'], 'station_id'),
        **dict.fromkeys(['milepoint', 'metermile', 'metermilep'], 'route_mile_point'),
        **dict.fromkeys(['latitude', 'lat'], 'latitude'),
        **dict.fromkeys(['longitude', 'long'], 'longitude'), 
        **dict.fromkeys(['aadtyr', 'year', 'factored1', 'factoreda1'], 'year'),
        **dict.fromkeys(['routelrs', 'maplrs'], 'route_identifier'),
        **dict.fromkeys(['termini', 'descriptio'], 'route_leg_descrip'),
        **dict.fromkeys(['beginmilep', 'beginmile', 'bmp'], 'route_leg_beginmile'),
        **dict.fromkeys(['endmilepo', 'endmilepoi', 'emp'], 'route_leg_endmile'),
        **dict.fromkeys(['routetype', 'rtetype', 'routetypen', 'routetype1'], 'route_type'),   # has to be a numeric column as well, some collision here
        **dict.fromkeys(['rtenum', 'rtenumb', 'routenumb', 'routenum', 'routenumbe'], 'route_number'),
        **dict.fromkeys(['county', 'countyname', 'countynam'], 'county_name'),
        **dict.fromkeys(['countyid', 'countynumb'], 'county_id'),
        **dict.fromkeys(['aadt', 'factoreda', 'count', 'factoredaa'], 'average_daily_traffic'),
        **dict.fromkeys(['id1'], 'row_number')
    }

    for df in shp_dfs.values():
        df.columns = [c.replace('_', '').lower().strip() for c in df.columns]

    # rename columns as per mapping dict
    shp_dfs_renamed = {year: df.rename(columns=col_mapping_dict) for year, df in shp_dfs.items()}

    # rename route_type column only if it's a float
    for year, df in shp_dfs_renamed.items():
        # create a df of column names and dtypes
        col_dtypes = df.dtypes.reset_index()
        col_dtypes.columns = ['col_name', 'dtype']
        # create a boolean mask with the criteria
        col_mask = (col_dtypes['col_name'] == 'route_type') & (col_dtypes['dtype'] == 'float64')
        # use integer indexing to rename the correct column 
        new_cols = np.array(df.columns)
        new_cols[col_mask] = 'route_type_number'
        df.columns = new_cols

    # still some collision - column name can mean different things in different years.
    # drop some columns that still aren't right
    shp_dfs_renamed['2009'].drop(['county_name'], axis=1, inplace=True)
    shp_dfs_renamed['2012'].drop(['county_name'], axis=1, inplace=True)
    shp_dfs_renamed['2017'].drop('county_name', axis=1, inplace=True)

    # drop columns that are duplicated
    for year, df in shp_dfs_renamed.items():
        df = df.loc[:, ~df.columns.duplicated()]
        shp_dfs_renamed[year] = df

    # drop duplicated rows in dataframes
    # some rows are only unique based on row_number (id1) and id2 fields
    for year, df in shp_dfs_renamed.items():
        df = df.drop('row_number', axis=1)
        if 'id2' in df.columns:
            df = df.drop('id2', axis=1)
        df = df.drop_duplicates()
        shp_dfs_renamed[year] = df

    # replace route type
    for year, df in shp_dfs_renamed.items():
        if 'route_type' in df.columns:
            df['route_type'] = df.route_type.str.replace('L', 'S')
        if 'route_type_number' in df.columns:
            df['route_type_number'] = df.route_type_number.replace(9, 7)

    # drop dupes by identity column
    for year, df in shp_dfs_renamed.items():
        df['average_daily_traffic'] = df. \
            groupby(['station_id', 'route_identifier', 'route_number']). \
            average_daily_traffic. \
            transform('mean')
        # drop dupes if there are any
        df = df.drop_duplicates()
        # if there are still multiple records within the group, we'll take the first record, now that adt is averaged across the group
        df = df.groupby(['station_id', 'route_identifier', 'route_number']).head(1)
        shp_dfs_renamed[year] = df

    exclude_cols = ['station_id', 'route_identifier', 'route_number', 'average_daily_traffic', 'year']
    cols = [c for c in shp_dfs_renamed['2018'].columns if c not in exclude_cols]
    
    # update all values for consistency
    update_df = shp_dfs_renamed['2018'].copy(deep=True)
    # DON'T overwrite average daily traffic values or year
    update_df = update_df.drop(['average_daily_traffic', 'year'], axis=1)
    update_df = update_df.set_index(['station_id', 'route_identifier', 'route_number'])
    cols = update_df.columns

    for year, df in shp_dfs_renamed.items():
    # make sure the year column is filled in for each one
        if year != '2018':
            for c in cols:
                if c not in df.columns:
                    df[c] = np.nan
            df = df.set_index(['station_id', 'route_identifier', 'route_number'])
            # overwrite all column values where index matches update_df index 
            df.update(update_df, overwrite=True)
            shp_dfs_renamed[year] = df.reset_index()
    
    # drop nas for average daily traffic - only in the 2018 df.
    
    shp_dfs_renamed['2018'] = shp_dfs_renamed['2018'].dropna(subset=['average_daily_traffic'])

    # convert all the lat/long series in the dfs if the dtype of the column is object (string) and has a colon
    for year, df in shp_dfs_renamed.items():
        if 'latitude' in df.columns:
            if df.latitude.dtype == 'O' and df.latitude.str.contains(':').any():
                df['latitude'] = convert_lat_long(df.latitude)
                df['longitude'] = convert_lat_long(df.longitude)
            # make sure all lat/long columns are floats
            else:
                df['latitude'] = df.latitude.astype('float')
                df['longitude'] = df.longitude.astype('float')

    # stack all the data frames together
    traffic_df = pd.concat(shp_dfs_renamed.values(), sort=True, axis=0)
    
    cols_to_keep = [
        'average_daily_traffic',
        'county_id',
        'county_name',
        'gmrotation',
        'latitude',
        'longitude', 
        'route_identifier',
        'route_number',
        'route_leg_beginmile',
        'route_leg_endmile',
        'route_mile_point',
        'route_leg_descrip',
        'route_type',
        'route_type_number',
        'station_id',
        'year'
    ]

    traffic_df = traffic_df[cols_to_keep]
    for col in cols_to_keep:
        traffic_df[col] = traffic_df.groupby(['station_id', 'route_identifier', 'route_number'])[col].bfill().ffill()

    traffic_df = traffic_df.sort_values(['station_id', 'route_identifier', 'route_number', 'year'])

    traffic_df['pct_changed'] = traffic_df. \
        groupby(['station_id', 'route_identifier', 'route_number']) \
        ['average_daily_traffic']. \
        pct_change()
    
    traffic_df['route_type'] = traffic_df.route_type.str.replace('-', '')
    traffic_df['route'] = traffic_df.route_type + '-' + traffic_df.route_number.astype('str')
    traffic_df['year'] = traffic_df.year.astype('int')
    traffic_df['county_name'] = traffic_df.county_name.str.upper()
    traffic_df.loc[traffic_df.route_number == 385, ['route_type', 'route_type_number']] = 'I', 1
    
    return traffic_df 

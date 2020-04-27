import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from plotly import graph_objs as go
import os

from wrangling import create_big_df

## read the data in and process
if not os.path.isfile('./data/bigframe.pkl'):
    create_big_df() 

traffic_df = pd.read_pickle('./data/bigframe.pkl')

# create the dash app
mapboxkey = os.environ.get('MAPBOX_KEY')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# slicer values 
route_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.route_type.unique())]
route_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

county_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.county_name.unique())]
county_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

route_name_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.route.unique())]
route_name_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})


# app layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H6('Route Type Slicer'),
                dcc.Dropdown(
                    id='route-types',
                    options=route_dict,
                    value=[],
                    multi=True,
                    placeholder='Click or search'
                )
            ], className="row"),
            html.Div([
                html.H6('County Slicer'),
                dcc.Dropdown(
                    id='county-names',
                    options=county_dict,
                    value=[],
                    multi=True,
                    placeholder='Click or search'
                )
            ], className="row"),
            html.Div([
                html.H6('Route Slicer'),
                dcc.Dropdown(
                    id='route-names',
                    options=route_name_dict,
                    value=[],
                    multi=True,
                    placeholder='Click or search'
                )
            ], className="row"),
            html.Div([
                html.H6('Values'),
                dcc.RadioItems(
                id='scale',
                options=[
                    {'label': 'AADT', 'value': 'AADT'},
                    {'label': 'Log10AADT', 'value': 'Log10AADT'},
                    {'label': 'Total Percent Change', 'value': 'Percent Change'}
                ],
                value='Log10AADT'
                )  
            ], className="row"),
            html.Div([
                html.H6('Map Background'),
                dcc.RadioItems(
                id='background',
                options=[
                    {'label': 'Light', 'value': 'light'},
                    {'label': 'Dark', 'value': 'dark'}
                ],
                value='dark'
                )  
            ], className="row")    
        ], className="three columns", style={"padding": 25}),
        html.Div(
            className="nine columns bg-grey",
            children=[
            dcc.Graph(id='scatter-geo'),
            dcc.Graph(id='year-plot')
        ])
    ], className="row")
])

# update route names with slicer values
@app.callback(
    dash.dependencies.Output("route-names", "options"),
    [dash.dependencies.Input('route-types', 'value'),
    dash.dependencies.Input("county-names", "value")]
)
def update_route_names(route_type, county_name):

    if len(route_type) < 1 or route_type==['ALL']:
        route_type = list(traffic_df.route_type.unique())

    if len(county_name) < 1 or county_name==['ALL']:
        county_name = list(traffic_df.county_name.unique())
    
    route_type_mask = traffic_df.route_type.isin(route_type)
    county_mask = traffic_df.county_name.isin(county_name)
    filter_mask = route_type_mask & county_mask
    df = traffic_df[filter_mask]
    
    route_name_dict = [{'label': i, 'value': i} for i in sorted(df.route.unique())]
    route_name_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

    return route_name_dict

# update route types with other slicer values
@app.callback(
    dash.dependencies.Output("route-types", "options"),
    [dash.dependencies.Input('route-names', 'value'),
    dash.dependencies.Input("county-names", "value")]
)
def update_route_types(route_name, county_name):

    if len(route_name) < 1 or route_name==['ALL']:
        route_name = list(traffic_df.route.unique())

    if len(county_name) < 1 or county_name==['ALL']:
        county_name = list(traffic_df.county_name.unique())
    
    route_mask = traffic_df.route.isin(route_name)
    county_mask = traffic_df.county_name.isin(county_name)
    filter_mask = route_mask & county_mask
    df = traffic_df[filter_mask]
    
    route_dict = [{'label': i, 'value': i} for i in sorted(df.route_type.unique())]
    route_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

    return route_dict

# update county names with other slicer values
@app.callback(
    dash.dependencies.Output("county-names", "options"),
    [dash.dependencies.Input('route-names', 'value'),
    dash.dependencies.Input("route-types", "value")]
)
def update_county(route_name, route_type):

    if len(route_name) < 1 or route_name==['ALL']:
        route_name = list(traffic_df.route.unique())

    if len(route_type) < 1 or route_type==['ALL']:
        route_type = list(traffic_df.route_type.unique())
    
    route_mask = traffic_df.route.isin(route_name)
    route_type_mask = traffic_df.route_type.isin(route_type)
    filter_mask = route_mask & route_type_mask
    df = traffic_df[filter_mask]
    
    county_dict = [{'label': i, 'value': i} for i in sorted(df.county_name.unique())]
    county_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

    return county_dict

# update mapbox plot
@app.callback(
    dash.dependencies.Output('scatter-geo', 'figure'),
    [dash.dependencies.Input('route-types', 'value'),
    dash.dependencies.Input('county-names', 'value'),
    dash.dependencies.Input('route-names', 'value'),
    dash.dependencies.Input('scale', 'value'),
    dash.dependencies.Input('background', 'value')]
)
def update_map(route_type, county_name, route_name, scale, map_background):
  
    if len(route_type) < 1 or route_type==['ALL']:
        route_type = list(traffic_df.route_type.unique())

    if len(county_name) < 1 or county_name==['ALL']:
        county_name = list(traffic_df.county_name.unique())

    if len(route_name) < 1 or route_name==['ALL']:
        route_name = list(traffic_df.route.unique())

    route_type_mask = traffic_df.route_type.isin(route_type)
    county_mask = traffic_df.county_name.isin(county_name)
    route_mask = traffic_df.route.isin(route_name)
    year_mask = traffic_df.year == 2018
    filter_mask = route_type_mask & county_mask & route_mask & year_mask


    plot_df = traffic_df[filter_mask]

    # map configurations
    if scale == 'AADT':
        color = plot_df['average_daily_traffic']
        title = 'Average Daily Traffic'
        size = np.log(plot_df['average_daily_traffic']) / 2
    elif scale == 'Log10AADT':
        color = np.log10(plot_df['average_daily_traffic'])
        title = 'Log10(Average Daily Traffic)'
        size = color
    elif scale == 'Percent Change':
        color = plot_df['total_pct_change']
        title = 'Total Pct Change'
        size = np.abs(color) / 100

    cmax = max(color)
    cmin = min(color)

    data = [go.Scattermapbox(
        lat = plot_df['latitude'],
        lon = plot_df['longitude'],
        mode = 'markers',
        marker = dict(
            size = size,
            opacity = 0.5, 
            color = color,
            colorbar = dict(title = title),
            colorscale = 'Jet',
            cmax = cmax,
            cmin = cmin,
            showscale = True
        ),
        text = plot_df['route_leg_descrip'] + " - AverageDailyTraffic: " + plot_df.average_daily_traffic.astype(str)
    )]
               
    layout = go.Layout(
        #autosize = True,
        hovermode = 'closest',
        showlegend = False,
        mapbox = dict(
            accesstoken = mapboxkey,
            bearing = 0,
            center = dict(lat = 33.8, lon = -81),
            pitch = 0,
            zoom = 6.6,
            style = map_background
            ),
        height=800,
        uirevision=True
        )

    return {'data': data, 'layout': layout} 

# update year over year violin plot
@app.callback(
    dash.dependencies.Output('year-plot', 'figure'),
    [dash.dependencies.Input('route-types', 'value'),
    dash.dependencies.Input('county-names', 'value'),
    dash.dependencies.Input('route-names', 'value'),
    dash.dependencies.Input('scale', 'value')]
)
def update_yearplot(route_type, county_name, route_name, scale):
  
    if len(route_type) < 1 or route_type==['ALL']:
        route_type = list(traffic_df.route_type.unique())

    if len(county_name) < 1 or county_name==['ALL']:
        county_name = list(traffic_df.county_name.unique())

    if len(route_name) < 1 or route_name==['ALL']:
        route_name = list(traffic_df.route.unique())

    route_type_mask = traffic_df.route_type.isin(route_type)
    county_mask = traffic_df.county_name.isin(county_name)
    route_mask = traffic_df.route.isin(route_name)
    filter_mask = route_type_mask & county_mask & route_mask

    plot_df = traffic_df[filter_mask]

    # map configurations
    if scale == 'AADT':
        vals = plot_df['average_daily_traffic']
        title = 'Average Daily Traffic'
    elif scale == 'Log10AADT':
        vals = np.log10(plot_df['average_daily_traffic'])
        title = 'Log10(Average Daily Traffic)'
    elif scale == 'Percent Change':
        vals = plot_df['total_pct_change']
        title = 'Total Pct Change'

    data = [go.Violin(y=vals, x=plot_df["year"], box_visible=True, meanline_visible=True, opacity=0.6)]
    layout = go.Layout(title=title)

    return {'data': data, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
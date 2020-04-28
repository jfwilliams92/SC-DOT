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
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

# slicer values 
route_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.route_type.unique())]
route_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

county_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.county_name.unique())]
county_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})

route_name_dict = [{'label': i, 'value': i} for i in sorted(traffic_df.route.unique())]
route_name_dict.insert(0, {'label': 'ALL', 'value': 'ALL'})


# app layout
app.layout = html.Div(
    className="row",
    children=[
        html.Div(
            className="slicer-div three columns",
            children=[
                html.H2("SC DOT"),
                html.H2("Average Daily Traffic in South Carolina"),
                html.Div(
                    className="dropdown-div row",
                    children=[
                        html.P('Route Type Slicer'),
                        dcc.Dropdown(
                            id='route-types',
                            options=route_dict,
                            value=[],
                            multi=True,
                            placeholder='Click or search'
                        )
                    ]
                ),
                html.Div(
                    className="dropdown-div row",
                    children=[
                        html.P('County Slicer'),
                        dcc.Dropdown(
                            id='county-names',
                            options=county_dict,
                            value=[],
                            multi=True,
                            placeholder='Click or search'
                        )
                    ]
                ),
                html.Div(
                    className="dropdown-div row",
                    children=[
                        html.P('Route Slicer'),
                        dcc.Dropdown(
                            id='route-names',
                            options=route_name_dict,
                            value=[],
                            multi=True,
                            placeholder='Click or search'
                        )
                    ]
                ),
                html.Div(
                    className="radio-div row",
                    children=[
                        html.P('Values'),
                        dcc.RadioItems(
                        id='scale',
                        options=[
                            {'label': 'AADT', 'value': 'AADT'},
                            {'label': 'Log10AADT', 'value': 'Log10AADT'},
                            {'label': 'Total Percent Change', 'value': 'Percent Change'}
                        ],
                        value='Log10AADT'
                        )  
                    ]
                ),
                html.Div(
                    className="radio-div row",
                    children=[
                        html.P('Map Background'),
                        dcc.RadioItems(
                        id='background',
                        options=[
                            {'label': 'Light', 'value': 'light'},
                            {'label': 'Dark', 'value': 'dark'}
                        ],
                        value='dark'
                        )  
                    ]
                )    
            ]
        ),
        html.Div(
            className="charts-div nine columns bg-grey",
            children=[
                dcc.Graph(id='scatter-geo'),
                dcc.Graph(id='year-plot')
            ]
        )
    ]
)

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
        text = 'Route: ' + plot_df['route'] +\
            '<br>Route Leg: ' + plot_df['route_leg_descrip'] +\
            "<br>AverageDailyTraffic: " + plot_df.average_daily_traffic.astype(str)
    )]
               
    layout = go.Layout(
        #autosize = True,
        hovermode = 'closest',
        font=dict(color="white"),
        showlegend = False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        margin=go.layout.Margin(t=0, b=0, l=0, r=0),
        mapbox = dict(
            accesstoken = mapboxkey,
            bearing = 0,
            center = dict(lat = 33.8, lon = -81),
            pitch = 0,
            zoom = 6.6,
            style = map_background
            ),
        height=575,
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
        medians = plot_df.groupby('year').average_daily_traffic.median().reset_index()
        title = 'Average Daily Traffic'
    elif scale == 'Log10AADT':
        vals = np.log10(plot_df['average_daily_traffic'])
        medians = plot_df.groupby('year').log10_adt.median().reset_index()
        title = 'Log10(Average Daily Traffic)'
    elif scale == 'Percent Change':
        vals = plot_df['total_pct_change']
        medians = plot_df.groupby('year').total_pct_change.median().reset_index()
        title = 'Total Pct Change'

    medians.columns=['year', 'vals']

    data = [
        go.Violin(
            y=vals, 
            x=plot_df["year"], 
            box_visible=True, 
            meanline_visible=True, 
            opacity=0.6,
            line_color='mediumpurple'
        ),
        go.Scatter(
            x=medians.year,
            y=medians.vals,
            line_color='lightblue'
        )
    ]
    layout = go.Layout(
        title=title,
        showlegend=False,
        font=dict(color="white"),
        margin=go.layout.Margin(t=32, b=25, l=30, r=5),
        plot_bgcolor="#323130",
        paper_bgcolor="#323130"
    )

    return {'data': data, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)
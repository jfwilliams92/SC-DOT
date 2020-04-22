import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from plotly import graph_objs as go
import os

from wrangling import create_big_df

## read the data in and process
traffic_df = create_big_df()
traffic_df['log_adt'] = np.log(traffic_df.average_daily_traffic)
traffic_df['log10_adt'] = np.log10(traffic_df.average_daily_traffic)

# create the dash app
mapboxkey = os.environ.get('MAPBOX_KEY')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# slicer values 
route_dict = [{'label': i, 'value': i} for i in traffic_df.route_type.unique()]
route_dict.insert(0, {'label': 'All', 'value': ''})

county_dict = [{'label': i, 'value': i} for i in traffic_df.county_name.unique()]
county_dict.insert(0, {'label': 'All', 'value': ''})


# app layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H4('Route Type Slicer'),
            dcc.Dropdown(
                id='route-types',
                options=route_dict,
                value='',
                multi=True
            )
        ], className="six columns"),
        html.Div([
            html.H4('County Slicer'),
            dcc.Dropdown(
                id='county-names',
                options=county_dict,
                value='',
                multi=True,
            )
        ], className="six columns")
    ], className="row"
    ),
    html.Div([
        dcc.Slider(
            id='crossfilter-year--slider',
            min=traffic_df['year'].min(),
            max=traffic_df['year'].max(),
            value=traffic_df['year'].max(),
            marks={int(year): str(int(year)) for year in traffic_df['year'].unique()},
            step=1.0,
        ),
    ], style={'padding': 50}),
    html.Div([dcc.Graph( id='scatter-geo')])
])

@app.callback(
    dash.dependencies.Output('scatter-geo', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value'),
    dash.dependencies.Input('route-types', 'value'),
    dash.dependencies.Input('county-names', 'value')]
)
def update_graph(year_value, route_type, county_name):
    plot_df = traffic_df[traffic_df.year == year_value]

    if (not route_type) or (route_type == ''):
        route_type = list(traffic_df.route_type.unique())

    if (not county_name) or (county_name == ''):
        county_name = list(traffic_df.county_name.unique())

    plot_df = plot_df[(plot_df.route_type.isin(route_type)) & (plot_df.county_name.isin(county_name))]

    data = [go.Scattermapbox(
        lat = plot_df['latitude'],
        lon = plot_df['longitude'],
        mode = 'markers',
        marker = dict(
            size = np.log10(plot_df['average_daily_traffic']),
            opacity = 0.5, 
            color = np.log10(plot_df['average_daily_traffic']),
            colorbar = dict(title = 'Log(Average Daily Traffic)'),
            colorscale = 'Jet',
            cmax = max(np.log10(plot_df['average_daily_traffic'])),
            cmin = min(np.log10(plot_df['average_daily_traffic'])),
            showscale = True
        ),
        text = plot_df['route_leg_descrip'] + " - AverageDailyTraffic: " + plot_df.average_daily_traffic.astype(str)
    )]
    
                      
    layout = go.Layout(
        title = 'Average Daily Traffic in SC',
        #autosize = True,
        hovermode = 'closest',
        showlegend = False,
        mapbox = dict(
            accesstoken = mapboxkey,
            bearing = 0,
            center = dict(lat = 34, lon = -81),
            pitch = 0,
            zoom = 6.5,
            style = 'dark'
            ),
        height=850,
        uirevision=True
        )

    return {'data': data, 'layout': layout} 

if __name__ == '__main__':
    app.run_server(debug=True)
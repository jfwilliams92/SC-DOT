import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from plotly import graph_objs as go
import os

from wrangling import create_big_df

traffic_df = create_big_df()
traffic_df['log_adt'] = np.log(traffic_df.average_daily_traffic)
traffic_df['log10_adt'] = np.log10(traffic_df.average_daily_traffic)
mapboxkey = os.environ.get('MAPBOX_KEY')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

# available_indicators = df['Indicator Name'].unique()
route_dict = [{'label': i, 'value': i} for i in traffic_df.route_type.unique()]
route_dict.insert(0, {'label': 'All', 'value': 1})


app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='route-types',
            options=route_dict,
            value=1,
            multi=True
        )
    ]),

    html.Div([
        dcc.Graph(
            id='scatter-geo',
            hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'width': '99%', 'display': 'inline-block', 'padding': '0 20'}),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=traffic_df['year'].min(),
        max=traffic_df['year'].max(),
        value=traffic_df['year'].max(),
        marks={str(year): str(year) for year in traffic_df['year'].unique()},
        step=None
    ), style={'width': '99%', 'padding': '0px 20px 20px 20px'})
])

@app.callback(
    dash.dependencies.Output('scatter-geo', 'figure'),
    [dash.dependencies.Input('crossfilter-year--slider', 'value'),
    dash.dependencies.Input('route-types', 'value')]
)
def update_graph(year_value, route_type):
    plot_df = traffic_df[traffic_df.year == year_value]

    if route_type != 1:
        plot_df = plot_df[plot_df.route_type.isin(route_type)]

    lat = plot_df['latitude']
    lon = plot_df['longitude']

    data = [go.Scattermapbox(
        lat = lat,
        lon = lon,
        mode = 'markers',
        marker = dict(
            size = np.log(plot_df['average_daily_traffic']) / 2,
            opacity = 0.5, 
            color = plot_df['log10_adt'],
            colorbar = dict(title = 'Log(Average Daily Traffic)'),
            colorscale = 'Jet',
            cmax = max(traffic_df.log10_adt),
            cmin = min(traffic_df.log10_adt),
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
            # center = dict(lat = 34, lon = -80),
            pitch = 0,
            # zoom = 9.5,
            style = 'dark'
            ),
        height=900,
        uirevision=True
        )

    return {'data': data, 'layout': layout} 


if __name__ == '__main__':
    app.run_server(debug=True)
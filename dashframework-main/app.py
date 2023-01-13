from jbi100_app.main import app
#from jbi100_app.views.menu import make_menu_layout
#from jbi100_app.views.scatterplot import Scatterplot

from dash import html, Input, Output
from dash import dcc, State

import plotly.express as px
import pandas as pd

from dash.dependencies import Input, Output, State
#import datetime as dt


if __name__ == '__main__':

    # Our data bases (I am using "processed" files because I made some small changes to those databases, I can send them to you if you want)
    #airbnbDb = pd.read_csv('C:/Users/aliah/Documents/GitHub/Visualization_Project_36/dashframework-main/airbnb_open_data_processed.csv', low_memory=False)
    #crimeDb = pd.read_csv('C:/Users/aliah/Documents/GitHub/Visualization_Project_36/dashframework-main/NYPD_Complaint_processed.csv', low_memory=False)
    airbnbDb = pd.read_csv('./airbnb_10k_processed.csv', low_memory=False)
    crimeDb = pd.read_csv('./NYPD_Complaint_processed.csv', low_memory=False)
    fakeDb = pd.read_csv('./fakeCrimeData.csv', low_memory=False)
    
    # Processing of dataframes
    airbnbDb['neighbourhood group'] = airbnbDb['neighbourhood group'].fillna('Not Specified')
    airbnbDb['host_identity_verified'] = airbnbDb['host_identity_verified'].fillna('Not Specified')
    airbnbDb['service fee'] = airbnbDb['service fee'].fillna(0)
    airbnbDb['availability 365'] = airbnbDb['availability 365'].fillna(365)
    airbnbDb['host_identity_verified'] = airbnbDb['host_identity_verified'].fillna('unconfirmed')
    airbnbDb['Count'] = (365 - airbnbDb['availability 365'])
    airbnbDb['Costs'] = airbnbDb.apply(lambda row: row['service fee']*row['Count'],axis=1)
    airbnbDb['Revenue'] = airbnbDb.apply(lambda row: ((row['price'] + row['service fee'])*row['Count']),axis=1)
    airbnbDb['Profit'] = airbnbDb['Revenue'] - airbnbDb['Costs']
    airbnbDb.loc[airbnbDb['neighbourhood group'] == 'brookln', 'neighbourhood group'] = 'Brooklyn'
    airbnbDb.loc[airbnbDb['neighbourhood group'] == 'manhatan', 'neighbourhood group'] = 'Manhattan'
    crimeDb['BORO_NM'] = crimeDb['BORO_NM'].fillna("Not Specified")
    crimeDb.loc[crimeDb['BORO_NM'] == '(null)', 'BORO_NM'] = 'MANHATTAN'     
        
    app.layout = html.Div(
        [   html.Div(id = 'Crime'),

            html.Div(
                id = 'original',
                children = 
            [   
                # Filtering Map
                html.Div(
                [
                    html.H1(children='Filter Properties', style = {"font-size": "20px"}),

                    dcc.Dropdown(id='dropdown_groups', options=[
                   {'label': i, 'value': i} for i in airbnbDb['neighbourhood group'].unique()
                    ], multi=False, placeholder='Choose Area', style = {"width": "75%"}),

                    html.Br(),

                    dcc.Dropdown(id='dropdown_verification', options=[
                    {'label': i, 'value': i} for i in airbnbDb['host_identity_verified'].unique()
                    ], multi=False, placeholder='Host Identity', style = {"width": "75%"}),
                    html.Br(), 

                    html.H1(children = 'Display Crime Analytics',style = {"font-size": "20px"}),
                    html.Button(
                        'Press',
                        id = 'reset',
                        n_clicks = 0,
                        style = {"width": "55%", "text-align": "left"}
                    ),
                    
                    html.Br(),
                ], style = {"width": "17%", "display": "inline-block"}), 
                # Map
                html.Div(
                [
                    html.H1(children='Location of Properties', style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "Map"),

                    html.Br(),

                    html.H1(children='Properties based on profit', style = {"font-size": "20px", "text-align": "center"}),

                    dcc.Graph(id = "Map_2"),
                    html.Br(),
    
                ], style= {"width": "33%", "display": "inline-block", "verticalAlign": "top"}), 
                #Visualizations
                html.Div(
                [
                    html.H1(children= "Visualizations", style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "Violin"),
                    html.P("Profit Baseline", style = {"text-align": "left"}),
                    dcc.Slider( id='slider-position', min=airbnbDb['Profit'].min(), max=airbnbDb['Profit'].max(), value=airbnbDb['Profit'].min(), step=None),
                    html.Div(id = 'x'),
                    dcc.Graph(id = "PcpGraph"),
                    dcc.Graph(id = "BubblePlot"),
                ], style= {"width": "40%", "display": "inline-block", "verticalAlign": "top", "text-align": "center", "float": "right"}
                ),
            ])
        ])
    
    #Map of properties
    @app.callback(
        Output("Map", "figure"),
        Input('dropdown_groups', 'value'), 
        Input('dropdown_verification', 'value'),
    )
    def output_figure(area, identity):
        if (area is None) and (identity is None):
            dff = airbnbDb
        elif not(area is None) and (identity is None):
            dff = airbnbDb[airbnbDb['neighbourhood group'].str.contains(''.join(area))]
        elif (area is None) and not(identity is None):
            dff = airbnbDb[airbnbDb['host_identity_verified'].str.contains(''.join(identity))]
        else:
            dff = airbnbDb[airbnbDb['neighbourhood group'].str.contains(''.join(area)) & airbnbDb['host_identity_verified'].str.contains(''.join(identity))]
        fig = px.scatter_mapbox(data_frame = dff, color = "host_identity_verified",color_discrete_sequence= ["blue", "green", "orange"],lat = "lat", lon = "long", hover_name = dff['NAME'], hover_data={'room type': True,'review rate number': True, 'price': True, 'service fee': True,  'availability 365': True,
           'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")
        fig.update_layout(legend = dict(title = "Host Identity"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
        return fig

    #Crime heatmap
    @app.callback(
        Output("CrimeMap", "figure"),
        Input('dropdown_crimearea', 'value')
    )
    def output_figure (area):
        if (area is None):
            dff = crimeDb
        else:
            dff = crimeDb[crimeDb['BORO_NM'].str.contains(''.join(area))]
        fig = px.density_mapbox(dff, lat='Latitude', lon='Longitude', radius=1,
                        center=dict(lat=40.7, lon=-73.9), zoom=8, hover_data= {'OFNS_DESC': True, 'PD_DESC': True},
                        mapbox_style="open-street-map", title='Crime heatmap')
        return fig

    #Violin figure
    @app.callback(
        Output("Violin", "figure"),
        Input("slider-position", "value")
    )
    def output_figure(profit):
        fig = px.violin(airbnbDb, y="Profit", x="room type", color="room type", box=True, points="all", title='Profitalibility analysis')
        fig.add_hline(y = profit, line_width = 3, line_dash = "dash", line_color = "black")
        fig.update_layout(legend = dict(title = "Room Type"))
        fig.update_traces(opacity=0.5, selector=dict(type='violin'))
        
        return fig

    #Second map (to be removed)
    @app.callback(
        Output("Map_2", "figure"),
        Input("slider-position", "value")
    )
    def output_figure(profit):
        dff = airbnbDb[airbnbDb['Profit'] >= profit]
        fig =  px.scatter_mapbox(data_frame = dff, lat = "lat", lon = "long", color = "room type",hover_name = dff['NAME'], hover_data={'room type': True, 'price': True, 'service fee': True,  'availability 365': True,
                'review rate number': True,'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")  
        fig.update_layout(legend = dict(title = "Room Type", itemclick = "toggleothers"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
        return fig

    #Pcp graph
    @app.callback(
        Output("PcpGraph", "figure"),
        Input('dropdown_groups', 'value')
    )
    def output_figure(value):
        dff = airbnbDb[airbnbDb['price'] >= value]
        coordinatesPlot = px.parallel_coordinates(airbnbDb, color="price",
                              dimensions=['lat', 'Construction year', 'service fee', "room type",
                                          'minimum nights', 'number of reviews', 'review rate number', 'availability 365'],
                              color_continuous_scale='agsunset',
                              color_continuous_midpoint=700)
        return coordinatesPlot


    #Bubble plot
    @app.callback(
        Output("BubblePlot", "figure"),
        Input('dropdown_groups', 'value')
    )
    def output_figure(value):
        dff = airbnbDb[airbnbDb['price'] >= value]
        bubblePlot = px.scatter(airbnbDb, x="last review", y="number of reviews",
	         size="reviews per month", color="review rate number", hover_name="neighbourhood", log_x=False, size_max=20, range_x=['2013-01-01','2019-12-31'])
        return bubblePlot
    
    #Crime bar chart
    @app.callback(
        Output("CrimeBarchart", "figure"),
        Input('dropdown_crimearea', 'value')
    )
    def output_figure(value):
        dff = airbnbDb[airbnbDb['price'] >= value]
 
        crimeBarchart = px.bar(fakeDb, x="neighbourhood", y=["felony", "violation", "misdemeanor"], title="Wide-Form Input")
        return crimeBarchart

    #Display Crime Analytics
    @app.callback(
        Output('Crime', 'children'),
        Input('reset', 'n_clicks'),
        State('Crime', 'children'),
        State('original', 'children')
    )
    def display(n_clicks, Crime, Original):
        if n_clicks >= 1:
            Crime = [
                            html.Div(
                        [
                            #Filtering
                            html.Div(
                                [
                                    html.H1(children= "Crime Heatmap", style = {"font-size": "20px", "text-align": "left"}),
                    
                                    dcc.Dropdown(id='dropdown_crimearea', options=[
                                    {'label': i, 'value': i} for i in crimeDb['BORO_NM'].unique()
                                    ], multi=False, placeholder='Area', style = {"width": "75%"}),

                                    html.H1(children = 'Hide Crime Analytics',style = {"font-size": "20px"}),

                                    html.Button(
                                    'Press',
                                    id = 'delete',
                                    n_clicks = 0,
                                    style = {"width": "55%", "text-align": "left"}
                                    ),
                                ], style = {"width": "17%", "display": "inline-block", "verticalAlign": "top"}
                            ),
                            
                            #Crime Heatmap
                            html.Div(
                                [
                                    html.Div(children = [dcc.Graph(id = "CrimeMap")]),
                                ], style = {"width": "35%", "display": "inline-block", "verticalAlign": "top"}
                            ),

                            #Visualizations
                            html.Div(
                                [
                                    html.H1(children = 'Crime Distribution', style = {"font-size": "20px", "text-align": "center"}),
                                    dcc.Graph(id = "CrimeBarchart"),
                                ], style = {"width": "40%", "display": "inline-block", "verticalAlign": "top", "float": "right"}
                            )
                        ])  
                       ]
            Original.clear()
            return Crime

    #Hide crime analytics
    @app.callback(
        Output('original', 'children'),
        Input('delete', 'n_clicks'),
        State('original', 'children'),
        State('Crime', 'children')
    )
    def hide(n_clicks, Original, Crime):
        if n_clicks > 0:
            Original = [   
                # Filtering Map
                html.Div(
                [
                    html.H1(children='Filter Properties', style = {"font-size": "20px"}),

                    dcc.Dropdown(id='dropdown_groups', options=[
                    {'label': i, 'value': i} for i in airbnbDb['neighbourhood group'].unique()
                    ], multi=False, placeholder='Choose Area', style = {"width": "75%"}),

                    html.Br(),

                    dcc.Dropdown(id='dropdown_verification', options=[
                    {'label': i, 'value': i} for i in airbnbDb['host_identity_verified'].unique()
                    ], multi=False, placeholder='Host Identity', style = {"width": "75%"}),


                    html.Br(), 

                    html.H1(children = 'Display Crime Analytics',style = {"font-size": "20px"}),
                    html.Button(
                        'Press',
                        id = 'reset',
                        n_clicks = 0,
                        style = {"width": "50%", "text-align": "left"}
                    ), 
                    
                    html.Br(),
                ], style = {"width": "17%", "display": "inline-block"}), 
                # Map
                html.Div(
                [
                    html.H1(children='Location of Properties', style = {"font-size": "20px", "text-align": "center"}),

                    dcc.Graph(id = "Map"),

                    html.Br(),

                    html.H1(children='Properties based on profit', style = {"font-size": "20px", "text-align": "center"}),

                    dcc.Graph(id = "Map_2"),
                    html.Br(),
    
                ], style= {"width": "33%", "display": "inline-block", "verticalAlign": "top"}), 
                #Visualizations
                html.Div(
                [
                    html.H1(children= "Visualizations", style = {"font-size": "20px", "text-align": "center"}),
                    #dcc.Graph(id = "CrimeMap"),
                    dcc.Graph(id = "Violin"),
                    
                    html.P("Profit Baseline", style = {"text-align": "left"}),
                    dcc.Slider( id='slider-position', min=airbnbDb['price'].min(), max=airbnbDb['price'].max(), value=airbnbDb['price'].min(), step=None),
                    dcc.Graph(id = "PcpGraph"),
                    dcc.Graph(id = "BubblePlot"),
                    html.Div(id = 'x')
                ], style= {"width": "40%", "display": "inline-block", "verticalAlign": "top", "text-align": "center", "float": "right"}
                ),
            ]
            Crime.clear()
            return Original

app.run_server(debug=False, dev_tools_ui=False)
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
    airbnbDb = pd.read_csv('C:/Users/aliah/Documents/GitHub/Visualization_Project_36/dashframework-main/airbnb_open_data_processed.csv', low_memory=False)
    crimeDb = pd.read_csv('C:/Users/aliah/Documents/GitHub/Visualization_Project_36/dashframework-main/NYPD_Complaint_processed.csv', low_memory=False)
    
    # Processing of dataframes
    airbnbDb['neighbourhood group'] = airbnbDb['neighbourhood group'].fillna('Not Specified')
    airbnbDb['host_identity_verified'] = airbnbDb['host_identity_verified'].fillna('Not Specified')
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


    # coordinatesPlot = px.parallel_coordinates(airbnbDb, color="lat",
    #                           dimensions=['Construction year', 'price', 'service fee',
    #                                       'minimum nights', 'number of reviews', 'reviews per month', 'availability 365'],
    #                           color_continuous_scale='balance',
    #                           color_continuous_midpoint=40.80)

    
    
    # reviewGraph = dcc.Graph(figure=reviewScatterplot)
    # mapGraph = dcc.Graph(figure=mapScatter)
    # verifiedGraph = dcc.Graph(figure=verifiedPiechart)
    # violinGraph = dcc.Graph(figure=violinPlot)
    # crimeGraph = dcc.Graph(figure=crimeHeatmap)
    # coordinatesGraph = dcc.Graph(figure=coordinatesPlot)
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

        #         # Right column
        #         html.Div(
        #             id="right-column",
        #             className="nine columns",
        #             children=[
        #                 reviewGraph,
        #                 mapGraph,
        #                 verifiedGraph,
        #                 # Here there are not included because they make the whole app go very slow
        #                 #violinGraph,
        #                 #crimeHeatmap,
        #                 coordinatesGraph
        #             ],
        #         ),
        #     ],
        # )
    # Next task is to define the interactions
    
    # @app.callback(
    #     Output(reviewGraph, "figure"), [
    #     Input("select-color-scatter-1", "value"),
    #     Input(mapGraph, 'selectedData')
    # ])
    # def update_scatter_1(selected_color):
    #     return dcc.Graph(figure=reviewScatterplot.update_traces(marker=dict(color=selected_color)))
        #dcc.Graph(figure=px.scatter(airbnbDb, x="review rate number", y="number of reviews", title='Review scatterplot', color=selected_color))

    # @app.callback(
    #     Output(scatterplot1.html_id, "figure"), [
    #     Input("select-color-scatter-1", "value"),
    #     Input(scatterplot2.html_id, 'selectedData')
    # ])
    # def update_scatter_1(selected_color, selected_data):
    #     return scatterplot1.update(selected_color, selected_data)

    # @app.callback(
    #     Output(scatterplot2.html_id, "figure"), [
    #     Input("select-color-scatter-2", "value"),
    #     Input(scatterplot1.html_id, 'selectedData')
    # ])
    # def update_scatter_2(selected_color, selected_data):
    #     return scatterplot2.update(selected_color, selected_data)
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
                    dcc.Slider( id='slider-position', min=airbnbDb['price'].min(), max=airbnbDb['price'].max(), value=airbnbDb['price'].min(), step=None),
                    html.Div(id = 'x')
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
            fig = px.scatter_mapbox(data_frame = airbnbDb, color = "host_identity_verified", color_discrete_sequence= ["blue", "green", "orange"], lat = "lat", lon = "long", hover_name = airbnbDb['NAME'], hover_data={'room type': True,'review rate number': True, 'price': True, 'service fee': True, 'availability 365': True,  
                'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")
            fig.update_layout(legend = dict(title = "Host Identity"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
            return fig
        elif not(area is None) and (identity is None):
            dff = airbnbDb[airbnbDb['neighbourhood group'].str.contains(''.join(area))]
            fig = px.scatter_mapbox(data_frame = dff, color = "host_identity_verified",color_discrete_sequence= ["blue", "green", "orange"],lat = "lat", lon = "long", hover_name = dff['NAME'], hover_data={'room type': True,'review rate number': True, 'price': True, 'service fee': True,  'availability 365': True,
                'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")
            fig.update_layout(legend = dict(title = "Host Identity"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
            return fig
        elif (area is None) and not(identity is None):
            dff = airbnbDb[airbnbDb['host_identity_verified'].str.contains(''.join(identity))]
            fig = px.scatter_mapbox(data_frame = dff, color = "host_identity_verified",color_discrete_sequence= ["blue", "green", "orange"],lat = "lat", lon = "long", hover_name = dff['NAME'], hover_data={'room type': True,'review rate number': True, 'price': True, 'service fee': True,  'availability 365': True,
                'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")
            fig.update_layout(legend = dict(title = "Host Identity"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
            return fig
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
            fig = px.density_mapbox(crimeDb, lat='Latitude', lon='Longitude', radius=1,
                        center=dict(lat=40.7, lon=-73.9), zoom=8, hover_data= {'OFNS_DESC': True, 'PD_DESC': True},
                        mapbox_style="open-street-map", title='Crime heatmap')
            return fig
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
        fig = px.violin(airbnbDb, y="price", x="room type", color="room type", box=True, points="all", title='Profitalibility analysis')
        fig.add_hline(y = profit, line_width = 3, line_dash = "dash", line_color = "black")
        fig.update_layout(legend = dict(title = "Room Type"))
        return fig

    #Second map (to be removed)
    @app.callback(
        Output("Map_2", "figure"),
        Input("slider-position", "value")
    )
    def output_figure(profit):
        dff = airbnbDb[airbnbDb['price'] >= profit]
        fig =  px.scatter_mapbox(data_frame = dff, lat = "lat", lon = "long", color = "room type",hover_name = dff['NAME'], hover_data={'room type': True, 'price': True, 'service fee': True,  'availability 365': True,
                'review rate number': True,'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="open-street-map")  
        fig.update_layout(legend = dict(title = "Room Type", itemclick = "toggleothers"), margin = {"r": 0, "l": 0, "t": 0,"b": 0})
        return fig

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
                                    html.H1(children = 'Crime Distribution', style = {"font-size": "20px", "text-align": "center"})
                                ], style = {"width": "40%", "display": "inline-block", "verticalAlign": "top"}
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
                    html.Div(id = 'x')
                ], style= {"width": "40%", "display": "inline-block", "verticalAlign": "top", "text-align": "center", "float": "right"}
                ),
            ]
            Crime.clear()
            return Original

app.run_server(debug=False, dev_tools_ui=False)
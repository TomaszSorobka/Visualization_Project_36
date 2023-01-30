import numpy as np
from jbi100_app.main import app
#from jbi100_app.views.menu import make_menu_layout
#from jbi100_app.views.scatterplot import Scatterplot
import plotly.graph_objects as go

from dash import html, Input, Output
from dash import dcc, State

import plotly.express as px
import pandas as pd

from dash.dependencies import Input, Output, State
#import datetime as dt


if __name__ == '__main__':

    airbnbDb = pd.read_csv("./airbnb_open_data.csv", low_memory=True)
    crimeDb = pd.read_csv('./NYPD_Complaint_processed.csv', low_memory=False)


    
    displayedPlots = False
    previousValue = None
    filteringArray = [[None, None], [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]
    cleanArray = [[None, None], [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]
    chosenDimensionsPcp = ['Profit', 'Construction year', 'service fee',
                                            'number of reviews', 'review rate number', 'availability 365']

    # Processing of dataframes
    airbnbDb = airbnbDb.dropna()
    airbnbDb.drop(airbnbDb[airbnbDb['availability 365'] > 365].index, inplace= True)
    print(len(airbnbDb))
    # airbnbDb['neighbourhood group'] = airbnbDb['neighbourhood group'].fillna('Not Specified')
    # airbnbDb['host_identity_verified'] = airbnbDb['host_identity_verified'].fillna('Not Specified')
    # airbnbDb['service fee'] = airbnbDb['service fee'].fillna(0)
    # airbnbDb['availability 365'] = airbnbDb['availability 365'].fillna(365)
    # airbnbDb['reviews per month'] = airbnbDb['reviews per month'].fillna(0)
    # airbnbDb['host_identity_verified'] = airbnbDb['host_identity_verified'].fillna('unconfirmed')
    # airbnbDb['NAME'] = airbnbDb['NAME'].fillna('No Name')
    airbnbDb['last review'] = pd.to_datetime(airbnbDb["last review"])
    airbnbDb['last review'] = pd.to_datetime(airbnbDb["last review"].dt.strftime('%Y-%m-%d'))
    airbnbDb['Count'] = (365 - airbnbDb['availability 365'])
    airbnbDb['Costs'] = airbnbDb.apply(lambda row: row['service fee']*row['Count'],axis=1)
    airbnbDb['Revenue'] = airbnbDb.apply(lambda row: ((row['price'] + row['service fee'])*row['Count']),axis=1)
    airbnbDb['Profit'] = airbnbDb['Revenue'] - airbnbDb['Costs']
    airbnbDb.loc[airbnbDb['neighbourhood group'] == 'brookln', 'neighbourhood group'] = 'Brooklyn'
    airbnbDb.loc[airbnbDb['neighbourhood group'] == 'manhatan', 'neighbourhood group'] = 'Manhattan'
    crimeDb['BORO_NM'] = crimeDb['BORO_NM'].fillna("Not Specified")
    crimeDb.loc[crimeDb['BORO_NM'] == '(null)', 'BORO_NM'] = 'MANHATTAN'  
    tempDb = airbnbDb
    filteredDb = airbnbDb 
        
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
                    ], multi=False, placeholder='Choose Area', style = {"width": "100%"}),

                    html.Br(),

                    dcc.Dropdown(id='dropdown_verification', options=[
                    {'label': i, 'value': i} for i in airbnbDb['host_identity_verified'].unique()
                    ], multi=False, placeholder='Host Identity', style = {"width": "100%"}),
                    html.Br(), 

                    html.H1(children = 'Display Crime Analytics',style = {"font-size": "20px"}),
                    html.Button(
                        'Press',
                        id = 'reset',
                        n_clicks = 0,
                        style = {"width": "90%", "text-align": "left"}
                    ),

                    html.Br(),
                    html.H1(children = 'Reset filtering tool',style = {"font-size": "20px"}),
                    
                    html.A(html.Button('Reset', n_clicks = 0, style = {"width": "90%", "text-align": "left"}),href='/'),
                    html.Br(),
                    html.H1(children = 'Reset Visualizations',style = {"font-size": "20px"}),
                    html.Button(
                        'Reset',
                        id = 'undo',
                        n_clicks = 0,
                        style = {"width": "90%", "text-align": "left"}
                    ),
                ], style = {"width": "10%", "display": "inline-block"}), 
                html.Div(style={"width": "1%", "display": "inline-block"}),
                # Map
                html.Div(
                [
                    html.H1(children='Filtering tool', style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "PcpGraph"),
                    

                    html.Br(),

                    
                    dcc.Graph(id = "Violin"),
                    #html.P("Profit Baseline", style = {"text-align": "left"}),
                    #dcc.Slider( id='slider-position', min=airbnbDb['Profit'].min(), max=airbnbDb['Profit'].max(), value=airbnbDb['Profit'].min(), step=None),
                    html.Div(id = 'x'),
                    #dcc.Graph(id = "Map_2"),
                    html.Br(),
    
                ], style= {"width": "40%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div(style={"width": "1%", "display": "inline-block"}), 
                #Visualizations
                html.Div(
                [
                    html.H1(children= "Location of Properties", style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "Map"),
                    html.Br(),
                    dcc.Graph(id = "BubblePlot"),
                    
                ], style= {"width": "48%", "display": "inline-block", "verticalAlign": "top", "text-align": "center"}
                ),
            ])
        ])
    

    #Crime heatmap
    @app.callback(
        Output("CrimeMap", "figure"),
        Input('CrimeBarchart', 'selectedData')
    )
    def output_figure (value):
        if (value is None):
            dff = crimeDb
        else:
            filtList = []
            areaList = []
            for i in range(len(value['points'])):
                curveNumber = value['points'][i]['curveNumber']
                group = value['points'][i]['x']
                areaList.append(group)
                if (curveNumber == 0):
                    crime = "FELONY"
                elif (curveNumber == 1):
                    crime = "MISDEMEANOR"
                else:
                    crime = "VIOLATION"
                filtList.append(crime)
            dff = crimeDb[crimeDb['LAW_CAT_CD'].isin(filtList) & crimeDb['BORO_NM'].isin(areaList)]
        
        fig = px.density_mapbox(dff, lat='Latitude', lon='Longitude', radius=4,
                        center=dict(lat=40.7, lon=-73.9), zoom=8.7, hover_data= {'OFNS_DESC': True, 'PD_DESC': True},
                        mapbox_style="carto-positron", opacity = 0.9, title='Crime heatmap')
        fig.update_layout(title = "Crime Heatmap", dragmode='lasso')
        return fig

    #Crime bar chart
    @app.callback(
        Output("CrimeBarchart", "figure"),
        Input('delete', 'n_clicks')
    )
    def output_figure(value):
        df_stack = crimeDb.groupby(['BORO_NM', 'LAW_CAT_CD']).size().reset_index()
        df_stack.columns = ['BORO_NM', 'LAW_CAT_CD', 'Counts']
        crimeBarchart = px.bar(df_stack, x = 'BORO_NM', y = 'Counts', color = 
                        'LAW_CAT_CD', barmode = 'stack', labels = 
                                    {
                                        "LAW_CAT_CD" : "Crime",
                                        "BORO_NM" : "Area",
                                        "Counts" : "Number of Crimes"
                                    })
        crimeBarchart.update_layout(title = 'Crime Distribution Per Area')
        crimeBarchart.update_layout(clickmode='event+select')
        return crimeBarchart    

#   Pcp graph
    @app.callback(
        Output("PcpGraph", "figure"),
        Input('dropdown_groups', 'value'),
    )
    def output_figure(value):
        dff = airbnbDb[airbnbDb['price'] >= value]
        
        coordinatesPlot = px.parallel_coordinates(airbnbDb, color="price",
                                dimensions=chosenDimensionsPcp,
                                color_continuous_scale='agsunset',
                                color_continuous_midpoint=700)
        coordinatesPlot.update_traces(unselected_line_opacity=0.1, selector=dict(type='parallelcoordinates'))
        
        return coordinatesPlot
       

    #Bubble plot
    def updateFiltering(filter):
        if (filter != None):
            # print(filter)
            dimensionNumber = int(list(filter[0])[0][11])
            paramKey = list(filter[0])[0]

            if (filter[0][paramKey] == None):
                lowerLimit = None
                higherLimit = None
            else:
                lowerLimit = filter[0][paramKey][0][0]
                higherLimit = filter[0][paramKey][0][1]

            filteringArray[dimensionNumber][0] = lowerLimit
            filteringArray[dimensionNumber][1] = higherLimit
            applyFiltering()

    #it kinda works but improve 
    def applyFiltering():
        global filteredDb
        filteredDb = airbnbDb
        i = 0
        for x in chosenDimensionsPcp:
            if (filteringArray[i][0] != None):
                filteredDb = filteredDb[filteredDb[x] >= filteringArray[i][0]]
                filteredDb = filteredDb[filteredDb[x] <= filteringArray[i][1]]
            i+=1

    def resetFiltering():
        global filteringArray
        global filteredDb
        global tempDb
        filteringArray = cleanArray
        filteredDb = airbnbDb
        tempDb = filteredDb


    @app.callback(
        [
        Output("BubblePlot", "figure"),
        Output("Map", "figure"),
        Output("Violin", "figure")],
        Output("undo", "n_clicks"),
        Input('PcpGraph', 'restyleData'),
        Input('BubblePlot', "selectedData"),
        Input('Map', "selectedData"),
        Input("original", "children"),
        Input('dropdown_groups', 'value'), 
        Input('dropdown_verification', 'value'),
        Input("undo", "n_clicks"),
    )
    def output_figure(value, bubblePoints, mapPoints, trigger, area, identity, clicks): #, area, identity
        global previousValue
        global displayedPlots
        global tempDb
        
        updateFiltering(value)
        global filteredDb
        violin = px.violin(filteredDb, y="Profit", x="room type", color="room type", box=True, points="all", title='Profitalibility analysis')
        violin.update_layout(legend = dict(title = "Room Type"))
        violin.update_traces(marker_opacity=0.05, selector=dict(type='violin'))

        if (area is None) and (identity is None):
            tempDb = filteredDb
        elif not(area is None) and (identity is None):
            tempDb  = filteredDb[filteredDb['neighbourhood group'].str.contains(''.join(area))]
        elif (area is None) and not(identity is None):
            tempDb  = filteredDb[filteredDb['host_identity_verified'].str.contains(''.join(identity))]
        else:
            tempDb  = filteredDb[filteredDb['neighbourhood group'].str.contains(''.join(area)) & filteredDb['host_identity_verified'].str.contains(''.join(identity))]

        if value != previousValue or not displayedPlots:
            bubblePlot = bubbleAssign()
            mapMain = mapAssign()

            displayedPlots = True
            #print('changed')
        else:
            if (bubblePoints is not None and mapPoints is None):
                mapMain = mapAssign()
                bubblePlot = None
                selected_points = [point['pointNumber'] for point in bubblePoints.get('points', [])]
                #print(selected_points)
                mapMain.update_traces(selectedpoints=selected_points, selector=dict(type='scattermapbox'))
                #print('map should be highlighted')
            elif (bubblePoints is None and mapPoints is not None):
                bubblePlot = bubbleAssign()
                mapMain = None
                # 
                selected_points = [point['pointNumber'] for point in mapPoints.get('points', [])]
                #print(selected_points)
                bubblePlot.update_traces(selectedpoints=selected_points)
                #print('scatter should be highlighted')
            else:
                bubblePlot = bubbleAssign()
                mapMain = mapAssign()
                displayedPlots = False
                #print('niedozwolone') #do reset
                #output_figure(previousValue, None, None, None, )
                

        if (clicks > 0):
            print(1)
            resetFiltering()
            displayedPlots = False
            mapMain = mapAssign()
            bubblePlot = bubbleAssign()
            violin = px.violin(filteredDb, y="Profit", x="room type", color="room type", box=True, points="all", title='Profitalibility analysis')
            violin.update_layout(legend = dict(title = "Room Type"))
            violin.update_traces(marker_opacity=0.05, selector=dict(type='violin'))
            clicks = 0
            return bubblePlot, mapMain, violin, clicks
        previousValue = value
        return bubblePlot, mapMain, violin, clicks


    def mapAssign():
        mapMain = px.scatter_mapbox(data_frame = tempDb, color = "host_identity_verified",color_discrete_sequence= ["blue", "green", "orange"],lat = "lat", lon = "long", hover_data={'room type': True,'review rate number': True, 'price': True, 'service fee': True,  'availability 365': True,
        'host_identity_verified': True,'lat': False, 'long': False}, mapbox_style="carto-positron", zoom = 9) #hover_name = filteredDb['NAME']
        mapMain.update_layout(legend = dict(title = "Host Identity"), margin = {"r": 0, "l": 0, "t": 0,"b": 0},
        mapbox=dict(                
            ), dragmode='lasso')
        mapMain.update_traces(marker_opacity=0.2, selected_marker_opacity=1, unselected_marker_opacity=0.01, selector=dict(type='scattermapbox'))
        return mapMain

    def bubbleAssign():
        bubblePlot = px.scatter(filteredDb, x="last review", y="number of reviews", opacity = 0.5, title="Reviews analysis",
            size="reviews per month", color="review rate number", hover_name="neighbourhood", log_x=False, size_max=20,range_x=['2015-01-01','2019-12-31'])

        bubblePlot.update_traces(marker_sizemin=8,selected_marker_opacity=1,unselected_marker_opacity=0.005)
        bubblePlot.update_layout(dragmode='lasso')
        return bubblePlot
    
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
                                    html.H1(children = 'Hide Crime Analytics',style = {"font-size": "20px"}),

                                    html.Button(
                                    'Press',
                                    id = 'delete',
                                    n_clicks = 0,
                                    style = {"width": "90%", "text-align": "left"}
                                    ),
                                ], style = {"width": "10%", "display": "inline-block", "verticalAlign": "top"}
                            ),
                            html.Div(style = {"width": "1%", "display": "inline-block", "verticalAlign": "top"}),
                            #Crime Heatmap
                            html.Div(
                                [
                                    html.Div(children = [dcc.Graph(id = "CrimeMap", style={"width": "100vh", "height": "100vh"})]),
                                ], style = {"width": "50%", "display": "inline-block", "verticalAlign": "top"}
                            ),
                            html.Div(style = {"width": "1%", "display": "inline-block", "verticalAlign": "top"}),
                            #Visualizations
                            html.Div(
                                [
                                    html.H1(children = 'Crime Distribution', style = {"font-size": "20px", "text-align": "center"}),
                                    dcc.Graph(id = "CrimeBarchart",style={"width": "100%", "height": "90vh"}),
                                ], style = {"width": "38%", "display": "inline-block", "verticalAlign": "top", "float": "right"}
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
                    ], multi=False, placeholder='Choose Area', style = {"width": "100%"}),

                    html.Br(),

                    dcc.Dropdown(id='dropdown_verification', options=[
                    {'label': i, 'value': i} for i in airbnbDb['host_identity_verified'].unique()
                    ], multi=False, placeholder='Host Identity', style = {"width": "100%"}),
                    html.Br(), 

                    html.H1(children = 'Display Crime Analytics',style = {"font-size": "20px"}),
                    html.Button(
                        'Press',
                        id = 'reset',
                        n_clicks = 0,
                        style = {"width": "90%", "text-align": "left"}
                    ),
                    html.Br(),
                    html.H1(children = 'Reset filtering tool',style = {"font-size": "20px"}),
                    
                    html.A(html.Button('Reset', n_clicks = 0, style = {"width": "90%", "text-align": "left"}),href='/'),
                    html.Br(),
                    html.H1(children = 'Reset Visualizations',style = {"font-size": "20px"}),
                    html.Button(
                        'Reset',
                        id = 'undo',
                        n_clicks = 0,
                        style = {"width": "90%", "text-align": "left"}
                    ),
                    html.Br()
                ], style = {"width": "10%", "display": "inline-block"}), 
                html.Div(style={"width": "1%", "display": "inline-block"}),
                # Map
                html.Div(
                [
                    html.H1(children='Filtering tool', style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "PcpGraph"),
                    

                    html.Br(),

                    #html.H1(children='Properties based on profit', style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "Violin"),
                    #html.P("Profit Baseline", style = {"text-align": "left"}),
                    #dcc.Slider( id='slider-position', min=airbnbDb['Profit'].min(), max=airbnbDb['Profit'].max(), value=airbnbDb['Profit'].min(), step=None),
                    html.Div(id = 'x'),
                    #dcc.Graph(id = "Map_2"),
                    html.Br(),
    
                ], style= {"width": "40%", "display": "inline-block", "verticalAlign": "top"}),
                html.Div(style={"width": "1%", "display": "inline-block"}), 
                #Visualizations
                html.Div(
                [
                    html.H1(children= "Location of Properties", style = {"font-size": "20px", "text-align": "center"}),
                    dcc.Graph(id = "Map"),
                    html.Br(),
                    dcc.Graph(id = "BubblePlot"),
                    
                ], style= {"width": "48%", "display": "inline-block", "verticalAlign": "top", "text-align": "center"}
                ),
            ]
            Crime.clear()
            return Original
    # @app.callback(
    #     Output("undo", "n_clicks"),
    #     Input("undo", "n_clicks")
    # )
    # def undo(value):
    #     global x
    #     if (value > 0):
    #         x += 1
    #         print(x)
    #         return value
    # @app.callback(
    # Output('undo', 'n_clicks'),
    # [Input('url', 'pathname'),
    #  Input('undo', 'n_clicks')]
    # )
    # def display_page(relative_pathname, value):
    #     if value > 1:
            
app.run_server(debug=False, dev_tools_ui=False)
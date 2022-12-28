from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.scatterplot import Scatterplot

from dash import html
from dash import dcc

import plotly.express as px
import pandas as pd

from dash.dependencies import Input, Output
import datetime as dt


if __name__ == '__main__':

    # Create data
    df = px.data.iris()

    # Our data bases (I am using "processed" files because I made some small changes to those databases, I can send them to you if you want)
    airbnbDb = pd.read_csv('dashframework-main/airbnb_open_data_processed.csv', low_memory=False)
    crimeDb = pd.read_csv('dashframework-main/NYPD_Complaint_processed.csv', low_memory=False)
    
    # Task visualizations
    reviewScatterplot = px.scatter(airbnbDb, x="review rate number", y="number of reviews", title='Review scatterplot')

    mapScatter = px.scatter_mapbox(airbnbDb, lat="lat", lon="long",
                        color_discrete_sequence=["fuchsia"], zoom=3, height=900, title='Listings basic map')
    mapScatter.update_layout(mapbox_style="open-street-map")
    mapScatter.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    verifiedPiechart = px.pie(airbnbDb, values='1', names='host_identity_verified', title='Verified or not')

    violinPlot = px.violin(airbnbDb, y="price", x="room type", color="room type", box=True, points="all", title='Violin plot profitalibility analysis')

    crimeHeatmap = px.density_mapbox(crimeDb, lat='Latitude', lon='Longitude', radius=10,
                        center=dict(lat=0, lon=180), zoom=3,
                        mapbox_style="stamen-terrain", title='Crime heatmap')

    
    
    reviewGraph = dcc.Graph(figure=reviewScatterplot)
    mapGraph = dcc.Graph(figure=mapScatter)
    verifiedGraph = dcc.Graph(figure=verifiedPiechart)
    violinGraph = dcc.Graph(figure=violinPlot)
    crimeGraph = dcc.Graph(figure=crimeHeatmap)


    app.layout = html.Div(
            id="app-container",
            children=[
                # Left column
                html.Div(
                    id="left-column",
                    className="three columns",
                    children=make_menu_layout()
                ),

                # Right column
                html.Div(
                    id="right-column",
                    className="nine columns",
                    children=[
                        reviewGraph,
                        mapGraph,
                        verifiedGraph,
                        # Here there are not included because they make the whole app go very slow
                        #violinGraph,
                        #crimeHeatmap
                    ],
                ),
            ],
        )
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

    


    app.run_server(debug=False, dev_tools_ui=False)
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
    aDb = pd.read_csv('dashframework-main/airbnb_open_data_processed.csv', low_memory=False)
    crimeDb = pd.read_csv('dashframework-main/NYPD_Complaint_processed.csv', low_memory=False)
    
    # Instantiate custom views
    fig1 = px.scatter(df, x="sepal_width", y="sepal_length")
    fig2 = px.scatter(aDb, x="review rate number", y="number of reviews", title='Review scatterplot')
    fig3 = px.scatter_mapbox(aDb, lat="lat", lon="long",
                        color_discrete_sequence=["fuchsia"], zoom=3, height=900, title='Listings basic map')
    fig3.update_layout(mapbox_style="open-street-map")
    fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig3.show()

    fig4 = px.pie(aDb, values='1', names='host_identity_verified', title='Verified or not')
    #fig4.show()


    # fig5 = px.violin(aDb, y="price", x="room type", color="room type", box=True, points="all", title='Violin plot profitalibility analysis')
    # fig5.show()

    # fig6 = px.density_mapbox(crimeDb, lat='Latitude', lon='Longitude', radius=10,
    #                     center=dict(lat=0, lon=180), zoom=3,
    #                     mapbox_style="stamen-terrain", title='Crime heatmap')
    # fig6.show()
    
    reviewScatterplot = dcc.Graph(figure=fig2)
    basicMap = dcc.Graph(figure=fig3)
    verifiedPieChart = dcc.Graph(figure=fig4)

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
                        reviewScatterplot,
                        basicMap,
                        verifiedPieChart,
                        #dcc.Graph(figure=fig5),
                        #dcc.Graph(figure=fig6)
                    ],
                ),
            ],
        )
    # Define interactions
    @app.callback(
        Output(reviewScatterplot, "figure"), [
        Input("select-color-scatter-1", "value"),
        #Input(basicMap, 'selectedData')
    ])
    def update_scatter_1(selected_color):
        return dcc.Graph(figure=fig2.update_traces(marker=dict(color=selected_color)))
        #dcc.Graph(figure=px.scatter(aDb, x="review rate number", y="number of reviews", title='Review scatterplot', color=selected_color))

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
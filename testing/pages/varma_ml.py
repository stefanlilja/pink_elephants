import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.statespace.varmax import VARMAX, VARMAXResults
from testing.read_from_db import read_from_db

df_main, df_time = read_from_db()
df_merged = pd.merge(df_main, df_time, how='left', on='time_stamp')
df_merged = df_merged[['latitude', 'longitude', 'temperature', 'tag_id', 'year', 'month', 'day']]
df_daily_avg = df_merged.groupby(by=['tag_id', 'year', 'month', 'day']).mean()
df_daily_avg.reset_index(inplace=True)

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='Time series forecasting'),
    html.Div([
        "Select mode: ",
        dcc.RadioItems(['Modelling', 'Forecast'],
                       'Modelling',
                       id='analytics-input',
                       labelStyle={'display': 'block'}
        )
    ]),
    html.Br(),
    dcc.Graph(id='graph')
], style={'textAlign': 'center', 'margin': 'auto'})



@callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='analytics-input', component_property='value')
)
def update_figure(mode):
    if mode == 'Forecast':
        df_forecast = df_daily_avg[df_daily_avg['tag_id'] == 'AM105'][['latitude','longitude', 'temperature']].iloc[:240]
        train_data = df_forecast[:-5]
        test_data = df_forecast[-5:]
        model_fit = VARMAXResults.load('./data/ML/varma_forecast_1')
        yhat = model_fit.forecast(steps = len(test_data))
        fig = go.Figure(go.Scattermapbox(
            name = 'Training data',
            mode = "markers+lines",
            lon = df_forecast['longitude'].iloc[225:236],
            lat = df_forecast['latitude'].iloc[225:236],
            marker = {'size': 10}))

        fig.add_trace(go.Scattermapbox(
            name = 'Forecast',
            mode = "markers+lines",
            lon = yhat['longitude'],
            lat = yhat['latitude'],
            marker = {'size': 10}
            ))

        fig.add_trace(go.Scattermapbox(
            name = 'True path',
            mode = "markers+lines",
            lon = test_data['longitude'],
            lat = test_data['latitude'],
            marker = {'size': 10}))

        fig.update_layout(
            margin ={'l':0,'t':0,'b':0,'r':0},
            mapbox = {
                'center': {'lon': yhat['longitude'].mean(), 'lat': yhat['latitude'].mean()},
                'style': "stamen-terrain",
                'zoom': 12})
    else:

        loaded_model = VARMAXResults.load('./data/ML/varma_1_1_AM105')
        i = 10
        pred = loaded_model.predict(i, i+10)
        true_val = df_daily_avg.iloc[i:i+11]
        fig = go.Figure()

        fig.add_trace(go.Scattermapbox(
            name = 'Real data',
            mode = "markers+lines",
            lon = true_val['longitude'],
            lat =  true_val['latitude'],
            marker = {'size': 10}))

        fig.add_trace(go.Scattermapbox(
            name = 'Model',
            mode = "markers+lines",
            lon = pred['longitude'],
            lat = pred['latitude'],
            marker = {'size': 10},
            )
        )

        fig.update_layout(
            margin ={'l':0,'t':0,'b':0,'r':0},
            mapbox = {
                'center': {'lon': pred['longitude'].mean(), 'lat': pred['latitude'].mean()},
                'style': "stamen-terrain",
                'zoom': 8.7})

    return fig

import dash
from dash import html, dcc, callback, Input, Output, ctx
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.statespace.varmax import VARMAXResults

df_pivoted = pd.read_csv('./data/ML/pivoted_data.csv', header=[0, 1])
model_fit = VARMAXResults.load('./data/ML/varma_2_1_model')

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='Time series forecasting'),
    html.Div(
        [
            html.Div(),  # used as padding
            html.Div(),
            html.Div(
                [
                    "Select mode: ",
                    dcc.RadioItems(
                        ['Modelling', 'Forecasting'],
                        'Modelling',
                        id='radio_items',
                        labelStyle={'display': 'block'}
                    ),
                    html.Div(id='raio_item_container')
                ],
                style={'display': 'block'}
            ),
            html.Div(children=[
                html.Div(
                    [
                        "Select elephant tag: ",
                        dcc.Dropdown(
                            options=['AM91', 'AM93', 'AM99'],
                            value='AM91',
                            id='dropdown',
                            style={'display': 'block'}
                        )
                    ],
                    style={'display': 'block'}
                )
            ]),
            html.Div(
                [
                    'Select number of days:',
                    dcc.Input(
                        id='day_counter',
                        type='number',
                        value=15,
                        style={'display': 'block'}
                    )
                ],
                style={'display': 'block'}
            ),
            html.Div(),  # used as padding
            html.Div()
        ],
        style={
            'display': 'flex',
            'flex-direction': 'row',
            'justify-content': 'space-around'
        }
    ),
    dcc.Graph(id='graph')
], style={'textAlign': 'center', 'margin': 'auto'})


@callback(
    [
        Output(component_id='graph', component_property='figure'),
        Output(component_id='dropdown', component_property='value'),
        Output(component_id='day_counter', component_property='value')
    ],
    [
        Input(component_id='radio_items', component_property='value'),
        Input(component_id='dropdown', component_property='value'),
        Input(component_id='day_counter', component_property='value')
    ]
)
def update_figure(mode, tag_used, n_days):
    # when radio items are used to switch mode, we set certain default values
    if ctx.triggered_id == 'radio_items':
        tag_used = 'AM91'
        if mode == 'Forecasting':
            n_days = 3
        else:
            n_days = 15

    if mode == 'Forecasting':
        lag = 7
        split_index = int(len(df_pivoted) * 0.9)
        real_data = df_pivoted.iloc[split_index - lag:split_index + n_days][tag_used]
        forecast = model_fit.forecast(steps=n_days)

        fig = go.Figure(go.Scattermapbox(
            name='Training data',
            mode="markers+lines",
            lon=real_data['longitude'],
            lat=real_data['latitude'],
            marker={'size': 10}
        ))

        fig.add_trace(go.Scattermapbox(
            name='Forecast',
            mode="markers+lines",
            lon=forecast[f'{tag_used}_longitude'],
            lat=forecast[f'{tag_used}_latitude'],
            marker={'size': 10}
        ))

        fig.add_trace(go.Scattermapbox(
            name='True path',
            mode="markers+lines",
            lon=real_data.iloc[lag:]['longitude'],
            lat=real_data.iloc[lag:]['latitude'],
            marker={'size': 10}
        ))

        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox={
                'center':
                    {
                        'lon': real_data['longitude'].mean() * 1 / 3 + forecast[f'{tag_used}_longitude'].mean() * 2 / 3,
                        'lat': real_data['latitude'].mean() * 1 / 3 + forecast[f'{tag_used}_latitude'].mean() * 2 / 3
                    },
                'style': "stamen-terrain",
                'zoom': 10.5}
        )
    else:
        offset = 203  # how far into the data we start (chosen for aesthetic reasons)
        real_data = df_pivoted[tag_used].iloc[offset:offset + n_days]
        model_data = model_fit.predict(offset + 1, offset + n_days)

        fig = go.Figure(go.Scattermapbox(
            name='Real data',
            mode="markers+lines",
            lon=real_data['longitude'],
            lat=real_data['latitude'],
            marker={'size': 10}
        ))

        fig.add_trace(go.Scattermapbox(
            name='Model',
            mode="markers+lines",
            lon=model_data[f'{tag_used}_longitude'],
            lat=model_data[f'{tag_used}_latitude'],
            marker={'size': 10},
        )
        )

        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox={
                'center': {'lon': real_data['longitude'].mean(), 'lat': real_data['latitude'].mean()},
                'style': "stamen-terrain",
                'zoom': 10
            })

    return fig, tag_used, n_days

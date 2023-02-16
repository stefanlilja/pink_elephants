import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from testing.read_from_db import read_from_db
import numpy as np
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# dash things
dash.register_page(__name__)

# pd.set_option('display.expand_frame_repr', False)
df1, df2 = read_from_db()
df_merge = pd.merge(df1, df2, how='left', on='time_stamp')
df_merge_col = pd.DataFrame(df_merge['tag_id'].unique(), columns=['tag_id'])

# standardise longitude and latitude
scaler = StandardScaler()

layout = html.Div(
    style={'textAlign': 'center'},
    children=[
        html.H4(children='This is our DBSCAN analytics page'),

        html.Div(children=[
            dcc.Dropdown(
                df_merge_col.tag_id,
                'AM105',
                placeholder="Select an elephant group",
                id='dbscan-dropdown',
                style={
                    'width': '45%',
                    'display': 'inline-block'
                }
            ),
            html.Div(id='pandas-output-container')
        ]),
        html.Br(),

        html.Div(children=[
            html.Div(children=[
                # html.H6('Rain season vs. Dry season'),
                dbc.Row(children=[
                    dbc.Col(
                        html.H6("Rain season", style={"textAlign": "right"})
                    ),
                    dbc.Col(
                        html.H6("vs.", style={"textAlign": "center"}),
                        width=4
                    ),
                    dbc.Col(
                        html.H6("Dry season", style={"textAlign": "left"})
                    ),
                ]),
                dcc.Graph(
                    id='rain_graph',
                    style={'display': 'inline-block'}
                ),
                dcc.Graph(
                    id='dry_graph',
                    style={'display': 'inline-block'}
                ),
            ]),
        ]),
    ])


@callback([Output('rain_graph', 'figure'),
           Output('dry_graph', 'figure'),
           Output('pandas-output-container', 'children')],
          Input('dbscan-dropdown', 'value'))
def dropdown_output(group_select):
    while group_select != 'AM107':
        one_elephant = df_merge[df_merge['tag_id'] == group_select]
        one_elephant = one_elephant.assign(date=pd.to_datetime(one_elephant['time_stamp']).dt.date)

        min_num_point = int(one_elephant['date'].groupby([one_elephant['date']]).count().mean()) * 2

        norm = pd.DataFrame(scaler.fit_transform(one_elephant[['longitude', 'latitude']]))
        one_elephant = one_elephant.assign(long_norm=list(norm[0]), lat_norm=list(norm[1]))

        rain = one_elephant.loc[
            (one_elephant['date'] >= datetime.strptime('2007-11-01', '%Y-%m-%d').date()) &
            (one_elephant['date'] <= datetime.strptime('2008-04-30', '%Y-%m-%d').date())
            ]

        dry = one_elephant.loc[
            (one_elephant['date'] >= datetime.strptime('2008-05-01', '%Y-%m-%d').date()) &
            (one_elephant['date'] <= datetime.strptime('2008-10-31', '%Y-%m-%d').date())
            ]

        dbscan_rain = DBSCAN(eps=0.2, min_samples=min_num_point).fit(rain[['long_norm', 'lat_norm']])
        rain = rain.assign(labels=dbscan_rain.labels_)

        dbscan_dry = DBSCAN(eps=0.2, min_samples=min_num_point).fit(dry[['long_norm', 'lat_norm']])
        dry = dry.assign(labels=dbscan_dry.labels_)

        # Rain
        rain_unique_labels = set(rain['labels'])
        rain_core_samples_mask = np.zeros_like(rain['labels'], dtype=bool)
        rain_core_samples_mask[dbscan_rain.core_sample_indices_] = True
        rain['core_samples_mask'] = rain_core_samples_mask

        # Dry
        dry_unique_labels = set(dry['labels'])
        dry_core_samples_mask = np.zeros_like(dry['labels'], dtype=bool)
        dry_core_samples_mask[dbscan_dry.core_sample_indices_] = True
        dry['core_samples_mask'] = dry_core_samples_mask

        # create color spectrum
        colors_dry = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(dry_unique_labels))]
        colors_rain = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(rain_unique_labels))]

        fig_rain = go.Figure()
        fig_dry = go.Figure()

        # rain season plot
        for k, col in zip(rain_unique_labels, colors_rain):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = rain['labels'] == k

            xy = rain.loc[class_member_mask & rain['core_samples_mask']]
            # Bigger black points to add a border/edge to the points
            fig_rain.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=14,
                    color=f'rgba{tuple([0, 0, 0, 1])}',
                    opacity=1.0
                )
            ))

            # The color of the cluster
            fig_rain.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=12,
                    color=f'rgba{tuple(col)}',
                    opacity=1.0
                ),
                text=rain[['longitude', 'latitude']],
                hoverinfo='text'
            ))

            xy = rain.loc[class_member_mask & ~rain['core_samples_mask']]
            # Bigger black points to add a border/edge to the points
            fig_rain.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=9,
                    color=f'rgba{tuple([0, 0, 0, 1])}',
                    opacity=1.0
                )
            ))

            # The color of the cluster
            fig_rain.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=7,
                    color=f'rgba{tuple(col)}',
                    opacity=1.0
                ),
                text=rain[['longitude', 'latitude']],
                hoverinfo='text'
            ))

        fig_rain.update_layout(showlegend=False)
        fig_rain.update_layout(mapbox_style="stamen-terrain")
        fig_rain.update_layout(margin={"r": 20, "t": 0, "l": 20, "b": 0},
                               mapbox={
                                   'center': go.layout.mapbox.Center(
                                       lat=rain['latitude'].mean(),
                                       lon=rain['longitude'].mean()
                                   ),
                                   'zoom': 8.05
                               })

        # dry season plot
        for k, col in zip(dry_unique_labels, colors_dry):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = dry['labels'] == k

            xy = dry.loc[class_member_mask & dry['core_samples_mask']]
            # Bigger black points to add a border/edge to the points
            fig_dry.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=14,
                    color=f'rgba{tuple([0, 0, 0, 1])}',
                    opacity=1.0
                )
            ))

            # The color of the cluster
            fig_dry.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=12,
                    color=f'rgba{tuple(col)}',
                    opacity=1.0
                ),
                text=dry[['longitude', 'latitude']],
                hoverinfo='text'
            ))

            xy = dry.loc[class_member_mask & ~dry['core_samples_mask']]
            # Bigger black points to add a border/edge to the points
            fig_dry.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=9,
                    color=f'rgba{tuple([0, 0, 0, 1])}',
                    opacity=1.0
                )
            ))

            # The color of the cluster
            fig_dry.add_trace(go.Scattermapbox(
                lat=xy['latitude'],
                lon=xy['longitude'],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=7,
                    color=f'rgba{tuple(col)}',
                    opacity=1.0
                ),
                text=dry[['longitude', 'latitude']],
                hoverinfo='text',
            ))

        fig_dry.update_layout(mapbox_style="stamen-terrain")
        fig_dry.update_layout(showlegend=False)
        fig_dry.update_layout(margin={"r": 20, "l": 20, "t": 0, "b": 0},
                              mapbox={
                                  'center': go.layout.mapbox.Center(
                                      lat=dry['latitude'].mean(),
                                      lon=dry['longitude'].mean()
                                  ),
                                  'zoom': 8.05
                              })

        return fig_rain, fig_dry, f'you have selected {group_select}'

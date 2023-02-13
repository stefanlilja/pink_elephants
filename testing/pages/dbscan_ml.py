import dash
from dash import html, dcc, callback, Output, Input
import pandas as pd
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from testing.read_from_db import read_from_db
import numpy as np
from sklearn.cluster import DBSCAN
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# dash things
dash.register_page(__name__, path='/dbscan-ml')

# pd.set_option('display.expand_frame_repr', False)
df1, df2 = read_from_db()
df_merge = pd.merge(df1, df2, how='left', on='time_stamp')

# Select one elephant
AM105 = df_merge[df_merge['tag_id'] == 'AM105']

# Creating date column
AM105['date'] = pd.to_datetime(AM105['time_stamp']).dt.date

# Mean number of instances/observations per day
minPoint = int(AM105['date'].groupby([AM105['date']]).count().mean()) * 2

# standardise longitude and latitude
scaler = StandardScaler()

AM105[['long_norm', 'lat_norm']] = scaler.fit_transform(AM105[['longitude', 'latitude']])

# divide into rain and dry seasons
# Nov 2007- apr 2008
AM105_rain = AM105.loc[(AM105['date'] >= datetime.strptime('2007-11-01', '%Y-%m-%d').date()) &
                       (AM105['date'] <= datetime.strptime('2008-04-30', '%Y-%m-%d').date())]

# May 2008 - oct 2008
AM105_dry = AM105.loc[(AM105['date'] >= datetime.strptime('2008-05-01', '%Y-%m-%d').date()) &
                      (AM105['date'] <= datetime.strptime('2008-10-31', '%Y-%m-%d').date())]

# Training the model
# Rain
db_rain = DBSCAN(eps=0.2, min_samples=minPoint).fit(AM105_rain[['long_norm', 'lat_norm']])
AM105_rain['labels'] = db_rain.labels_

# Dry
db_dry = DBSCAN(eps=0.2, min_samples=minPoint).fit(AM105_dry[['long_norm', 'lat_norm']])
AM105_dry['labels'] = db_dry.labels_

# Rain
rain_unique_labels = set(AM105_rain['labels'])
rain_core_samples_mask = np.zeros_like(AM105_rain['labels'], dtype=bool)
rain_core_samples_mask[db_rain.core_sample_indices_] = True
AM105_rain['core_samples_mask'] = rain_core_samples_mask

# Dry
dry_unique_labels = set(AM105_dry['labels'])
dry_core_samples_mask = np.zeros_like(AM105_dry['labels'], dtype=bool)
dry_core_samples_mask[db_dry.core_sample_indices_] = True
AM105_dry['core_samples_mask'] = dry_core_samples_mask

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

    class_member_mask = AM105_rain['labels'] == k

    xy = AM105_rain.loc[class_member_mask & AM105_rain['core_samples_mask']]
    # Bigger black points to add a border/edge to the points
    fig_rain.add_trace(go.Scattermapbox(
        lat=xy['latitude'],
        lon=xy['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color=f'rgba{tuple([0, 0, 0, 1])}',
            opacity=1.0
        ),
        text=AM105_rain[['latitude', 'longitude']],
        hoverinfo='text'
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
        text=AM105_rain[['latitude', 'longitude']],
        hoverinfo='text'
    ))

    xy = AM105_rain.loc[class_member_mask & ~AM105_rain['core_samples_mask']]
    # Bigger black points to add a border/edge to the points
    fig_rain.add_trace(go.Scattermapbox(
        lat=xy['latitude'],
        lon=xy['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9,
            color=f'rgba{tuple([0, 0, 0, 1])}',
            opacity=1.0
        ),
        text=AM105_rain[['latitude', 'longitude']],
        hoverinfo='text',
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
        text=AM105_rain[['latitude', 'longitude']],
        hoverinfo='text',
    ))

fig_rain.update_layout(showlegend=False)
fig_rain.update_layout(mapbox_style="stamen-terrain")
fig_rain.update_layout(margin={"r": 20, "t": 0, "l": 20, "b": 0},
                       mapbox={'center': go.layout.mapbox.Center(lat=-24.8, lon=32), 'zoom': 8})

# dry season plot
for k, col in zip(dry_unique_labels, colors_dry):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = AM105_dry['labels'] == k

    xy = AM105_dry.loc[class_member_mask & AM105_dry['core_samples_mask']]
    # Bigger black points to add a border/edge to the points
    fig_dry.add_trace(go.Scattermapbox(
        lat=xy['latitude'],
        lon=xy['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color=f'rgba{tuple([0, 0, 0, 1])}',
            opacity=1.0
        ),
        text=AM105_dry[['latitude', 'longitude']],
        hoverinfo='text'
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
        text=AM105_dry[['latitude', 'longitude']],
        hoverinfo='text'
    ))

    xy = AM105_dry.loc[class_member_mask & ~AM105_dry['core_samples_mask']]
    # Bigger black points to add a border/edge to the points
    fig_dry.add_trace(go.Scattermapbox(
        lat=xy['latitude'],
        lon=xy['longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9,
            color=f'rgba{tuple([0, 0, 0, 1])}',
            opacity=1.0
        ),
        text=AM105_dry[['latitude', 'longitude']],
        hoverinfo='text',
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
        text=AM105_dry[['latitude', 'longitude']],
        hoverinfo='text',
    ))


fig_dry.update_layout(mapbox_style="stamen-terrain")
fig_dry.update_layout(showlegend=False)
fig_dry.update_layout(margin={"r": 20, "t": 0, "l": 20, "b": 0},
                      mapbox={'center': go.layout.mapbox.Center(lat=-24.8, lon=32), 'zoom': 8})

layout = html.Div(children=[
    html.H4(children='This is our DBSCAN analytics page'),

    html.Div(children='''
        This is our DBSCAN analytics page content.
    '''),
    html.Div(children=[
        dcc.Graph(
            id='db_graph_rain',
            figure=fig_rain,
            style={'display': 'inline-block'}
        ),
        dcc.Graph(
            id='db_graph_dry',
            figure=fig_dry,
            style={'display': 'inline-block'}
        ),
    ], style={'align': 'center'}),
])

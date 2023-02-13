import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
from sqlalchemy import create_engine
from configparser import ConfigParser
import pandas as pd

dash.register_page(__name__, path='/')

config = ConfigParser()
config.read('database.ini')
conf = config['postgresql']

engine = create_engine(f"postgresql://{conf['username']}:{conf['password']}@{conf['hostname']}/{conf['database']}")
with engine.connect() as conn:
    df_main = pd.read_sql_table('location_ping', conn)
    df_time = pd.read_sql_table('time', conn)

df_year_month = df_time[['year', 'month']].drop_duplicates().reset_index(drop=True)

layout = html.Div([
    html.H4('Elephant tracking technology (patent pending)', style={'textAlign': 'center'}),
    html.Div(
        style={'textAlign': 'center', "margin": "auto"},
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        ['AM105', 'AM107', 'AM108', 'AM110', 'AM239', 'AM253', 'AM254',
                         'AM255', 'AM306', 'AM307', 'AM308', 'AM91', 'AM93', 'AM99'],
                        ['AM105'],
                        multi=True,
                        placeholder="Select a group",
                        id='group-dropdown',
                        style={
                            'width': '45%',
                            'alignment': 'right',
                            'display': 'inline-block'
                        }
                    )
                ]),

            dcc.Graph(
                id='graph-with-slider'
            ),

            dcc.RangeSlider(
                df_year_month.index.min(),
                df_year_month.index.max(),
                1,
                value=[df_year_month.index[12], df_year_month.index[13]],
                marks={
                    0: '2007: Aug',
                    1: 'Sep',
                    2: 'Okt',
                    3: 'Nov',
                    4: 'Dec',
                    5: '2008: Jan',
                    6: 'Feb',
                    7: 'Mar',
                    8: 'Apr',
                    9: 'May',
                    10: 'Jun',
                    11: 'Jul',
                    12: 'Aug',
                    13: 'Sep',
                    14: 'Okt',
                    15: 'Nov',
                    16: 'Dec',
                    17: '2009: Jan',
                    18: 'Feb',
                    19: 'Mar',
                    20: 'Apr',
                    21: 'May',
                    22: 'Jun',
                    23: 'Jul',
                    24: 'Aug'
                },
                id='my-range-slider'
            ),

            dcc.RangeSlider(
                1,
                31,
                1,
                value=[15, 18],
                id='day-slider',
                tooltip={
                    "placement": "bottom",
                    "always_visible": True
                }
            ),
        ]),

    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')

])


# configuring callback functions
@callback(
    Output('graph-with-slider', 'figure'),
    [Input('my-range-slider', 'value'),
     Input('group-dropdown', 'value'),
     Input('day-slider', 'value'),
     Input('url', 'pathname')]
)
def output_callbacks(range_selector, group_selector, day_selector, pathname):
    if pathname == '/':
        min_year, min_month = df_year_month.iloc[range_selector[0]]
        max_year, max_month = df_year_month.iloc[range_selector[1]]

        df_2 = (df_main.loc[df_main.time_stamp >= f'{min_year}-{min_month:02}-{day_selector[0]:02} 00:00:00']
                .loc[df_main.time_stamp <= f'{max_year}-{max_month:02}-{day_selector[1]:02} 23:59:00']
                .query(f'tag_id in {group_selector}')
                )

        fig = px.line_mapbox(
            df_2,
            lat='latitude',
            lon='longitude',
            color='tag_id',
            width=1500,
            height=550,
            hover_data=['temperature']
        )
        fig.update_layout(mapbox_style='stamen-terrain')
        fig.update_layout(margin={"r": 0, "l": 0, "t": 0, "b": 0})

        return fig

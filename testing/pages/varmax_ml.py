import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__)

layout = html.Div(children=[
    html.H1(children='This is our VARMAX analytics page'),
    html.Div([
        "Select an elephant group: ",
        dcc.RadioItems(['G-1', 'G-2', 'G-3'],
                       'G-1',
                       id='analytics-input')
    ]),
    html.Br(),
    html.Div(id='analytics-output'),
])


@callback(
    Output(component_id='analytics-output', component_property='children'),
    Input(component_id='analytics-input', component_property='value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'

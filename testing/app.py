import dash as dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CERULEAN])

app.layout = html.Div([
    dbc.Row([
        dbc.Col(width=4),
        dbc.Col(
            html.H1(children=['Project Pink Elephant'], style={'color': 'hotpink'}),
            width=3,
            style={
                "textAlign": "center",
                # plus your style for the fonts, etc...
            }
        ),
        dbc.Col(
            html.Div(
                html.Img(src="assets/elephant.png", style={'height': '25%', 'width': '25%'}),
                style={"float": "left"}  # one of many approaches...
            )
        ),
        # dbc.Col(width=3),
    ]),
    # html.Div(children=[
    #     dbc.CardImg(src='elephant.png', style={"width": "9rem"}),
    #     html.H1('Project Pink Elephant', style={'textAlign': 'center', 'color': 'hotpink'})]),
    html.Hr(),
    html.Div(
        [
            html.Div(children=[
                dcc.Link(href=page["relative_path"])
            ])
            for page in dash.page_registry.values()
        ], style={'display': 'none'}
    ),
    html.Div(children=[
        dbc.ButtonGroup([
            dbc.Button(
                "Elephant tracking",
                href="/",
                color="primary"
            ),
            dbc.Button(
                "VARMAX ML model/forecasting",
                href="/varmax-ml",
                color="primary",
            ),

            dbc.Button(
                "DBSCAN Clustering model",
                href="/dbscan-ml",
                color="primary"
            )
        ],
            size="lg",
            className="me-1",
        ),
    ], style={'textAlign': 'center'},
    ),

    dash.page_container
], className='bg-light')

if __name__ == "__main__":
    app.run_server(debug=True)

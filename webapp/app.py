import dash as dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CERULEAN]
)

app.layout = html.Div([
    dbc.Row(children=[
        dbc.Col(width=3),
        dbc.Col(
            html.Div(
                html.Img(src="assets/elephant.png", style={'height': '25%', 'width': '25%'}),
                style={"float": "left"}
            )
        ),
        dbc.Col(
            html.H2(children=['Project Pink Elephant'], style={'color': 'hotpink'}),
            width=2,
            style={
                "textAlign": "center",
            }
        ),
        dbc.Col(
            html.Div(
                html.Img(src="assets/elephant the other way.png", style={'height': '25%', 'width': '25%'}),
                style={"float": "right"}
            )
        ),
        dbc.Col(width=3),
    ], style={"textAlign": "center"}),
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
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Elephant tracking",
                    href="/",
                    color="primary"
                ),
                dbc.Button(
                    "VARMA model/forecasting",
                    href="/varma-ml",
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

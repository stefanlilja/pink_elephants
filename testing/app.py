import dash as dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div([
    html.H1('Project Pink Elephant', style={'textAlign': 'center', 'color': 'hotpink'}),
    html.Hr(),
    html.Div(
        [
            html.Div(children=[
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"], className='bg-light border'
                )
            ])
            for page in dash.page_registry.values()
        ]
    ),

    dash.page_container
])

if __name__ == "__main__":
    app.run_server(debug=True)

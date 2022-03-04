
from server import app

from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash

import src.layout
import src.callback_uploader

@app.callback(
    Output('analytics', 'children'),
    Input('stored_data', 'data')
)
def analytic_cards(data):
    if data is None:
        return dash.no_update
    else: 
        return html.Div([
            dbc.Card(
                dbc.CardBody(
                    html.H1('TEST')
                ),
            ),
        ])  

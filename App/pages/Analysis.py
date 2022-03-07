from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import os
import io
import base64
from flask import session
import pandas as pd
import datetime

from server import app

config = {
    'toImageButtonOptions': {
        'format': 'svg', # one of png, svg, jpeg, webp
        'filename': 'custom_image',
        'height': 500,
        'width': 700,
        'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
    }
}

layout = html.Div([
    html.Div(html.Div(children =[],id = "alert-div")),
    html.H1("Analysis", className="display-2 mb-5 "),
    html.Hr(),
    ])


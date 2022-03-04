from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc
import os
import io
import base64
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

if not os.path.exists("image"):
    os.mkdir("image")

layout = html.Div([
    html.Div(html.Div(children =[],id = "alert-div")),
    html.H1("Dashboard", className="display-2 mb-5 "),
    html.Hr(),
    dbc.Card(
        [
            dbc.CardHeader("Upload your schedule", className="fs-3"),
            dbc.CardBody([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Schedule Files')
                    ], id='uploader_ui', className='shadow bg-primary text-white'),
                    style={
                        'width': '50%',
                        'lineHeight': '60px',
                        'textAlign': 'center',
                        'margin': 'auto',
                        'marginTop': '2rem',
                    }, 
                    className = 'text-center mb-5 border border-1 rounded-3',
                    # Allow multiple files to be uploaded
                    multiple=True
                ),              
            ],),
        ], className="w-50 m-auto my-5"),
    html.Div(id = "upload_table"),
    html.Div(id = "upload-output")
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            return update_upload(df, filename, date)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            return update_upload(df, filename, date)
    except Exception as e:
        print("There's an error -- {} is missing".format(e))
        return dbc.Alert([
            html.H1("An opsies occured 😥"),
            html.Hr(),
            html.P(["There is some error with the file you uploaded. Check ",html.A('reference page', href="/pages/reference"), " for more info."],
            className="fs-3"),
            ],
            dismissable=True,
            color="warning",
            className= "fixed-top w-25 mt-5",
            style = {
                "zIndex": "2",
                "marginLeft": "73%",
            },
            )

def update_upload(df, filename, date):
    df = df.rename(columns=df.iloc[0], )
    df2 = df.drop([0,0])

    df2['Structure'] = df2['Home Story Name'].str.contains('basement',case=False,regex=True)

    return html.Div([  
        html.H5(filename),
        dbc.Alert(
            [
                html.H1("Upload is SUCCESSFUL!"),
                html.Hr(),
                html.P("{} has been uploaded succesfully".format(filename), className="h4"),
                html.P("Happy designing! 😁")
            ], 
            is_open=True, 
            fade=True,
            dismissable=True,
            className= "fixed-top w-25 mt-5",
            style = {
                "zIndex": "2",
                "marginLeft": "73%",
            },
        ),
        html.H6(datetime.datetime.fromtimestamp(date)),
        dash_table.DataTable(
            data=df2.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df2.columns],
            page_size=15,
            style_data={
                'whiteSpace': 'normal',
                'width': 'auto',         
            },
            id='df2 tbl',
        ),
        dcc.Store(id='stored_data', data=df2.to_json()),
        #html.Div(id='analytics')
    ], className='mx-5')

@app.callback(
    Output('upload-output', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified')
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
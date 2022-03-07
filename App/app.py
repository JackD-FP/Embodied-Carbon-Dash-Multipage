import os
import io
import base64
import datetime
from dash import html, Input, Output, State, dcc, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from numpy import True_
import pandas as pd

from src.layout import layout

from server import app
from pages import Analysis, reference, total_embodied_carbon
from src import overall_carbon 

if not os.path.exists("image"):
    os.mkdir("image")

#load basic material and do some shit about material name.
df_db = pd.read_csv("Basic Material v3.csv")
df_db['material'] = df_db['material name'].str.cat(df_db['material variant name'], sep = ' ')
df_db['material'] = df_db['material'].str.cat(df_db['locations'], sep =" - ")

#read databases from greenbook, ice and epic
df_gb = pd.read_csv("Greenbook _reduced.csv")
df_ice =pd.read_csv("ice _reduced.csv")
df_epic = pd.read_csv("epic _reduced.csv")

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "32rem",
    "padding": "2rem 3rem",
    "backgroundColor": "#f8f9fa",
}

CONTENT_STYLE = {
    "marginLeft": "34rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}

global_df = []

sidebar = html.Div(
    [
        html.Img(src="/assets/f+p_mono.svg", className="img-thumbnail"),
        html.H5("Embodied Carbon", className="my-5 display-6", style={"font": "2rem"}),
        html.Hr(),
        html.P(
            "Analyse design using this Embodied Carbon Calculator. More information in the reference page below.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/", active="exact", id="dashboard_click",),
                dbc.NavLink("Analysis", href="/pages/Analysis", active="exact"),
                dbc.NavLink("Total Embodied Carbon", href="/pages/total_embodied_carbon", active="exact"),
                dbc.NavLink("Reference", href="/pages/reference", active="exact")
            ],
            vertical=True,
            pills=True,
            style={
                "marginTop": "3rem",
                "fontSize": "1.5rem"
            },
            className="display-6",
        ),
    ],
    style=SIDEBAR_STYLE,
)

index = html.Div(
    [
        dcc.Store(id="schedule_store"),
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
                    ], id='uploader_ui', className='bg-primary text-white'),
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
            ]),

        ], className="w-50 m-auto my-5"),
        html.Div(id = "upload-output"),
        html.Div(id = "refresh_table"),
    ],
    id = "index_div")

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            return update_upload(df, filename, date)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            return update_upload(df, filename, date)
    except Exception as e:
        print("There's an error -- {} is missing".format(e))
        return dbc.Alert([
            html.H1("An opsies occured 😢"),
            html.Hr(),
            html.P(["There is some error with the file you uploaded. Check ",html.A('reference page', href="/pages/reference"), " for more info."],
            className="fs-3 p-3"),
            ],
            dismissable=True,
            color="warning",
            className= "fixed-top w-25 mt-5 shadow",
            style = {
                "zIndex": "2",
                "marginLeft": "73%",
            },)


def update_upload(df, filename, date):
    df = df.rename(columns=df.iloc[0])
    df2 = df.drop([0,0])

    df2['Structure'] = df2['Home Story Name'].str.contains('basement',case=False,regex=True)

    return html.Div([  
        dbc.Alert(
            [
                html.H1("Upload is SUCCESSFUL!"),
                html.Hr(),
                html.P("{} has been uploaded succesfully".format(filename), className="h4"),
                html.P("Happy designing! 😁")
            ], 
            is_open=True, 
            dismissable=True,
            className= "fixed-top w-25 mt-5 p-3",
            style = {
                "zIndex": "2",
                "marginLeft": "73%",
            },
        ),
        dcc.Store(id='stored_data', data=df2.to_json(), storage_type="session"),
        dash_table.DataTable(
            data=df2.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df2.columns],
            page_size=15,
            style_data={
                'whiteSpace': 'normal',
                'width': 'auto',         
            },
            id='data_table',
            persistence=True,
            persistence_type="memory")
    ], className='mx-5')

@app.callback(
    Output('upload-output', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



content = html.Div([],
    id="page-content", 
    style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url", refresh=False), sidebar, content])

#PAGE ROUTER!!!!
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return index
    elif pathname == "/pages/Analysis":
        return Analysis.layout
    elif pathname == "/pages/total_embodied_carbon":
        return total_embodied_carbon.layout
    elif pathname == "/pages/reference":
        return reference.layout
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger m-auto"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)

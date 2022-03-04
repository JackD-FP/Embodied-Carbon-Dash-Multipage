
import dash
from dash import html, Input, Output, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from src.layout import layout

from server import app
from pages import dashboard, reference, total_embodied_carbon

#load basic material and do some shit about material name.
df_db = pd.read_csv("Basic Material v3.csv")
df_db['material'] = df_db['material name'].str.cat(df_db['material variant name'], sep = ' ')
df_db['material'] = df_db['material'].str.cat(df_db['locations'], sep =" - ")

#read databases from greenbook, ice and epic
df_gb = pd.read_csv("Greenbook _reduced.csv")
df_ice =pd.read_csv("ice _reduced.csv")
df_epic = pd.read_csv("epic _reduced.csv")


#app.layout = html.Div(layout, className="position-relative", style={'marginLeft': "10rem", 'marginRight': '10rem'})

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "32rem",
    "padding": "2rem 3rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "34rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

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
                dbc.NavLink("Dashboard", href="/pages/dashboard", active="exact"),
                dbc.NavLink("Total Embodied Carbon", href="/pages/total_embodied_carbon", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
                dbc.NavLink("Reference", href="/pages/reference", active="exact")
            ],
            vertical=True,
            pills=True,
            style={
                "marginTop": "3rem",
                "font-size": "1.5rem"
            },
            className="display-6",
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/pages/dashboard":
        return dashboard.layout
    elif pathname == "/pages/total_embodied_carbon":
        return total_embodied_carbon.layout
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
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

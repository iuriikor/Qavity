from flask import Flask
from dash import Dash, _dash_renderer
from quart import Quart
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")
dash_server = Flask('ControlGUIdash_v02')
webcam_server = Quart(__name__)
app = Dash(server=dash_server,
           external_stylesheets=dmc.styles.ALL,
           use_pages=True)

from dash import Dash
import dash_bootstrap_components as dbc
import static_variables

variables = static_variables.get_singleton()

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=external_stylesheets,
           suppress_callback_exceptions=True)

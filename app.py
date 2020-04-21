import dash


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname='/')
server = app.server
app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = False
app.css.config.serve_locally = False
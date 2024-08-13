from dash import dcc, html, Dash
import dash_bootstrap_components as dbc
from inventory_dashboard_app import create_inventory_dashboard
from financial_dashboard import create_financial_dashboard
#from demand_dashboard import create_demand_dashboard
from dash.dependencies import Input, Output, State
# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout with a navigation system
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Unified Dashboard Application", className="mb-4 mt-2 text-center"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Tabs(id="tabs", value='financial', children=[
            dcc.Tab(label='Financial Dashboard', value='financial'),
            dcc.Tab(label='Inventory Dashboard', value='inventory'),
            dcc.Tab(label='Demand Dashboard', value='demand'),
        ]), width=12)
    ]),
    
    html.Div(id='tabs-content')
])

# Define callback to switch between dashboards
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'financial':
        return create_financial_dashboard()
    elif tab == 'inventory':
        print('came here')
        return create_inventory_dashboard()
   
    return html.Div("Select a dashboard from the tabs above.")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=5020)

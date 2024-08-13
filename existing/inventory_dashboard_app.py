from flask import Flask
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialize Flask server for the inventory dashboard
inventory_dashboard_server = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=inventory_dashboard_server, external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname='/inventory_dash/')

# Load and preprocess the data
data_path = 'mnt/data/apparel.csv'
df = pd.read_csv(data_path)

# Required columns based on provided details
required_columns = [
    'Handle', 'Title', 'Vendor', 'Variant Inventory Qty', 'Variant Price', 'Image Src'
]

# Verify all required columns are present
for col in required_columns:
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in the dataset")

# Clean the data by removing any rows with null values in the 'Vendor' or 'Title' columns
df = df.dropna(subset=['Vendor', 'Title'])

# Simulate a 'Date' column for inventory trends
df['Date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')

# Ensure that the dropdown options are constructed correctly
vendor_options = [{'label': 'All Vendors', 'value': 'all'}] + [{'label': vendor, 'value': vendor} for vendor in df['Vendor'].unique()]
product_options = [{'label': 'All Products', 'value': 'all'}] + [{'label': title, 'value': title} for title in df['Title'].unique()]

# Function to create the inventory dashboard
def create_inventory_dashboard():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1('Inventory Optimization Dashboard', className='text-center text-primary mb-4'), width=12)
        ]),
        dbc.Row([
           
            dbc.Col(dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='vendor-dropdown',
                    options=vendor_options,
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='product-dropdown',
                    options=product_options,
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ), width=6)
            ], className='mb-2')),
            dbc.Row([
                dbc.Col(dbc.Button("Run Inventory Optimization", id='optimize-inventory', color="primary", className="mr-1"), width=12)
            ])
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='inventory-measures-graph'), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='inventory-trend-graph'), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='inventory-forecast-trends-graph'), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='optimization-results', className='mt-4'), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='inventory-alerts', className='mt-4'), width=12)
        ])
    ], fluid=True)

# Callbacks for interactivity
@app.callback(
    Output('inventory-measures-graph', 'figure'),
    Output('inventory-trend-graph', 'figure'),
    Output('inventory-forecast-trends-graph', 'figure'),
    Output('inventory-alerts', 'children'),
    Input('vendor-dropdown', 'value'),
    Input('product-dropdown', 'value'),
    Input('optimize-inventory', 'n_clicks')
)
def update_graphs(vendor, product, n_clicks):
    filtered_df = df.copy()
    
    # Debugging prints
    print(f"Vendor selected: {vendor}")
    print(f"Product selected: {product}")
    print(f"Number of clicks: {n_clicks}")
    
    if vendor != 'all':
        filtered_df = filtered_df[filtered_df['Vendor'] == vendor]
    if product != 'all':
        filtered_df = filtered_df[filtered_df['Title'] == product]
    
    # Check if filtered data is empty
    if filtered_df.empty:
        print("Filtered DataFrame is empty.")
        return {}, {}, {}, html.P("No data available for the selected criteria.")

    inventory_measures_fig = {
        'data': [{
            'x': filtered_df['Title'],
            'y': filtered_df['Variant Inventory Qty'],
            'type': 'bar',
            'name': 'Inventory Qty'
        }],
        'layout': {
            'title': 'Inventory Measures'
        }
    }
    
    inventory_trend_fig = {
        'data': [{
            'x': filtered_df['Title'],
            'y': filtered_df['Variant Price'],
            'type': 'line',
            'name': 'Price'
        }],
        'layout': {
            'title': 'Inventory Trend'
        }
    }

    # Creating a forecast trends figure
    forecast_fig = px.line(filtered_df, x='Date', y='Variant Inventory Qty', title='Inventory Forecast Trends')

    # AI-driven inventory alerts
    alert_messages = []
    low_inventory_threshold = 10  # Example threshold for low inventory
    high_inventory_threshold = 1000  # Example threshold for high inventory

    for _, row in filtered_df.iterrows():
        if row['Variant Inventory Qty'] < low_inventory_threshold:
            alert_messages.append(f"Alert: Low inventory for {row['Title']} (Vendor: {row['Vendor']}) - Quantity: {row['Variant Inventory Qty']}")
        if row['Variant Inventory Qty'] > high_inventory_threshold:
            alert_messages.append(f"Alert: High inventory for {row['Title']} (Vendor: {row['Vendor']}) - Quantity: {row['Variant Inventory Qty']}")

    alerts = html.Ul([html.Li(alert) for alert in alert_messages]) if alert_messages else html.P("No inventory alerts")

    return inventory_measures_fig, inventory_trend_fig, forecast_fig, alerts

@app.callback(
    Output('optimization-results', 'children'),
    Input('optimize-inventory', 'n_clicks')
)
def run_inventory_optimization(n_clicks):
    if n_clicks is not None:
        # Placeholder for optimization logic
        return "Inventory optimization has been run."
    return "Click the button to run inventory optimization."

@inventory_dashboard_server.route('/inventory_dashboard')
def inventory_dashboard():
    return app.index()  # Use Dash's default index

if __name__ == '__main__':
    app.layout = create_inventory_dashboard()
    inventory_dashboard_server.run(debug=True,port=5015)

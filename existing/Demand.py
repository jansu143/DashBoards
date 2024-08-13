from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

# Initialize Flask server
server = Flask(__name__)

# Initialize Dash app with a Bootstrap theme
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load and prepare data
data_path = 'mnt/data/apparel.csv'
df = pd.read_csv(data_path, encoding='ISO-8859-1')

# Adding synthetic columns for Inventory, Replenishment, Demand, and Financial Metrics
df['InventoryOnHand'] = np.random.randint(50, 500, size=df.shape[0])
df['Replenishment'] = np.random.randint(20, 100, size=df.shape[0])
df['Demand'] = np.random.randint(30, 150, size=df.shape[0])

# Financial Metrics
df['Revenue'] = df['Demand'] * np.random.randint(100, 500, size=df.shape[0])
df['Cost'] = df['Replenishment'] * np.random.randint(50, 150, size=df.shape[0])
df['Profit'] = df['Revenue'] - df['Cost']

# Convert dates to datetime objects
df['Date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
def create_demand_dashboard():
    return html.Div([
        html.H2("Inventory Dashboard"),
        # Add your inventory dashboard components here
    ])
# Define the layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Demand Allocation and Financial Impact Dashboard"), className="mb-4 mt-2")
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4("Filters"),
            dcc.Dropdown(
                id='product-dropdown',
                options=[{'label': str(p), 'value': p} for p in df['Title'].unique() if pd.notna(p)],
                value=df['Title'].unique()[0],
                placeholder="Select a product...",
                style={'margin-bottom': '10px'}
            ),
            dcc.Dropdown(
                id='location-dropdown',
                options=[{'label': 'USA', 'value': 'USA'}, {'label': 'Global', 'value': 'Global'}],
                value='USA',
                placeholder="Select a location...",
                style={'margin-bottom': '10px'}
            ),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['Date'].min(),
                end_date=df['Date'].max(),
                display_format='YYYY-MM-DD',
                className="mb-4"
            )
        ], width=3),
        
        dbc.Col([
            html.H4("Summary Table"),
            dash_table.DataTable(
                id='summary-table',
                columns=[
                    {"name": "Date", "id": "Date", "type": "datetime"},
                    {"name": "Inventory On Hand", "id": "InventoryOnHand", "type": "numeric"},
                    {"name": "Replenishment", "id": "Replenishment", "type": "numeric"},
                    {"name": "Demand", "id": "Demand", "type": "numeric"},
                    {"name": "Revenue", "id": "Revenue", "type": "numeric"},
                    {"name": "Cost", "id": "Cost", "type": "numeric"},
                    {"name": "Profit", "id": "Profit", "type": "numeric"},
                ],
                data=df.to_dict('records'),
                style_table={'height': '400px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
            ),
        ], width=9)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='inventory-graph')
        ], width=12),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='financial-graph')
        ], width=12),
    ]),
    
    dbc.Row([
        dbc.Col(html.Div(id='drilldown-output'), width=12)
    ])
])

# Define callbacks to update graphs based on dropdown selection and date range
@app.callback(
    [Output('inventory-graph', 'figure'),
     Output('financial-graph', 'figure'),
     Output('summary-table', 'data')],
    [Input('product-dropdown', 'value'),
     Input('location-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(selected_product, selected_location, start_date, end_date):
    filtered_data = df[(df['Title'] == selected_product) & 
                       (df['Date'] >= start_date) & 
                       (df['Date'] <= end_date)]
    
    # Inventory optimization graph
    inventory_fig = go.Figure()
    inventory_fig.add_trace(go.Bar(x=filtered_data['Date'], y=filtered_data['InventoryOnHand'], name='Inventory On Hand', marker_color='blue'))
    inventory_fig.add_trace(go.Bar(x=filtered_data['Date'], y=filtered_data['Replenishment'], name='Replenishment', marker_color='green'))
    inventory_fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Demand'], mode='lines+markers', name='Demand', line=dict(color='red', width=2)))
    
    inventory_fig.update_layout(
        title='Inventory Optimization',
        barmode='stack',
        xaxis_title='Date',
        yaxis_title='Units',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        hovermode='x unified',
        clickmode='event+select'
    )
    
    # Financial impact graph
    financial_fig = go.Figure()
    financial_fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Revenue'], mode='lines+markers', name='Revenue', line=dict(color='green', width=2)))
    financial_fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Cost'], mode='lines+markers', name='Cost', line=dict(color='orange', width=2)))
    financial_fig.add_trace(go.Scatter(x=filtered_data['Date'], y=filtered_data['Profit'], mode='lines+markers', name='Profit', line=dict(color='purple', width=2)))
    
    financial_fig.update_layout(
        title='Financial Metrics Over Time',
        xaxis_title='Date',
        yaxis_title='Amount',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        hovermode='x unified',
        clickmode='event+select'
    )
    
    # Update summary table data
    table_data = filtered_data.to_dict('records')
    
    return inventory_fig, financial_fig, table_data

# Drill-down callback
@app.callback(
    Output('drilldown-output', 'children'),
    [Input('inventory-graph', 'clickData'),
     Input('financial-graph', 'clickData')],
    [State('product-dropdown', 'value')]
)
def drilldown_details(inventory_click, financial_click, selected_product):
    # Initialize the output string
    details = ""
    
    if inventory_click:
        point_date = inventory_click['points'][0]['x']
        point_metric = inventory_click['points'][0]['y']
        details += f"Inventory Data for {selected_product} on {point_date}: {point_metric} units\n"
        
    if financial_click:
        point_date = financial_click['points'][0]['x']
        point_metric = financial_click['points'][0]['y']
        details += f"Financial Data for {selected_product} on {point_date}: {point_metric} amount\n"
    
    if not details:
        details = "Click on a data point in the graphs above to see detailed information here."
    
    return html.Pre(details)

# Run the app
if __name__ == '__main__':
    app.run(debug=True,port=5017)

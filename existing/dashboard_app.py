
from flask import Flask, render_template
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from SalesOperationsDashboard import SalesOperationsDashboard
import plotly.graph_objs as go
from dash import dash_table
import pandas as pd
# Initialize Flask server for the dashboard
dashboard_server = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=dashboard_server, external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname='/dash/')

# Use the SalesOperationsDashboard class
data_path = 'mnt/data/AmazonSaleReport.csv'
df = pd.read_csv(data_path, encoding='ISO-8859-1')
sales_dashboard = SalesOperationsDashboard(data_path)
summary_df_extended = df.groupby(['Category', 'Fulfilment', 'Sales Channel ', 'ship-service-level', 'Status']).agg({
    'Order ID': 'count',               # Number of orders
    'Amount': 'sum',                   # Total amount (could represent "Actual")
}).reset_index()

# Simulate "PY Actual" as 95% of "Actual" sales (this is a placeholder logic)
summary_df_extended['PY Actual'] = summary_df_extended['Amount'] * 0.95

# Calculate "CY vs PY" as the difference
summary_df_extended['CY vs PY'] = summary_df_extended['Amount'] - summary_df_extended['PY Actual']
# Layout of the dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('AI Demand Plans'), className="mb-2")
    ]),
       dbc.Col(dbc.Row([
        dash_table.DataTable(
            id='summary-table',
            columns=[
                {"name": "Category", "id": "Category", "type": "text"},
                {"name": "Fulfilment", "id": "Fulfilment", "type": "text"},
                {"name": "Sales Channel", "id": "Sales Channel ", "type": "text"},
                {"name": "Ship Service Level", "id": "ship-service-level", "type": "text"},
                {"name": "Status", "id": "Status", "type": "text"},
                {"name": "Order ID", "id": "Order ID", "type": "numeric"},
                {"name": "Amount", "id": "Amount", "type": "numeric"},
                {"name": "PY Actual", "id": "PY Actual", "type": "numeric"},
                {"name": "CY vs PY", "id": "CY vs PY", "type": "numeric"},
            ],
            data=summary_df_extended.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'center',  # Center align all text
                'padding': '5px',
                'minWidth': '100px', 'width': '150px', 'maxWidth': '200px',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'border': '1px solid black',
            },
            style_data={
                'border': '1px solid grey',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'CY vs PY', 'filter_query': '{CY vs PY} < 0'},
                    'color': 'red',
                    'fontWeight': 'bold',
                },
                {
                    'if': {'column_id': 'CY vs PY', 'filter_query': '{CY vs PY} >= 0'},
                    'color': 'green',
                    'fontWeight': 'bold',
                }
            ],
            page_size=10,
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in summary_df_extended.to_dict('records')
            ],
            tooltip_duration=None  # Keep tooltips visible
        )
    ])),
    dbc.Row([
       # dbc.Col(html.Div([
           # html.H2('Demand Plan'),
           # html.P("IBM democratizes machine learning and deep learning to accelerate the infusion of AI in organizations to drive innovation. It empowers users to operationalize AI and optimize decisions based on historical data and external factors to increase forecast accuracy and produce consistent plans."),
           # html.P("The combination of predictive analytics using Watson Studio and Planning Analytics delivers trust into the process around where and how the values were generated."),
           # dbc.Button("Data Spreading", color="primary", className="mt-2")
        #]), width=3, className="bg-light p-3"),
      
        dbc.Col(html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='retailer-dropdown',
                    options=[
                        {'label': 'All Retailer', 'value': 'all'},
                        {'label': 'Retailer 1', 'value': 'retailer1'},
                        {'label': 'Retailer 2', 'value': 'retailer2'},
                        # Add more retailers as needed
                    ],
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='category-dropdown',
                    options=[
                        {'label': 'All Category', 'value': 'all'},
                        {'label': 'Set', 'value': 'Set'},
                        {'label': 'Blouse', 'value': 'Blouse'},
                        {'label': 'Western Dress', 'value': 'Western Dress'},
                        # Add more categories as needed
                    ],
                    value='all',
                    clearable=False,
                    style={'width': '100%'}
                ), width=6)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(dbc.Input(id='adjustment-input', type='number', placeholder='Adjustment %', className="mr-1")),
                dbc.Col(dbc.Button("Adjust Forecast", id='adjust-forecast', color="primary", className="mr-1")),
                dbc.Col(dbc.Button("Run AI Predictive Forecast Baseline", id='predict-forecast', color="primary", className="mr-1")),
                dbc.Col(dbc.Button("Run AI Forecast Promotional Uplift", id='predict-uplift', color="secondary", className="mr-1")),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='sales-forecast-graph'), width=12)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='uplift-graph'), width=6),
                dbc.Col(dcc.Graph(id='sales-breakdown-graph'), width=6)
            ]),
            dbc.Row([
                dbc.Col(html.Div(id='data-spreading'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('AI Trend Analysis'), className="mt-4"),
                dbc.Col(dcc.Graph(id='trend-analysis-graph'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('AI Recommendations'), className="mt-4"),
                dbc.Col(html.Div(id='ai-recommendations'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('Category Sales Distribution'), className="mt-4"),
                dbc.Col(dcc.Graph(id='category-sales-distribution'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('Sales Over Time'), className="mt-4"),
                dbc.Col(dcc.Graph(id='sales-over-time'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('Top Products by Sales'), className="mt-4"),
                dbc.Col(dcc.Graph(id='top-products-by-sales'), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.H4('Sales by Region'), className="mt-4"),
                dbc.Col(dcc.Graph(id='sales-by-region'), width=12)
            ]),
        ]), width=9),
        
    dbc.Row([
        html.Div(id='click-data')
    ])
    ])
], fluid=True)

@app.callback(
    Output('sales-forecast-graph', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value'),
    Input('adjust-forecast', 'n_clicks'),
    State('adjustment-input', 'value')
)
def update_graph(selected_category, selected_retailer, n_clicks, adjustment_percent):
    fig = sales_dashboard.create_forecast_figure(selected_category=selected_category, adjustment_percent=adjustment_percent)
    return fig

@app.callback(
    Output('uplift-graph', 'figure'),
    Input('predict-uplift', 'n_clicks')
)
def update_uplift_graph(n_clicks_uplift):
    if n_clicks_uplift:
        uplift_fig = sales_dashboard.create_uplift_figure()
        return uplift_fig
    return dash.no_update

@app.callback(
    Output('sales-breakdown-graph', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value')
)
def update_sales_breakdown_graph(selected_category, selected_retailer):
    sales_breakdown_fig = sales_dashboard.create_sales_breakdown_figure()
    return sales_breakdown_fig

@app.callback(
    Output('data-spreading', 'children'),
    Input('predict-forecast', 'n_clicks'),
    Input('predict-uplift', 'n_clicks')
)
def run_ai_predictions(n_clicks_forecast, n_clicks_uplift):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'No AI predictions run yet.'
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'predict-forecast':
        return 'AI Predictive Forecast Baseline has been run.'
    elif button_id == 'predict-uplift':
        uplift_data = sales_dashboard.run_uplift_prediction()
        return format_uplift_data(uplift_data)

def format_uplift_data(data):
    if isinstance(data, str):
        return data
    
    top_categories = data.groupby('Category')['Uplift'].sum().sort_values(ascending=False).head(10)
    uplift_summary = html.Div([
        html.H4('Top Categories by Uplift'),
        html.Ul([html.Li(f"{category}: {uplift:.2f}") for category, uplift in top_categories.items()])
    ])
    
    return uplift_summary

@app.callback(
    Output('trend-analysis-graph', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value')
)
def update_trend_analysis(selected_category, selected_retailer):
    trend_fig = sales_dashboard.create_trend_analysis_figure(selected_category, selected_retailer)
    return trend_fig

@app.callback(
    Output('ai-recommendations', 'children'),
    Input('predict-forecast', 'n_clicks'),
    Input('predict-uplift', 'n_clicks')
)
def generate_ai_recommendations(n_clicks_forecast, n_clicks_uplift):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'No AI recommendations yet.'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    recommendations =    recommendations = []
    
    if button_id == 'predict-forecast':
        recommendations.append("Based on the predictive forecast, consider increasing inventory for categories with high forecasted demand.")
    
    if button_id == 'predict-uplift':
        recommendations.append("Promotional uplift suggests running targeted promotions for categories with high uplift potential.")
    
    return html.Ul([html.Li(rec) for rec in recommendations])

@app.callback(
    Output('category-sales-distribution', 'figure'),
    Input('category-dropdown', 'value')
)
def update_category_sales_distribution(selected_category):
    distribution_fig = sales_dashboard.create_category_sales_distribution_figure(selected_category)
    return distribution_fig

@app.callback(
    Output('sales-over-time', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value')
)
def update_sales_over_time(selected_category, selected_retailer):
    sales_over_time_fig = sales_dashboard.create_sales_over_time_figure(selected_category, selected_retailer)
    return sales_over_time_fig

@app.callback(
    Output('top-products-by-sales', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value')
)
def update_top_products_by_sales(selected_category, selected_retailer):
    top_products_fig = sales_dashboard.create_top_products_by_sales_figure(selected_category, selected_retailer)
    return top_products_fig

@app.callback(
    Output('sales-by-region', 'figure'),
    Input('category-dropdown', 'value'),
    Input('retailer-dropdown', 'value')
)
def update_sales_by_region(selected_category, selected_retailer):
    sales_by_region_fig = sales_dashboard.create_sales_by_region_figure(selected_category, selected_retailer)
    return sales_by_region_fig

@dashboard_server.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
# Update the bar chart based on the selected category
@app.callback(
    Output('category-sales-bar-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_bar_chart(selected_category):
    filtered_data = sales_dashboard[sales_dashboard['Category'] == selected_category]
    fig = {
        'data': [
            go.Bar(
                x=filtered_data['SKU'],
                y=filtered_data['Amount'],
                marker={'color': 'blue'}
            )
        ],
        'layout': go.Layout(
            title=f'Sales for {selected_category}',
            xaxis={'title': 'SKU'},
            yaxis={'title': 'Total Sales Amount'},
            barmode='group'
        )
    }
    return fig
@app.callback(
    Output('click-data', 'children'),
    Input('table', 'active_cell'),
    State('table', 'data')
)
def display_click_data(active_cell, data):
    if active_cell:
        row = active_cell['row']
        col = active_cell['column_id']
        value = data[row][col]
        return f"You clicked on value: {value} in column: {col}"
    return "Click on a table cell to see the value"
if __name__ == '__main__':
    dashboard_server.run(debug=True, port=5014)




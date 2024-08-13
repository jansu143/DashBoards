from dash import dcc, html, dash_table, Dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

# Placeholder financial data, replace with actual data
financial_data = {
    "Category": ["Sales", "Cost of sales", "Gross margin", "Net income"],
    "Q1": [1.03, 0.75, 0.28, 0.10],
    "Q2": [1.24, 0.85, 0.39, 0.20],
    "Q3": [1.52, 0.90, 0.62, 0.30],
    "Q4": [1.85, 1.05, 0.80, 0.60],
    "Total Year": [5.64, 3.55, 2.09, 1.20]
}

df_financial = pd.DataFrame(financial_data)

def create_financial_dashboard():
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1('Financial Impact Dashboard', className='text-center text-primary mb-4'), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='financial-metrics-graph', figure=create_financial_metrics_figure()), width=4),
            dbc.Col(dcc.Graph(id='sales-bar-graph', figure=create_sales_bar_figure()), width=4),
            dbc.Col(dcc.Graph(id='net-income-line-graph', figure=create_net_income_line_figure()), width=4)
        ]),
        dbc.Row([
            dbc.Col(html.H5('Financial Details', className='text-center mt-4'), width=12),
            dbc.Col(dash_table.DataTable(
                id='financial-table',
                columns=[{"name": i, "id": i} for i in df_financial.columns],
                data=df_financial.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center'},
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
            ), width=12)
        ])
    ], fluid=True)

def create_financial_metrics_figure():
    metrics = {
        "Sales": 5.67,
        "Gross Margin": 2.89,
        "Net Income": 1.20
    }
    return {
        'data': [
            go.Indicator(
                mode="number",
                value=metrics["Sales"],
                title={"text": "Sales"},
                domain={'x': [0, 0.33], 'y': [0, 1]}
            ),
            go.Indicator(
                mode="number",
                value=metrics["Gross Margin"],
                title={"text": "Gross Margin"},
                domain={'x': [0.33, 0.66], 'y': [0, 1]}
            ),
            go.Indicator(
                mode="number",
                value=metrics["Net Income"],
                title={"text": "Net Income"},
                domain={'x': [0.66, 1], 'y': [0, 1]}
            )
        ],
        'layout': go.Layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
    }

def create_sales_bar_figure():
    return {
        'data': [
            go.Bar(
                x=['Q1', 'Q2', 'Q3', 'Q4'],
                y=[1.03, 1.24, 1.52, 1.85],
                name="Sales"
            )
        ],
        'layout': go.Layout(
            title="Sales by Quarter",
            barmode='group',
            height=250
        )
    }

def create_net_income_line_figure():
    return {
        'data': [
            go.Scatter(
                x=['Q1', 'Q2', 'Q3', 'Q4'],
                y=[0.10, 0.20, 0.30, 0.60],
                mode='lines+markers',
                name='Net Income'
            )
        ],
        'layout': go.Layout(
            title="Net Income Trend",
            height=250
        )
    }

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set the layout to the financial dashboard
app.layout = create_financial_dashboard()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

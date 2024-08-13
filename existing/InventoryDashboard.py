import pandas as pd
import plotly.express as px

class InventoryDashboard:
    def __init__(self, data_path, encoding='ISO-8859-1'):
        self.data_path = data_path
        self.encoding = encoding
        self.data = self.load_data()

    def load_data(self):
        try:
            data = pd.read_csv(self.data_path, encoding=self.encoding)
            return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None

    def create_inventory_measures_figure(self, selected_region='all', selected_product='all'):
        if self.data is None:
            return None
        
        df = self.data
        if selected_region != 'all':
            df = df[df['Region'] == selected_region]
        if selected_product != 'all':
            df = df[df['Product'] == selected_product]
        
        fig = px.bar(df, x='Date', y='Inventory Quantity', color='Region', barmode='group')
        fig.update_layout(title='Inventory Measures by Region')
        return fig

    def create_inventory_trend_figure(self, selected_region='all', selected_product='all'):
        if self.data is None:
            return None
        
        df = self.data
        if selected_region != 'all':
            df = df[df['Region'] == selected_region]
        if selected_product != 'all':
            df = df[df['Product'] == selected_product]
        
        fig = px.line(df, x='Date', y='Inventory Quantity', color='Region')
        fig.update_layout(title='Inventory Trends Over Time')
        return fig

    def run_inventory_optimization(self):
        if self.data is None:
            return "No data available for optimization."
        
        # Placeholder for optimization logic
        optimization_results = {
            "Optimal Inventory Level": 10000,
            "Total Cost": 50000,
            "Regions to Focus": ["USA", "East"]
        }
        return optimization_results

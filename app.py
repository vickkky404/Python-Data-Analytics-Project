import dash
from dash import dcc, html, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime as dt
import base64
import io


app = dash.Dash(__name__)
server = app.server  


app.layout = html.Div([
    html.H1("Sales Data Analysis Dashboard ", style={'textAlign': 'center'}),
    html.H1("PYTHON Data Analysis project ", style={'textAlign': 'center'}),

   
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag & Drop or ', html.A('Select CSV/Excel File')]),
        style={
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'padding': '20px',
            'margin': '10px'
        },
        multiple=False
    ),

    
    html.Div([
        dcc.Dropdown(
            id='region-filter',
            options=[],
            placeholder="Select Region",
            multi=True,
            style={'width': '48%', 'margin': '10px'}
        ),
        dcc.Dropdown(
            id='category-filter',
            options=[],
            placeholder="Select Category",
            multi=True,
            style={'width': '48%', 'margin': '10px'}
        ),
        dcc.DatePickerRange(
            id='date-range',
            start_date=dt(2023, 1, 1),
            end_date=dt(2023, 12, 31),
            style={'margin': '10px'}
        )
    ], style={'display': 'flex', 'flex-wrap': 'wrap'}),

    
    html.Div([
        dcc.Graph(id='sales-trend', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='top-products', style={'width': '49%', 'display': 'inline-block'})
    ]),
    html.Div([
        dcc.Graph(id='region-pie', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='category-heatmap', style={'width': '49%', 'display': 'inline-block'})
    ]),

    
    html.Div(id='output-data-upload', style={'display': 'none'}),

    html.H1("Made by = Nalinikant Bastia(23014100001)"),
])



@callback(
    Output('output-data-upload', 'children'),
    Output('region-filter', 'options'),
    Output('category-filter', 'options'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data(contents, filename):
    if contents is None:
        return dash.no_update, [], []  
    
    try:
      
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
       
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return dash.no_update, [], []  
        
      s
        required_columns = ['Date', 'Region', 'Product', 'Sales', 'Category']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV missing required columns!")
        
       
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle invalid dates
        df.dropna(subset=['Date', 'Region', 'Category'], inplace=True)  # Remove bad rows
        
       
        regions = [{'label': i, 'value': i} for i in df['Region'].unique()]
        categories = [{'label': i, 'value': i} for i in df['Category'].unique()]
        
        return df.to_json(date_format='iso'), regions, categories
    
    except Exception as e:
        print(f"Error: {e}")
        return dash.no_update, [], []  

  
    df['Date'] = pd.to_datetime(df['Date'])

    
    regions = [{'label': i, 'value': i} for i in df['Region'].unique()]
    categories = [{'label': i, 'value': i} for i in df['Category'].unique()]

    return df.to_json(date_format='iso'), regions, categories



@callback(
    Output('sales-trend', 'figure'),
    Output('top-products', 'figure'),
    Output('region-pie', 'figure'),
    Output('category-heatmap', 'figure'),
    Input('output-data-upload', 'children'),
    Input('region-filter', 'value'),
    Input('category-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_graphs(json_data, selected_regions, selected_categories, start_date, end_date):
    if json_data is None:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df = pd.read_json(json_data)
    df['Date'] = pd.to_datetime(df['Date'])

   
    filtered_df = df[
        (df['Region'].isin(selected_regions if selected_regions else df['Region'].unique())) &
        (df['Category'].isin(selected_categories if selected_categories else df['Category'].unique())) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
        ]

    
    trend_df = filtered_df.groupby(pd.Grouper(key='Date', freq='M'))['Sales'].sum().reset_index()
    trend_fig = px.line(trend_df, x='Date', y='Sales', title='Monthly Sales Trend')

   
    top_products = filtered_df.groupby('Product')['Sales'].sum().nlargest(10).reset_index()
    product_fig = px.bar(top_products, x='Product', y='Sales', title='Top 10 Products by Sales')

    # Pie Chart: Sales by Region
    region_fig = px.pie(filtered_df, names='Region', values='Sales', title='Sales Distribution by Region')

    # Heatmap: Sales by Category and Region
    heatmap_df = filtered_df.pivot_table(values='Sales', index='Region', columns='Category', aggfunc='sum')
    heatmap_fig = px.imshow(
        heatmap_df,
        labels=dict(x="Category", y="Region", color="Sales"),
        title="Sales Heatmap (Region vs Category)"
    )

    return trend_fig, product_fig, region_fig, heatmap_fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)

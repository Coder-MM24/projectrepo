# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

#TASK 1: Add a Launch Site Drop-down Input Component
# Define the dropdown component
dropdown = dcc.Dropdown(
    id='site-dropdown',  
    options=[
        {'label': 'All Sites', 'value': 'ALL'},  
        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'}, 
        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},  
    ],
    value='ALL',  # Default value to be selected
    placeholder="Select a Launch Site here",  # Placeholder text for the dropdown
    searchable=True  # Enable search functionality within the dropdown
)

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by 'Launch Site' and count the number of successful launches
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        fig = px.pie(
            values=success_counts,
            names=success_counts.index,
            title='Total Success Launches by Site',
            labels={site: site for site in success_counts.index}
        )
    else:
        # Filter the dataframe to include data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Calculate value counts for successes and failures
        success_fail_counts = filtered_df['class'].value_counts().reindex([0, 1], fill_value=0)
        # Render the pie chart for the selected site
        fig = px.pie(
            values=success_fail_counts,
            names=success_fail_counts.index.map({0: 'Failure', 1: 'Success'}),
            title=f'Total Success and Failure Launches for site {selected_site}',
            labels={0: 'Failure', 1: 'Success'}
        )
    fig.update_traces(textinfo='label+percent', insidetextorientation='radial')
    
    return fig

#TASK 3: Add a Range Slider to Select Payload
# Define the range slider component
range_slider = dcc.RangeSlider(
    id='payload-slider',  # Unique identifier for the RangeSlider component
    min=0,  # Slider starting point (Kg)
    max=10000,  # Slider ending point (Kg)
    step=1000,  # Slider interval (Kg)
    marks={0: '0', 10000: '10000'},  # Marks on the slider
    value=[0, 10000]  # Current selected range
)

# Define the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dropdown,  # Include the dropdown component here
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    range_slider,
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    if selected_site == 'ALL':
        # Render scatter plot for all sites
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        # Filter dataframe for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        # Render scatter plot for the selected site
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for {selected_site}'
        )
    # Update x-axis tick format to display in '000s
    fig.update_layout(
        xaxis=dict(
            tickformat=',.0f'
        )
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()

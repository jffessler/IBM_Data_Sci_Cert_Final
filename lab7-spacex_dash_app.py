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

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                    'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    html.Div([
    dcc.Dropdown(id='site-dropdown', options=[
        {'label': 'All Sites', 'value': 'ALL'},
        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True)
    ]),
    html.Br(),
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(
        dcc.Graph(id='success-pie-chart')
    ),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    dcc.RangeSlider(id='payload-slider',
                min=0,
                max=10000, 
                step=1000,
                marks={i: f'{i}' for i in range(0, 10001, 1000)},
                value=[min_payload, max_payload]),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown',component_property='value'))

def pie_chart_vis(selected_site):
    site_df = spacex_df[['Launch Site','class']]
    if selected_site == "ALL":
        fig = px.pie(site_df,
                     values='class', 
                     names='Launch Site',
                     title='Successful Launches by Site')
        return fig
    elif selected_site != "ALL":
        site1_df = site_df[site_df["Launch Site"] == selected_site]
        size = len(site1_df)
        site1_df = site1_df.groupby('Launch Site').sum()
        site1_df.loc[1]=size-(site1_df['class'][0])
        site1_df = site1_df.reset_index()
        site1_df.rename(columns={"Launch Site":"Outcomes"}, inplace = True)
        site1_df.loc[[0],['Outcomes']] = 'Success'
        site1_df.loc[[1],['Outcomes']] = 'Failure'
        fig = px.pie(site1_df,
                     values='class', 
                     names='Outcomes',
                     title=f'Launch Results at {selected_site}')
        return fig
    else:
        return None

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown',component_property='value'),
               Input(component_id='payload-slider',component_property='value')])
def scatter_plot_vis(selected_site,selected_payload):
    scatter_df = spacex_df[["Launch Site","class","Payload Mass (kg)","Booster Version Category"]]
    scatterAll_df = scatter_df[(scatter_df['Payload Mass (kg)']>=selected_payload[0])&
                               (scatter_df['Payload Mass (kg)']<=selected_payload[1])]
    if selected_site == "ALL":
        fig = px.scatter(scatterAll_df,
                     x='Payload Mass (kg)', 
                     y='class',
                     title=f'Launch Success between {selected_payload[0]} and {selected_payload[1]} (kg)',
                     color='Booster Version Category')
        return fig
    elif selected_site != "ALL":
        scatterOther_df = scatterAll_df[scatterAll_df['Launch Site']==selected_site]
        fig = px.scatter(scatterOther_df,
                     x='Payload Mass (kg)', 
                     y='class',
                     title=f'Launch Success between {selected_payload[0]} and {selected_payload[1]} (kg) from the {selected_site} site',
                     color='Booster Version Category')
        return fig
    else:
        return None

# Run the app
if __name__ == '__main__':
    app.run_server()

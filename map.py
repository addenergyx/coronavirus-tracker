# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 16:26:10 2020

@author: david
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_daq as daq
from dash.dependencies import Input, Output

from server import server
import os

ts_confirmed= pd.read_csv('time_series_19-covid-Confirmed.csv')
ts_recovered= pd.read_csv('time_series_19-covid-Recovered.csv')
ts_death= pd.read_csv('time_series_19-covid-Deaths.csv')

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(name='map', server=server, url_base_pathname='/map/', external_stylesheets=external_stylesheets )

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF'
}

body = html.Div(
    [
       dbc.Row(
           [
               dbc.Col(
                  [
                     html.Div([
                         html.H2("Coronavirus Timeline Dashboard",style={'text-align':'center','padding':'3rem 3rem'}),
                         html.P("ad"),
                               dbc.Button("View details", color="secondary"),
                    ], style={'color': colors['text'],'padding':'3rem 3rem'}),
                  
                    ## DROPDOWN ROW
                    html.Div([
                        dbc.Row(
                            [
                                dbc.Col(dcc.Dropdown( 
                                id='nation',
                                options=nation_options,
                                value=['Worldwide'],
                                multi=True
                                #style=dropdown_style
                                )),
                                dbc.Col(dcc.Dropdown( 
                                    id='case',
                                    options=[{'label':i,'value':i} for i in df.columns[3:6] ],
                                    value='Confirmed',
                                    className='dropdown',
                                    searchable=False,
                                    #style=dropdown_style
                                )),
                            ]
                        )
                    ]),
                    
                    ],width=3),
              dbc.Col(
                  [
                      html.Div([
                        daq.ToggleSwitch(
                            id='my-toggle-switch',
                            value=False
                        ),
                        html.Div(id='toggle-switch-output')
                    ]),
                      
                      html.Div([
                          dcc.Graph(
                            id='corona-map',
                            #figure=fig,
                            style={'margin' : '0'}        
                          ),
                        ]),
                  ]
            )
       ],      
    )
  ])
    
def Homepage():
    layout = html.Div([
    #nav,
    body
    ], style={'backgroundColor': colors['background']})
    return layout

app.layout = Homepage()

@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               Input('exclude-china','value')])
def update_map(selected_nation, selected_case, click):
    #selected_nation='US'
    zoom = 3    
    
    filtered_df = df[df['Country/Region'].isin(selected_nation)] # Country Dropdown
    
    if 'Worldwide' in selected_nation or not selected_nation: # Case Dropdown
        filtered_df = df
        zoom = 2
    
    if not click:
        filtered_df = filtered_df[filtered_df['Country/Region'] != 'China'] # China Checkbox
    
    px.set_mapbox_access_token(mapbox_access_token)
        
    if selected_case == 'Deaths':
        #filtered_df = filtered_df[['Deaths','Latitude','Longitude','City/Country']]
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Deaths",
                      size_max=100, hover_name="City/Country",
                      hover_data=["Deaths"])
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    elif selected_case == 'Recovered':
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Recovered",
                      size_max=100, hover_name="City/Country",
                      hover_data=["Confirmed", "Recovered", "Deaths"] )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Green'))
    else:
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", color="Deaths", size="Confirmed",
                              #color_continuous_scale=px.colors.diverging.Picnic,
                              size_max=50, hover_name="City/Country",
                              hover_data=["Confirmed", "Recovered", "Deaths"] )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=2),showlegend=False)
    
    fig.update(
            layout=dict(title=dict(x=0.5), paper_bgcolor=colors['background'] )
        )
    
    fig.update_layout(
        autosize=True,
        height=750,
        #width=1500,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            style="dark",
            # center=dict(
            #     lat=56,
            #     lon=324
            # ),
            pitch=0,
            zoom=zoom
        ),
    )
    
    return fig


app.layout = Homepage()
if __name__ == "__main__":
    app.run_server()
    #app.run_server(debug=True, use_reloader=False)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 19:39:52 2020

@author: david
"""
from server import server
import pandas as pd
import numpy as np
import os

df = pd.read_csv('data.csv')
old_df = pd.read_csv('old_data.csv')
## Cleanup data

for index, row in df.iterrows():
      if row['Province/State'] == row['Country/Region'] or row['Province/State'] == 'UK':
          df['Province/State'][index] = None

city_country = np.array(df['Province/State'] + ", " + df['Country/Region'] )
df["City/Country"] = city_country
#df['Province/State'].fillna(df['Country/Region'], inplace=True)
df['City/Country'].fillna(df['Country/Region'], inplace=True)

total_deaths = df['Deaths'].sum(axis = 0, skipna = True)
total_recovered = df['Recovered'].sum(axis = 0, skipna = True)
total_cases = df['Confirmed'].sum(axis = 0, skipna = True)

old_total_deaths = df['Deaths'].sum(axis = 0, skipna = True)
old_total_recovered = df['Recovered'].sum(axis = 0, skipna = True)
old_total_cases = df['Confirmed'].sum(axis = 0, skipna = True)

## Change in stats
death_change = total_deaths - old_total_deaths
recovery_change = total_recovered - old_total_recovered
cases_change = total_cases - old_total_cases

import plotly.graph_objects as go
import dash_table

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

import plotly.express as px
# px.set_mapbox_access_token('pk.eyJ1IjoiYWRkeiIsImEiOiJjazdwOGRzd2swM2w1M2V0aHNqMHNxcnN2In0.TlOw891OF9vJQBY5KC_G7w')
# fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Deaths", size="Confirmed",
#                   color_continuous_scale=px.colors.diverging.Picnic, size_max=50, zoom=5, hover_name="City/Country",
#                   hover_data=["Confirmed", "Recovered", "Deaths"], title = 'COVID-19 Coronavirus Cases, Recoveries & Deaths' )
# #fig.show()

# fig.update_traces(hoverinfo='text', marker=dict(sizemin=2))

# fig.update(
#         layout=dict(title=dict(x=0.5), showlegend=False)
#     )

# fig.update_layout(
#     autosize=True,
#     height=750,
#     hovermode='closest',
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         bearing=0,
#         style="dark",
#         center=dict(
#             lat=55,
#             lon=-3
#         ),
#         pitch=0,
#         zoom=5
#     ),
# )

#from plotly.offline import plot
#plot(fig, auto_open=True)
from newsapi import NewsApiClient

def update_news():
    # Init
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    
    # /v2/top-headlines
    top_headlines = newsapi.get_top_headlines(q='Coronavirus',
                                              #sources='google-news',
                                              language='en',
                                              country='gb')
    
    articles = top_headlines['articles']
    
    titles = []
    urls = []
    for a in articles:
        titles.append(a['title'])
        urls.append(a['url'])
    
    d = {'Title':titles,'Url':urls}
    
    news_df = pd.DataFrame(d)

    return news_df

def generate_html_table(max_rows=5):
    news_df = update_news()

    return html.Div(
        [
            html.Div(
                html.Table(
                    # Header
                    [html.Tr([html.Th()])]
                    +
                    # Body
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.A(
                                        news_df.iloc[i]["Title"],
                                        href=news_df.iloc[i]["Url"],
                                        target="_blank"
                                    )
                                )
                            ]
                        )
                        for i in range(min(len(news_df),max_rows))
                    ]
                ),
                style={"height": "300px", "overflowY": "scroll"},
            ),
        ],
        style={"height": "100%"},)




import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(name='tracker', server=server, url_base_pathname='/tracker/')

#Bootstrap CSS
app.css.append_css({
    "external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"
})  

app.title = 'Coranavirus Tracker'

nation_options = []
nations = df['Country/Region'].unique()
for nation in df['Country/Region'].unique():
    nation_options.append({'label':str(nation), 'value': nation})
nation_options.append({'label':'Worldwide', 'value': 'Worldwide'})
    
app.layout = html.Div(children=[
    html.H1(children='Coronavirus (COVID-19) Global Tracker', style={'textAlign':'center'}),
    
    html.Div([
        html.H2('Total Confirmed: {}'.format(total_cases), style={'color':'blue', 'display':'inline-block', 'width': '33%', 'textAlign':'center'}),
        html.H2('Total Deaths: {}'.format(total_deaths), style={'color':'red', 'display':'inline-block', 'width': '33%', 'textAlign':'center'}),
        html.H2('Total Recovered: {}'.format(total_recovered), style={'color':'green', 'display':'inline-block', 'width': '33%', 'textAlign':'center'})
        # Add past 24hr changes
    ]),
    
    html.Div([    
        dcc.Dropdown( 
            id='nation',
            options=nation_options,
            value='Worldwide',
            #multi=True
        ),  
    ], style={'width': '50%', 'display':'inline-block'}),
  
    html.Div([    
        dcc.Dropdown( 
            id='case',
            options=[{'label':i,'value':i} for i in df.columns[3:6] ],
            value='Confirmed',
        ),  
    ], style={'width': '50%', 'display':'inline-block'}),
    
    
    html.Div([
        dcc.Checklist(id='exclude-china', 
                       options=[{'label':'Include China','value':1}],
                       value=[1])    
    ]),
    #html.Div(id='exclude-china-output'),
    
        html.Div([   
            dcc.Graph(
                id='corona-map',
                #figure=fig,
                style={'margin' : '0'}        
            ),
        ]),
        
        html.Div([ 
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                ],
                data=df.to_dict('records'),
                hidden_columns = ["Latitude","Longitude",'City/Country'],
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current= 0,
                page_size= 20,
            ),
        ]),
    
    html.Div([
        html.H3("Coronavirus News"),
        generate_html_table()
    ], className="six columns"),
    
    #html.Div(id='datatable-interactivity-container')
  ])

@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               Input('exclude-china','value')])
def update_map(selected_nation, selected_case, click):
    #selected_nation='US'
    zoom = 3
    
    filtered_df = df[df['Country/Region']==selected_nation] # Country Dropdown
    
    if selected_nation == 'Worldwide' or selected_nation == None: # Case Dropdown
        filtered_df = df
        zoom = 2
    
    if not click:
        filtered_df = filtered_df[filtered_df['Country/Region'] != 'China'] # China Checkbox
    
    px.set_mapbox_access_token('pk.eyJ1IjoiYWRkeiIsImEiOiJjazdwOGRzd2swM2w1M2V0aHNqMHNxcnN2In0.TlOw891OF9vJQBY5KC_G7w')
        
    if selected_case == 'Deaths':
        #filtered_df = filtered_df[['Deaths','Latitude','Longitude','City/Country']]
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Deaths",
                      size_max=100, hover_name="City/Country",
                      hover_data=["Deaths"], title = 'COVID-19 Coronavirus Cases, Recoveries & Deaths' )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    elif selected_case == 'Recovered':
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Recovered",
                      size_max=100, hover_name="City/Country",
                      hover_data=["Confirmed", "Recovered", "Deaths"], title = 'COVID-19 Coronavirus Cases, Recoveries & Deaths' )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Green'))
    else:
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", color="Deaths", size="Confirmed",
                              #color_continuous_scale=px.colors.diverging.Picnic,
                              size_max=50, hover_name="City/Country",
                              hover_data=["Confirmed", "Recovered", "Deaths"], title = 'COVID-19 Coronavirus Cases, Recoveries & Deaths' )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=2))
    
    fig.update(
            layout=dict(title=dict(x=0.5), showlegend=False)
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


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
    #app.run_server()



































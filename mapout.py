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
import numpy as np
from components import NationsDropdown, CasesDropdown, Navbar, Footer, Banner, Info
from dataset import get_jhu_dataset, get_recovery_frame, getMarks, clean_data, unix_to_date, getTimeScaleUnix, get_data_from_postgres, getTimeScale, get_animation_frame, get_animation_from_postgres

import plotly.express as px
from newsapi import NewsApiClient

from server import server
import os

import time
import datetime

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

#ts_confirmed, ts_death = get_jhu_dataset() 
ts_confirmed, ts_death, ts_recovered = get_data_from_postgres()

# ts_confirmed= pd.read_csv('time_series_covid19_confirmed_global.csv')
# ts_death= pd.read_csv('time_series_covid19_deaths_global.csv') 

# ts_recovered = get_recovery_frame(ts_confirmed, ts_death)   

clean_data(ts_confirmed)
clean_data(ts_death)
# clean_data(ts_recovered)

def update_news():
    # Init
    newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
    
    # /v2/top-headlines
    top_headlines = newsapi.get_top_headlines(q='Coronavirus',
                                              #sources='google-news',
                                              language='en',
                                              #country='gb'
                                              )
    
    articles = top_headlines['articles']
    
    titles = []
    urls = []
    for a in articles:
        titles.append(a['title'])
        urls.append(a['url'])
    
    d = {'Title':titles,'Url':urls}
    
    news_df = pd.DataFrame(d)

    return news_df

def generate_html_table(max_rows=10):
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

time_scale = ts_confirmed.columns[4:-1]
time_scale_unix = [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in time_scale]

external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

app = dash.Dash(name='map', server=server, url_base_pathname='/map/', external_stylesheets=external_stylesheets, 
                meta_tags=[
                    #{ 'name':'viewport','content':'width=device-width, initial-scale=1' },## Fixes media query not showing
                    {
                        'name': 'description',
                        'content': 'This dashboard is designed to monitor events, deaths, and recoveries reported by serveral sources such as WHO and Johns Hopkins University on the n-Cov (Coronavirus). This constantly searches repositories and reviews all countries case studies.'
                    },
                ] 
            )

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-146361977-3"></script>
        
        <script type='text/javascript' src='https://platform-api.sharethis.com/js/sharethis.js#property=5e849281c43e3f0019117eac&product=inline-share-buttons' async='async'></script>
        
        <script async src="https://platform-api.sharethis.com/js/sharethis.js#property=5e849281c43e3f0019117eac&product=sticky-share-buttons"></script>
        
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
        
          gtag('config', 'UA-146361977-3');
        </script>
        <script data-ad-client="ca-pub-7702690633531029" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <script data-name="BMC-Widget" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="addenergyx" data-description="Support me on Buy me a coffee!" 
        data-message="Thank you for visiting. Please support this project" data-color="#FF813F" data-position="right" data-x_margin="18" data-y_margin="18"></script>
        {%css%}
        {%favicon%}
    </head>
    <body>
        <div></div>
        {%app_entry%}
        <footer> 
          {%config%} 
          {%scripts%} 
          {%renderer%}
        </footer>
    </body>
</html>
'''

app.title = 'Time-laspe Map'

app.config.suppress_callback_exceptions = True

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF',
    'secondary':'#2B2B2B'
}

body = html.Div(
    [
       dbc.Row(
           [
               ## Side Panel
               dbc.Col(
                  [
                     html.Div([
                         html.H2("Coronavirus Timeline Dashboard",style={'text-align':'center', 'padding-bottom':'20px', 'padding-top':'40px'}),
                    ], style={'color': '#0275d8'}),
                    
                    html.Div([
                        html.Div([NationsDropdown(ts_confirmed)]),
                        
                        html.Div([CasesDropdown()]),
                        
                        # html.Div([
                        #     dcc.Slider(
                        #         id='time-frame',
                        #         min = getTimeScaleUnix()[0],
                        #         max = getTimeScaleUnix()[-1],
                        #         value = getTimeScaleUnix()[-1],
                        #         #updatemode='drag',
                        #         #tooltip = { 'always_visible': True },
                        #         marks=getMarks(12),
                        #         step=1,
                        #     ),
                        # ]),
                        
                        html.Div([
                            html.H3("Global Coronavirus News", style={'color': colors['text'], 'text-align':'center'}),
                            generate_html_table()
                        ],style={'padding-bottom':'20px','padding-top':'20px'}),
                        ], style={'padding-right':'20px','padding-left':'20px'}),
                    ], width=12,lg=3, className='card', style={'backgroundColor': colors['secondary'],'padding-top':'80px'} ),
              
              ## Main panel
              dbc.Col(
                  [
                      # dbc.Col([
                      #     html.Div([
                      #       daq.ToggleSwitch(
                      #           id='exclude-china',
                      #           value=True,
                      #           label=['Excluding China', 'Including China'],
                      #           color='#0275d8',
                      #           style={
                      #               'color': 'white'
                      #           }
                      #       ),
                      #    ]),
                      # ], width={"size": 2, "offset":9}),
                      dcc.Loading(
                          children=[
                              html.Div([
                                  dcc.Graph(
                                    id='corona-map',
                                    #figure=fig,
                                    style={'margin' : '0'},
                                  ),
                             ])
                         ], type='circle',
                      )
                  ],style={'padding-top':'80px'}, width=12, lg=9
            )
       ]),
       
  ])
    
def Homepage():
    layout = html.Div([
        Navbar(),
        body,
        Info(),
        Footer(),
        Banner()
    ], style={'backgroundColor': colors['background'], 'overflow-x': 'hidden', 'height':'100%'})
    return layout

# @app.callback(Output('time-frame','value'), [Input('time-lapse','n_intervals')])
# def update_slider(n):
    
#     counter = 0
    
#     counter += n
    
#     return counter


@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               #Input('exclude-china','value'), Input('time-frame','value')
                                              ])
def update_map(selected_nation, selected_case):
    
    ## For testing
    # unix_date=1584071771
    # selected_nation=['Worldwide']
    
    df = get_animation_from_postgres()
    
    px.set_mapbox_access_token(mapbox_access_token)

    #date = unix_to_date(unix_date)
        
    #zoom = 3    
    
    ## Country Dropdown
    if 'Worldwide' in selected_nation or not selected_nation: 
        filtered_df = df
        # filtered_ts_confirmed = ts_confirmed
        # filtered_ts_death = ts_death
        # filtered_ts_recovered = ts_recovered
        zoom = 2
    else:
        filtered_df = df[df['country'].isin(selected_nation)] 
        # filtered_ts_confirmed = ts_confirmed[ts_confirmed['Country/Region'].isin(selected_nation)]
        # filtered_ts_death = ts_death[ts_death['Country/Region'].isin(selected_nation)]
        # filtered_ts_recovered = ts_recovered[ts_recovered['Country/Region'].isin(selected_nation)]
    
    ## China Checkbox
    # if not click: 
        #filtered_df = filtered_df[filtered_df['Country/Region'] != 'China'] 
        # filtered_ts_confirmed = filtered_ts_confirmed[filtered_ts_confirmed['Country/Region'] != 'China']
        # filtered_ts_death = filtered_ts_death[filtered_ts_death['Country/Region'] != 'China']
        # filtered_ts_recovered = filtered_ts_recovered[filtered_ts_recovered['Country/Region'] != 'China']
    
        
    ## Rename columns to prettify hover data
    # temp_deaths_df = filtered_ts_death.rename(columns = {date:'Deaths', 'Lat':'Latitude', 'Long':'Longitude'})
    # temp_recovered_df = filtered_ts_recovered.rename(columns = {date:'Active/Recovered', 'Lat':'Latitude', 'Long':'Longitude'})
    # temp_confirmed_df = filtered_ts_confirmed.rename(columns = {date:'Confirmed', 'Lat':'Latitude', 'Long':'Longitude'})
    
    # #Some data from JHU appears as -1 unsure why
    # temp_recovered_df[temp_recovered_df['Active/Recovered'] < 0] = 0
    # temp_confirmed_df[temp_confirmed_df['Confirmed'] < 0] = 0
    # temp_deaths_df[temp_deaths_df['Deaths'] < 0] = 0
    
    # #assumes order of countries from datasets are the same
    # temp_all = temp_confirmed_df[['City/Country', 'Confirmed','Latitude','Longitude']]
    # temp_all.insert(2,'Deaths', temp_deaths_df[['Deaths']])
    # temp_all.insert(2,'Active/Recovered',temp_recovered_df[['Active/Recovered']])
    
    if selected_case == 'Deaths':
        fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", size='deaths', size_max=50, hover_name="country",
                                animation_group='country', animation_frame="date")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    elif selected_case == 'Recovered':
        fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", size="recovered",
                      size_max=50, hover_name="country",animation_group='country', animation_frame="date")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Green'))
    elif selected_case == 'Confirmed':
        fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", size="confirmed",
                      size_max=50, hover_name="country",animation_group='country', animation_frame="date")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Blue'))
    else:
        fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="confirmed", color='deaths',
                              size_max=50, hover_name="country",
                              hover_data=["confirmed", "recovered", "deaths"],
                              animation_group='country',
                              animation_frame="date"
                              )
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=2))
    
    fig.update(
            layout=dict(title=dict(x=0.5), paper_bgcolor=colors['background'] ),
        )
    
    fig.update_layout(
        autosize=True,
        height=750,
        #width=1500,
        font={
            'family': 'Courier New, monospace',
            'size': 18,
            'color': 'white'
        },
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            style="dark",
            pitch=0,
            zoom=1
        ),
    )
    
    return fig

app.layout = Homepage()

if __name__ == "__main__":
    #app.run_server()
    app.run_server(debug=True, use_reloader=False)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 19:39:52 2020

@author: david
"""
from server import server
import pandas as pd
import numpy as np
import os
from navbar import Navbar
#Data files
# df = pd.read_csv('data.csv')
# old_df = pd.read_csv('old_data.csv')
ts_confirmed= pd.read_csv('time_series_19-covid-Confirmed.csv')
ts_recovered= pd.read_csv('time_series_19-covid-Recovered.csv')
ts_death= pd.read_csv('time_series_19-covid-Deaths.csv')

def clean_data(frame):
    for index, row in frame.iterrows():
      if row['Province/State'] == row['Country/Region'] or row['Province/State'] == 'UK':
          frame['Province/State'][index] = None
    
    city_country = np.array(frame['Province/State'] + ", " + frame['Country/Region'] )
    frame["City/Country"] = city_country
    #df['Province/State'].fillna(df['Country/Region'], inplace=True)
    frame['City/Country'].fillna(frame['Country/Region'], inplace=True)

clean_data(ts_confirmed)
clean_data(ts_death)
clean_data(ts_recovered)
#clean_data(df)

import time
import datetime
time_scale = ts_confirmed.columns[4:-1]
result = {}
'''
Dash does not support datetime objects by default.
You can solve this issue by converting your datetime object into an unix timestamp.
'''
time_scale_unix = [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in time_scale]

def getMarks(start, end, Nth=4):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    result = {}
    for i, date in enumerate(time_scale):
        if(i%Nth == 1):
            # Append value to dict
            result[time_scale_unix[i]] = time_scale[i]
    return result

# ## Cleanup data
# for index, row in df.iterrows():
#       if row['Province/State'] == row['Country/Region'] or row['Province/State'] == 'UK':
#           df['Province/State'][index] = None

# city_country = np.array(df['Province/State'] + ", " + df['Country/Region'] )
# df["City/Country"] = city_country
# #df['Province/State'].fillna(df['Country/Region'], inplace=True)
# df['City/Country'].fillna(df['Country/Region'], inplace=True)

total_deaths = ts_death.iloc[:,-2].sum(axis = 0, skipna = True)
total_recovered = ts_recovered.iloc[:,-2].sum(axis = 0, skipna = True)
total_cases = ts_confirmed.iloc[:,-2].sum(axis = 0, skipna = True)

old_total_deaths = ts_death.iloc[:,-3].sum(axis = 0, skipna = True)
old_total_recovered = ts_recovered.iloc[:,-3].sum(axis = 0, skipna = True)
old_total_cases = ts_confirmed.iloc[:,-3].sum(axis = 0, skipna = True)

# total_recovered = df['Recovered'].sum(axis = 0, skipna = True)
# total_cases = df['Confirmed'].sum(axis = 0, skipna = True)

# old_total_deaths = old_df['Deaths'].sum(axis = 0, skipna = True)
# old_total_recovered = old_df['Recovered'].sum(axis = 0, skipna = True)
# old_total_cases = old_df['Confirmed'].sum(axis = 0, skipna = True)

## Change in stats
# death_change = total_deaths - old_total_deaths
# recovery_change = total_recovered - old_total_recovered
# cases_change = total_cases - old_total_cases

import requests as req
import re

def get_num_countries_affected():
    
    resp = req.get("https://www.worldometers.info/coronavirus/")
    
    pattern = '(\d+) countries'
    
    content = resp.text
    
    stripped = re.sub('<[^<]+?>', '', content)
    
    a = re.search(pattern, stripped)
    
    return a.group(1)
    

import dash_table

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output

#external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css','https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(name='tracker', server=server, url_base_pathname='/tracker/', external_stylesheets=external_stylesheets, 
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

app.title = 'Coranavirus Tracker'

app.config.suppress_callback_exceptions = True

nation_options = []
nations = ts_confirmed['Country/Region'].unique()
for nation in ts_confirmed['Country/Region'].unique():
    nation_options.append({'label':str(nation), 'value': nation})
nation_options.append({'label':'Worldwide', 'value': 'Worldwide'})

 
# navbar = dbc.NavbarSimple( 
#     #id='navbar',
#     children=[
#         dbc.NavItem(dbc.NavLink("Home", href="../", external_link=True,)),
#         dbc.NavItem(dbc.NavLink("Latest News", href="../news", external_link=True)),
#         dbc.NavItem(dbc.NavLink("Audiobooks", href="../books", external_link=True)),
#     ],
#     brand="Coronavirus (COVID-19) Global Tracker",
#     brand_href="../",
#     expand=True,
#     dark=True,
#     color='default',
#     sticky="top",
#     fluid=True,
#     #className=" bg-transparent",
# )

confirmed_card = [
    dbc.CardHeader("Total Confirmed Cases", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(total_cases, className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(total_cases-old_total_cases),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

death_card = [
    dbc.CardHeader("Total Deaths", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(total_deaths, className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(total_deaths-old_total_deaths),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

recovered_card = [
    dbc.CardHeader("Total Recovered", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(total_recovered, className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(total_recovered-old_total_recovered),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

affected_card = [
    dbc.CardHeader("Total Infected countries/territories", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(get_num_countries_affected()+"/195", className="card-title", style={'textAlign':'center'}),
            html.Br(),
            #html.P("   ",className="card-text"),
        ]
    ),
]

cards = html.Div([
        dbc.Row(
            [
                dbc.Col(dbc.Card(confirmed_card, color="primary", inverse=True, style={'margin':'10px'}),width=12,lg=3),
                dbc.Col(dbc.Card(death_card, color="danger", inverse=True, style={'margin':'10px'}),width=12,lg=3),
                dbc.Col(dbc.Card(recovered_card, color="success", inverse=True, style={'margin':'10px'}),width=12,lg=3),
                dbc.Col(dbc.Card(affected_card, color="dark", inverse=True, style={'margin':'10px'}),width=12,lg=3),
            ],
            no_gutters=True
        ),
    ])

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF'
}

body = html.Div([
    html.Div(children=[ html.H1('Coronavirus (COVID-19) Global Tracker',
                                style={'border':'1px solid #FFFFFF',
                                       'padding':'20px',
                                       'width':'40%',
                                       'color':'#FFFFFF',
                                       'text-align':'center'
                                       }
                                )
        ],className='splash', style={
                                      'background-image': 'linear-gradient(to top, #191A1A 0%, transparent 75%), url(https://pmcdeadline2.files.wordpress.com/2020/03/coronavirus.jpg)',
                                      'background-position': 'center center',
                                      'background-repeat': 'no-repeat', # By default, a background image will repeat indefinitely, both vertically and horizontally
                                      'background-size' : 'cover',
                                      'display':'flex',
                                      'align-items' : 'center',
                                      'justify-content': 'center'
                                      }),
        
    html.Div([cards], className="mb-4"),
        
    # html.Div([
    #     html.H2('Total Confirmed: {}'.format(total_cases), style={'color':'blue', 'display':'inline-block', 'width': '33%', 'textAlign':'center'}),
    #     html.H2('Total Deaths: {}'.format(total_deaths), style={'color':'red', 'display':'inline-block', 'width': '33%', 'textAlign':'center'}),
    #     html.H2('Total Recovered: {}'.format(total_recovered), style={'color':'green', 'display':'inline-block', 'width': '33%', 'textAlign':'center'}),
    #     # Add past 24hr changes
    # ]),
    
    # html.Div([ 
    #     html.Div([   
    #         dbc.Alert('Total Confirmed: {}'.format(total_cases), color="primary"),
    #     ],className='four columns'),
    #     html.Div([ 
    #         dbc.Alert('Total Deaths: {}'.format(total_deaths), color="danger"),
    #     ],className='four columns'),
    #     html.Div([ 
    #         dbc.Alert('Total Recovered: {}'.format(total_recovered), color="success"),
    #     ],className='four columns'),    
    # ],className='row'),
    
    # html.Div(
    #     [
    #         
    #         dbc.Alert("This is a secondary alert", color="secondary"),
    #         
    #         dbc.Alert("This is a warning alert... be careful...", color="warning"),
    #         
    #         dbc.Alert("This is an info alert. Good to know!", color="info"),
    #         dbc.Alert("This is a light alert", color="light"),
    #         dbc.Alert("This is a dark alert", color="dark"),
    #     ]
    # ),
    
    ##TIME SCALE
    html.Div([
        dcc.Slider(
            id='time-frame',
            min = time_scale_unix[0],
            max = time_scale_unix[-1],
            value = time_scale_unix[-1],
            #updatemode='drag',
            #tooltip = { 'always_visible': True },
            marks=getMarks(time_scale[0],time_scale[-1]),
            step=1,
            )
    ]),
    
    html.Div([
        dcc.Graph(
            id='time-series-confirmed',
        )
    ],style={'padding-bottom': 40,
             'padding-right': 40,
             'padding-left': 40,}),
    
    html.Div(id='slider-output-container', style={'color':'white'}),
    
    ## DROPDOWN ROW
    html.Div([
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown( 
                id='nation',
                options=nation_options,
                value=['Worldwide'],
                multi=True,
                #style=dropdown_style,
                className='dropdown',
                )),
                dbc.Col(dcc.Dropdown( 
                    id='case',
                    #options=[{'label':i,'value':i} for i in df.columns[3:6]], #for data.csv
                    options=[
                        {'label':'All','value':'All'},
                        {'label':'Confirmed','value':'Confirmed'},
                        {'label':'Deaths','value':'Deaths'},
                        {'label':'Recovered','value':'Recovered'},
                    ],
                    value='All',
                    className='dropdown',
                    searchable=False,
                    #style=dropdown_style
                )),
            ]
        )
    ]),
    
    html.Div([
        dcc.Checklist(id='exclude-china', 
                       options=[{'label':'Include China','value':1}],
                       value=[1],
                       labelStyle=dict(color='white'))    
    ]),
    
    html.Div([
      dcc.Graph(
        id='corona-map',
        #figure=fig,
        style={'margin' : '0'}        
      ),
    ]),
    
    # html.Div([
    #     dbc.Row(
    #         [ 
    #             dbc.Col(
    #                 dcc.Graph(
    #                     id='corona-map',
    #                     #figure=fig,
    #                     style={'margin' : '0'}        
    #                 ),
    #             ),       
    #             dbc.Col(
    #                 dash_table.DataTable(
    #                     id='datatable-interactivity',
    #                     columns=[
    #                         {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
    #                     ],
    #                     data=df.to_dict('records'),
    #                     hidden_columns = ["Latitude","Longitude",'City/Country', 'Last Update'],
    #                     filter_action="native",
    #                     sort_action="native",
    #                     sort_mode="multi",
    #                     column_selectable="single",
    #                     # row_selectable="multi",
    #                     # row_deletable=True,
    #                     # selected_columns=[],
    #                     # selected_rows=[],
    #                     page_action="native",
    #                     # page_current= 0,
    #                     # page_size= 20,
    #                     style_table={'color': 'white','overflowY': 'scroll'},
    #                     style_data={'color':'white'},
    #                     style_header={'backgroundColor': 'rgb(30, 30, 30)'},
    #                     style_cell={
    #                         'backgroundColor': 'rgb(50, 50, 50)',
    #                         'color': 'white',
    #                         'minWidth': '80px', 'width': '80px', 'maxWidth': '100px', 'font_size': '20px'
    #                     },
    #                     #style_cell={'minWidth': '80px', 'width': '80px', 'maxWidth': '80px', 'font_size': '20px',},
    #                     fixed_rows={ 'headers': True, 'data': 0 }
    #                 ),
    #             ),
    #         ], style={'padding-top': '50px'}),
    # ]),
    
    # html.Div([
    #     html.H3("Coronavirus News", style={'color': colors['text']}),
    #     generate_html_table()
    # ], className='col-3'),
    
    # Footer
    html.Div(
        className='row',
        children=[
          html.Div(
            className='col',
            children=[
              html.P(
                'Data source:',style={'color': colors['text']}
              ),
              html.A(
                  'Johns Hopkins CSSE',
                  href='https://github.com/CSSEGISandData/COVID-19'
              )                    
            ]
          ),
          html.Div(
            className='col',
            children=[
              html.P(
                'Code avaliable at:',style={'color': colors['text']}
              ),
              html.A(
                  'Github',
                  href='https://github.com/addenergyx/coronavirus-tracker'
              )                    
            ]
          ),
          html.Div(
            className='col',
            children=[
              html.P(
                'Made with:', style={'color': colors['text']}
              ),
              html.A(
                  'Dash / Plot.ly',
                  href='https://plot.ly/dash/'
              )                    
            ]
          ),                                                         
        ],        
        style={
            'padding': 40
        }
    ) 
    
  ])

def Homepage():
    layout = html.Div([
    Navbar(),
    body
    ], style={'backgroundColor': colors['background']})
    return layout
           
app.layout = Homepage()
  
import plotly.graph_objs as go

# @app.callback(Output('slider-output-container', 'children'), [Input('time-frame','value')])
# def test(unix_date):
#     return 'You have selected "{}"'.format(datetime.datetime.fromtimestamp(unix_date).strftime("%m/%d/%y"))

def unix_to_date(unix_date):
    ## In unix use - to remove leading 0 e.g %-m/%-d/%y
    if os.name == 'nt':
        date=datetime.datetime.fromtimestamp(unix_date).strftime("%#m/%#d/%y")
    else:
        date=datetime.datetime.fromtimestamp(unix_date).strftime("%-m/%-d/%y")     
    return date

@app.callback(Output('time-series-confirmed','figure'), [Input('time-frame','value')])
def update_time_series(unix_date):    
    
    #unix_date=1580256000
    
    date = unix_to_date(unix_date)
      
    listy = []
    
    for a in time_scale:
        listy.append(a)
        #print(a +' ? '+ date)
        if a == date:
            #print('-------------------------')
            break
    
    listy.insert(0,'City/Country')
    
    #for individual countries    
    # filtered_ts_confirmed = ts_confirmed[listy]
    # filtered_ts_death = ts_death[listy]
    # filtered_ts_recovered = ts_recovered[listy]
    #filtered_ts_df = ts_confirmed[['City/Country','3/3/20']]
    
    
    ## Total events on a given day
    filtered_ts_confirmed = ts_confirmed[listy[1:]].sum()
    filtered_ts_death = ts_death[listy[1:]].sum()
    filtered_ts_recovered = ts_recovered[listy[1:]].sum()
    
    trace0 = go.Scatter(x=listy[1:], y=filtered_ts_confirmed,
                        mode='lines',
                        name='Confirrmed',
                        line = {'color':'#0275d8'}
                        )
    
    trace1 = go.Scatter(x=listy[1:], y=filtered_ts_death,
                    mode='lines',
                    name='Deaths',
                    line = {'color':'#d9534f'}
                    )

    trace2 = go.Scatter(x=listy[1:], y=filtered_ts_recovered,
                    mode='lines',
                    name='Recovered',
                    line = {'color':'#5cb85c'}
                    )
    
    data = [trace0, trace1, trace2]
    
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       font={
                            'family': 'Courier New, monospace',
                            'size': 18,
                            'color': 'white'
                            },
                       xaxis={'gridcolor':'rgb(46,47,47)','autorange': True,},
                       yaxis={'gridcolor':'rgb(46,47,47)','autorange': True,'title':'Number of cases'},
                       hovermode='closest'
                       )
    
    fig = go.Figure(data=data, layout=layout)
    
    fig.update_layout(
    legend=dict(
        x=0.01,
        y=1,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="#f7f7f7"
        ),
        bgcolor="#292b2c",
        bordercolor="#f7f7f7",
        borderwidth=2,
    )
)

    return fig
                                      
@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               Input('exclude-china','value'), Input('time-frame','value')])
def update_map(selected_nation, selected_case, click, unix_date):
    
    #unix_date=1580256000
    #selected_nation=['Worldwide']
    
    date = unix_to_date(unix_date)
    
    zoom = 3    
    
    ## Country Dropdown
    if 'Worldwide' in selected_nation or not selected_nation: 
        #filtered_df = df
        filtered_ts_confirmed = ts_confirmed
        filtered_ts_death = ts_death
        filtered_ts_recovered = ts_recovered
        zoom = 2
    else:
        #filtered_df = df[df['Country/Region'].isin(selected_nation)] 
        filtered_ts_confirmed = ts_confirmed[ts_confirmed['Country/Region'].isin(selected_nation)]
        filtered_ts_death = ts_death[ts_death['Country/Region'].isin(selected_nation)]
        filtered_ts_recovered = ts_recovered[ts_recovered['Country/Region'].isin(selected_nation)]
    
    ## China Checkbox
    if not click: 
        #filtered_df = filtered_df[filtered_df['Country/Region'] != 'China'] 
        filtered_ts_confirmed = filtered_ts_confirmed[filtered_ts_confirmed['Country/Region'] != 'China']
        filtered_ts_death = filtered_ts_death[filtered_ts_death['Country/Region'] != 'China']
        filtered_ts_recovered = filtered_ts_recovered[filtered_ts_recovered['Country/Region'] != 'China']
    
    px.set_mapbox_access_token(mapbox_access_token)
        
    ## Rename columns to prettify hover data
    temp_deaths_df = filtered_ts_death.rename(columns = {date:'Deaths', 'Lat':'Latitude', 'Long':'Longitude'})
    temp_recovered_df = filtered_ts_recovered.rename(columns = {date:'Recovered', 'Lat':'Latitude', 'Long':'Longitude'})
    temp_confirmed_df = filtered_ts_confirmed.rename(columns = {date:'Confirmed', 'Lat':'Latitude', 'Long':'Longitude'})
    
    #assumes order of countries from datasets are the same
    temp_all = temp_confirmed_df[['City/Country', 'Confirmed','Latitude','Longitude']]
    temp_all.insert(2,'Deaths', temp_deaths_df[['Deaths']])
    temp_all.insert(2,'Recovered',temp_recovered_df[['Recovered']])
    
    if selected_case == 'Deaths':
        fig = px.scatter_mapbox(temp_deaths_df, lat="Latitude", lon="Longitude", size='Deaths', size_max=100, hover_name="City/Country")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    elif selected_case == 'Recovered':
        fig = px.scatter_mapbox(temp_recovered_df, lat="Latitude", lon="Longitude", size="Recovered",
                      size_max=100, hover_name="City/Country")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Green'))
    elif selected_case == 'Confirmed':
        fig = px.scatter_mapbox(temp_confirmed_df, lat="Latitude", lon="Longitude", size="Confirmed",
                      size_max=100, hover_name="City/Country")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Blue'))
    else:
        fig = px.scatter_mapbox(temp_all, lat="Latitude", lon="Longitude", color="Deaths", size="Confirmed",
                              #color_continuous_scale=px.colors.diverging.Picnic,
                              size_max=50, hover_name="City/Country",
                              hover_data=["Confirmed", "Recovered", "Deaths"] 
                              )
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
   
    '''
    Uses data.csv, no time series remove 'Input('exclude-china','value'), Input('time-frame','value')' from
    decorator if using code below
    '''
    
    # zoom = 3    
    
    # filtered_df = df[df['Country/Region'].isin(selected_nation)] # Country Dropdown
    
    # if 'Worldwide' in selected_nation or not selected_nation: # Case Dropdown
    #     filtered_df = df
    #     zoom = 2
    
    # if not click:
    #     filtered_df = filtered_df[filtered_df['Country/Region'] != 'China'] # China Checkbox
    
    # px.set_mapbox_access_token(mapbox_access_token)
        
    # if selected_case == 'Deaths':
    #     #filtered_df = filtered_df[['Deaths','Latitude','Longitude','City/Country']]
    #     fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Deaths",
    #                   size_max=100, hover_name="City/Country",
    #                   hover_data=["Deaths"])
    #     fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    # elif selected_case == 'Recovered':
    #     fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", size="Recovered",
    #                   size_max=100, hover_name="City/Country",
    #                   hover_data=["Confirmed", "Recovered", "Deaths"] )
    #     fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Green'))
    # else:
    #     fig = px.scatter_mapbox(filtered_df, lat="Latitude", lon="Longitude", color="Deaths", size="Confirmed",
    #                           #color_continuous_scale=px.colors.diverging.Picnic,
    #                           size_max=50, hover_name="City/Country",
    #                           hover_data=["Confirmed", "Recovered", "Deaths"] )
    #     fig.update_traces(hoverinfo='text', marker=dict(sizemin=2),showlegend=False)
    
    # fig.update(
    #         layout=dict(title=dict(x=0.5), paper_bgcolor=colors['background'] )
    #     )
    
    # fig.update_layout(
    #     autosize=True,
    #     height=750,
    #     #width=1500,
    #     hovermode='closest',
    #     mapbox=dict(
    #         accesstoken=mapbox_access_token,
    #         bearing=0,
    #         style="dark",
    #         # center=dict(
    #         #     lat=56,
    #         #     lon=324
    #         # ),
    #         pitch=0,
    #         zoom=zoom
    #     ),
    # )
    
    return fig

# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=False)
#     #app.run_server()



































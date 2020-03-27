# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 19:39:52 2020

@author: david
"""
from server import server
import os
from navbar import NationsDropdown, CasesDropdown, Navbar
from dataset import get_jhu_dataset, get_recovery_frame, getMarks, clean_data, get_total, get_previous_total, unix_to_date

import time
import datetime

import requests as req
import re

# generate random integer values
from random import randint

interval_state = 1000
url = 'https://www.worldometers.info/coronavirus/'
ts_confirmed, ts_death = get_jhu_dataset()
ts_recovered = get_recovery_frame(ts_confirmed, ts_death)   

clean_data(ts_confirmed)
clean_data(ts_death)
clean_data(ts_recovered)

time_scale = ts_confirmed.columns[4:-1]
'''
Dash does not support datetime objects by default.
You can solve this issue by converting your datetime object into an unix timestamp.
'''
time_scale_unix = [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in time_scale]

total_deaths = get_total(ts_death)
#total_recovered = ts_recovered.iloc[:,-2].sum(axis = 0, skipna = True)
total_cases = get_total(ts_confirmed)

old_total_deaths = get_previous_total(ts_death)
#old_total_recovered = ts_recovered.iloc[:,-3].sum(axis = 0, skipna = True)
old_total_cases = get_previous_total(ts_confirmed)

def get_num_countries_affected():
    
    resp = req.get(url)
    
    pattern = '(\d+) countries'
    
    content = resp.text
    
    stripped = re.sub('<[^<]+?>', '', content)
    
    a = re.search(pattern, stripped)
    
    return a.group(1)

def get_total(pattern):
    resp = req.get(url)
    
    #pattern = 'Deaths:\s*(\d+.\d+)'
    content = resp.text
    
    stripped = re.sub('<[^<]+?>', '', content)
    
    a = re.search(pattern, stripped)
    a = re.sub('\D', '', str(a.group(1)))
    
    return int(a)

import dash_table

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

#external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css','https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

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
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-146361977-3"></script>
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

app.title = 'Tracker'

app.config.suppress_callback_exceptions = True

confirmed_card = [
    dbc.CardHeader("Total Confirmed Cases", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="con", className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(get_total('Coronavirus Cases:\s*(\d+.\d+)')-old_total_cases),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

death_card = [
    dbc.CardHeader("Total Deaths", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="dea", className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(get_total('Deaths:\s*(\d+.\d+)')-old_total_deaths),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

recovered_card = [
    dbc.CardHeader("Total Recovered", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="reco", className="card-title", style={'textAlign':'center'}),
            #html.P("+{} in the last 24hrs".format(total_recovered-old_total_recovered),className="card-text", style={'textAlign':'center'}),
            html.P("*JHU has stopped reporting recovered cases due to no reliable data sources",className="card-text", style={'textAlign':'center', 'font-size':'8px', #'padding-bottom':'8px'
                                                                                                                              }),
        ]
    ),
]

mortality_card = [
    dbc.CardHeader("Global Mortality Rate", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2('{0:.2f}%'.format((total_deaths / total_cases)*100), className="card-title card-style"),
            #html.P("+{} in the last 24hrs".format(total_recovered-old_total_recovered),className="card-text", style={'textAlign':'center'}),
            html.Br(),
        ]
    ),
]

affected_card = [
    dbc.CardHeader("Total Infected countries/territories", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(get_num_countries_affected(), className="card-title card-style"),
            #html.Br(),
            #html.P("   ",className="card-text"),
        ]
    ),
]

progress = html.Div([
        dbc.Progress(id="progress", className="mr-2 ml-2 mb-3", color="success",striped=True, animated=True),
        dcc.Interval(id="progress-interval", n_intervals=0, interval=interval_state),
    ])


def get_outbrek_days():
    start = datetime.date(2019, 12, 31)
    today = datetime.date.today()
    delta = today - start
    return delta.days

days_card = [
    dbc.CardHeader("Days Since Outbreak", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(get_outbrek_days(), className="card-title card-style"),
            html.Br(),
        ],
    ),
]

cards = html.Div([
        dbc.Row(
            [
                dbc.Col(dbc.Card(days_card, color="light", style={'margin':'10px', 'height':'85%'}), width=12, lg=2),
                dbc.Col(dbc.Card(confirmed_card, color="primary", inverse=True, style={'margin':'10px', 'height':'85%'}), width=12, lg=2),
                dbc.Col(dbc.Card(death_card, color="danger", inverse=True, style={'margin':'10px', 'height':'85%'}), width=12, lg=2),
                dbc.Col(children=[dbc.Card(recovered_card, color="success", inverse=True, style={'margin':'10px', 'height':'85%'}), progress], width=12, lg=2),
                dbc.Col(dbc.Card(mortality_card, color="warning", inverse=True, style={'margin':'10px', 'height':'85%'}), width=12, lg=2),
                dbc.Col(dbc.Card(affected_card, color="dark", inverse=True, style={'margin':'10px', 'height':'85%'}), width=12, lg=2),
            ],
            no_gutters=True,
        ),
    ])

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF'
}

modal = html.Div(
    [
        dbc.Button(" Recovery Data", id="open", className="ml-auto btn-danger fa fa-send", style={'float':'right'}),
        dbc.Modal(
            [
                dbc.ModalHeader("Recovery Data"),
                dbc.ModalBody("John Hopkins University which is the source for this data has decided to drop support for recovery data." +
                              " Active/Recovery will be Confirmed - Deaths till an alternative source is found. Sorry for the inconvenience"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
        ), 
    ], style={'padding-right':'20px'},
)

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
        
    html.Div([
        cards,
        dcc.Interval(id='recovery-interval-component',
                    interval=interval_state,
                    n_intervals=0,
                    )
        ], className="mb-4"),
    
    ##TIME SCALE
    html.Div([
        dcc.Slider(
            id='time-frame',
            min = time_scale_unix[0],
            max = time_scale_unix[-1],
            value = time_scale_unix[-1],
            #updatemode='drag',
            #tooltip = { 'always_visible': True },
            marks=getMarks(time_scale, time_scale_unix),
            step=1,
            ),
        dcc.Interval(id='data-interval-component',
            interval=2000,
            n_intervals=0,
            )
    ]),
    
    html.Div(id='data'),
    
    html.Div(modal),
    
    html.Div([
        dcc.Graph(
            id='time-series-confirmed',
        )
    ],style={'padding-bottom': 40,
             'padding-right': 40,
             'padding-left': 40,}),
        
    ## DROPDOWN ROW
    html.Div([
        dbc.Row(
            [
                html.Div([NationsDropdown(ts_confirmed)]),
                html.Div([CasesDropdown()]),
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

# @app.callback(Output('data','children'), [Input('data-interval-component','n_intervals')])
# def update_dataset(n):
#     #Data files
#     # df = pd.read_csv('data.csv')
#     # old_df = pd.read_csv('old_data.csv')
    
#     ## John hopkins stopped displaying recovery data
#     #ts_recovered= pd.read_csv('time_series_19-covid-Recovered.csv')
#     #ts_confirmed = pd.read_csv('time_series_covid19_confirmed_global.csv')
#     #ts_death = pd.read_csv('time_series_covid19_deaths_global.csv')
    
#     ts_confirmed, ts_death = get_jhu_dataset()
    
#     ts_recovered = get_recovery_frame(ts_confirmed, ts_death)   
    
#     clean_data(ts_confirmed)
#     clean_data(ts_death)
#     clean_data(ts_recovered)
#     #clean_data(df)
#     #ts_confirmed.fillna(method='bfill', inplace=True, axis=1)
    
#     time_scale = ts_confirmed.columns[4:-1]
#     '''
#     Dash does not support datetime objects by default.
#     You can solve this issue by converting your datetime object into an unix timestamp.
#     '''
#     time_scale_unix = [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in time_scale]
    
#     # ## Cleanup data
#     # for index, row in df.iterrows():
#     #       if row['Province/State'] == row['Country/Region'] or row['Province/State'] == 'UK':
#     #           df['Province/State'][index] = None
    
#     # city_country = np.array(df['Province/State'] + ", " + df['Country/Region'] )
#     # df["City/Country"] = city_country
#     # #df['Province/State'].fillna(df['Country/Region'], inplace=True)
#     # df['City/Country'].fillna(df['Country/Region'], inplace=True)
    
#     total_deaths = get_total(ts_death)
#     #total_recovered = ts_recovered.iloc[:,-2].sum(axis = 0, skipna = True)
#     total_cases = get_total(ts_confirmed)
    
#     old_total_deaths = get_previous_total(ts_death)
#     #old_total_recovered = ts_recovered.iloc[:,-3].sum(axis = 0, skipna = True)
#     old_total_cases = get_previous_total(ts_confirmed)
    
#     # total_recovered = df['Recovered'].sum(axis = 0, skipna = True)
#     # total_cases = df['Confirmed'].sum(axis = 0, skipna = True)
    
#     # old_total_deaths = old_df['Deaths'].sum(axis = 0, skipna = True)
#     # old_total_recovered = old_df['Recovered'].sum(axis = 0, skipna = True)
#     # old_total_cases = old_df['Confirmed'].sum(axis = 0, skipna = True)
    
#     ## Change in stats
#     # death_change = total_deaths - old_total_deaths
#     # recovery_change = total_recovered - old_total_recovered
#     # cases_change = total_cases - old_total_cases
        
#     return #total_cases, total_deaths, old_total_cases, old_total_deaths, ts_confirmed, time_scale, time_scale_unix

@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = int(get_total('Recovered:\s*(\d+.\d+)') / (get_total('Coronavirus Cases:\s*(\d+.\d+)') - get_total('Deaths:\s*(\d+.\d+)')) *100)
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %"

@app.callback(
    [Output('reco','children'), Output('con','children'), Output('dea','children')],
    [Input('recovery-interval-component','n_intervals')])
def update_cards(n):
    
    ## Randomise scraping site times
    global interval_state
    interval_state = randint(60000, 180000)
    
    return "*"+"{:,d}".format(get_total('Recovered:\s*(\d+.\d+)')), "{:,d}".format(get_total('Coronavirus Cases:\s*(\d+.\d+)')), "{:,d}".format(get_total('Deaths:\s*(\d+.\d+)'))

# @app.callback(Output('con','children'), [Input('recovery-interval-component','n_intervals')])
# def update_confirmed(n):
#     return "{:,d}".format(int(get_total('Coronavirus Cases:\s*(\d+.\d+)')))

# @app.callback(Output('dea','children'), [Input('recovery-interval-component','n_intervals')])
# def update_deaths(n):    
#     return "{:,d}".format(int(get_total('Deaths:\s*(\d+.\d+)')))

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
                        line = {'color':'#0275d8'},
                        #fill='tozeroy'
                        )
    
    trace1 = go.Scatter(x=listy[1:], y=filtered_ts_death,
                    mode='lines',
                    name='Deaths',
                    line = {'color':'#d9534f'},
                    #fill='tozeroy'
                    )

    trace2 = go.Scatter(x=listy[1:], y=filtered_ts_recovered,
                    mode='lines',
                    name='Active or Recovered',
                    line = {'color':'#5cb85c'},
                    #fill='tozeroy'
                    )
    
    data = [trace0, trace1, trace2]
    
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       font={
                            'family': 'Courier New, monospace',
                            'size': 18,
                            'color': 'white'
                            },
                       title="Global Cases",
                       xaxis={'gridcolor':'rgb(46,47,47)','autorange': True,},
                       yaxis={'gridcolor':'rgb(46,47,47)','autorange': True,'title':'Number of cases'},
                       hovermode='closest',
                       transition={
                            'duration': 500,
                            'easing': 'cubic-in-out',}
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
 
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
                                     
@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               Input('exclude-china','value'), Input('time-frame','value')])
def update_map(selected_nation, selected_case, click, unix_date):
    
    #unix_date=1585008000
    #selected_nation=['Worldwide']
    
    date = unix_to_date(unix_date)
    #date='3/25/20'
    
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
    temp_recovered_df = filtered_ts_recovered.rename(columns = {date:'Active/Recovered', 'Lat':'Latitude', 'Long':'Longitude'})
    temp_confirmed_df = filtered_ts_confirmed.rename(columns = {date:'Confirmed', 'Lat':'Latitude', 'Long':'Longitude'})

    #Some data from JHU appears as -1 unsure why
    temp_recovered_df[temp_recovered_df['Active/Recovered'] < 0] = 0
    temp_confirmed_df[temp_confirmed_df['Confirmed'] < 0] = 0
    temp_deaths_df[temp_deaths_df['Deaths'] < 0] = 0

    #assumes order of countries from datasets are the same
    temp_all = temp_confirmed_df[['City/Country', 'Confirmed','Latitude','Longitude']]
    temp_all.insert(2,'Deaths', temp_deaths_df[['Deaths']])
    temp_all.insert(2,'Active/Recovered',temp_recovered_df[['Active/Recovered']])
    
    if selected_case == 'Deaths':
        fig = px.scatter_mapbox(temp_deaths_df, lat="Latitude", lon="Longitude", size='Deaths', size_max=100, hover_name="City/Country")
        fig.update_traces(hoverinfo='text', marker=dict(sizemin=5, color='Red'))
    elif selected_case == 'Active/Recovered':
        fig = px.scatter_mapbox(temp_recovered_df, lat="Latitude", lon="Longitude", size="Active/Recovered",
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
                              hover_data=["Confirmed", "Active/Recovered", "Deaths"] 
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
       
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
    #app.run_server()



































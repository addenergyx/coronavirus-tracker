# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 19:39:52 2020

@author: david
"""
from server import server
import os
from components import NationsDropdown, CasesDropdown, Navbar, Footer, Banner
from dataset import get_jhu_dataset, getMarks, clean_data, unix_to_date, getTimeScale, getTimeScaleUnix, get_deaths_diff, get_cases_diff, get_recovery_diff, get_data_from_postgres, get_daily_report
import dash_daq as daq

import datetime

import requests as req
import re
import pandas as pd

# generate random integer values
from random import randint

import plotly.graph_objs as go

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State

import dash_table

import base64

image_filename = 'assets/img/hand-wash.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

interval_state = 60000
url = 'https://www.worldometers.info/coronavirus/'

# number of seconds between re-calculating the data                                                                                                                           
# UPDATE_INTERVAL = 3600

def get_new_data():
    
    """Updates the global variable 'data' with new data"""
    # Global variables will break the app https://dash.plotly.com/sharing-data-between-callbacks
    # Setting global variables in Dash isn’t safe as the memory isn’t shared across processes. 
    # In general, it is not safe to mutate data outside of the scope of a callback!
    #global ts_confirmed, ts_death, ts_recovered
    # ts_confirmed, ts_death = get_jhu_dataset()
    # #ts_recovered = get_recovery_dataset()   
  
    # ts_recovered = pd.read_csv('recovered.csv')

    #clean_data(ts_recovered)
    
    '''
    Dash does not support datetime objects by default.
    You can solve this issue by converting your datetime object into an unix timestamp.
    '''
    # global time_scale, time_scale_unix
    # time_scale = ts_confirmed.columns[4:-1]
    # time_scale_unix = [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in time_scale]
    
    # global total_deaths, total_cases, old_total_deaths, old_total_cases
    # ##SHOULD PROBABLY GO IN OWN THREAD AND UPDATE MORE FREQUENTLY
    # total_deaths = get_total(ts_death)
    # #total_recovered = ts_recovered.iloc[:,-2].sum(axis = 0, skipna = True)
    # total_cases = get_total(clean_data(ts_confirmed))
    
    # old_total_deaths = get_previous_total(clean_data(ts_death))
    # #old_total_recovered = ts_recovered.iloc[:,-3].sum(axis = 0, skipna = True)
    # old_total_cases = get_previous_total(clean_data(ts_confirmed))

# def get_new_data_every(period=UPDATE_INTERVAL):
#     """Update the data every 'period' seconds"""
#     while True:
#         get_new_data()
#         print(str(datetime.datetime.now())+": data updated")
#         time.sleep(period)

def get_num_countries_affected():
    
    resp = req.get(url)
    
    pattern = '(\d+) countries'
    
    content = resp.text
    
    stripped = re.sub('<[^<]+?>', '', content)
    
    a = re.search(pattern, stripped)
    
    return a.group(1)

def pull_total(pattern):
    resp = req.get(url)
    
    #pattern = 'Deaths:\s*(\d+.\d+)'
    content = resp.text
    
    stripped = re.sub('<[^<]+?>', '', content)
    
    a = re.search(pattern, stripped)
    a = re.sub('\D', '', str(a.group(1)))
    
    return int(a)

# get initial data                                                                                                                                                            
#get_new_data()

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

#external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css','https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

app = dash.Dash(name='tracker', server=server, url_base_pathname='/tracker/', external_stylesheets=external_stylesheets, 
                meta_tags=[
                    #{ 'name':'viewport','content':'width=device-width, initial-scale=1, shrink-to-fit=no' },## Fixes media query not showing
                    {
                        'name':'description',
                        'content':'This dashboard is designed to monitor events, deaths, and recoveries reported by several sources such as WHO and Johns Hopkins University on the n-Cov (Coronavirus). This constantly searches repositories and reviews all countries case studies.',
                        'keywords':'coronavirus,coronavirus news,coronavirus outbreak,coronavirus update,covid19,n-covid19, ncov',
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
        
        <script type='text/javascript' src='https://platform-api.sharethis.com/js/sharethis.js#property=5e849281c43e3f0019117eac&product=inline-share-buttons' async='async'></script>
        
        <script async src="https://platform-api.sharethis.com/js/sharethis.js#property=5e849281c43e3f0019117eac&product=sticky-share-buttons"></script>
        
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

app.title = 'Live Coronavirus Tracker'

app.config.suppress_callback_exceptions = True

confirmed_card = [
    dbc.CardHeader("Total Confirmed Cases", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="con", className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(get_cases_diff()),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

death_card = [
    dbc.CardHeader("Total Deaths", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="dea", className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(get_deaths_diff()),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

recovered_card = [
    dbc.CardHeader("Total Recovered", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(id="reco", className="card-title", style={'textAlign':'center'}),
            html.P("+{} in the last 24hrs".format(get_recovery_diff()),className="card-text", style={'textAlign':'center'}),
        ]
    ),
]

mortality_card = [
    dbc.CardHeader("Global Mortality Rate", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2('{0:.2f}%'.format((int(pull_total('Deaths:\s*(\d+.*\d+)')) / int(pull_total('Coronavirus Cases:\s*(\d+.*\d+)')))*100), className="card-title card-style"),
        ]
    ),
]

affected_card = [
    dbc.CardHeader("Total Infected countries/territories", style={'textAlign':'center'}),
    dbc.CardBody(
        [
            html.H2(get_num_countries_affected(), className="card-title card-style"),
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
                dbc.Col(dbc.Card(days_card, color="light", className='card-style'), width=12, lg=2),
                dbc.Col(dbc.Card(confirmed_card, color="primary", inverse=True, className='card-style'), width=12, lg=2),
                dbc.Col(dbc.Card(death_card, color="danger", inverse=True, className='card-style'), width=12, lg=2),
                dbc.Col(children=[dbc.Card(recovered_card, color="success", inverse=True, className='card-style'), progress], width=12, lg=2),
                dbc.Col(dbc.Card(mortality_card, color="warning", inverse=True, className='card-style'), width=12, lg=2),
                dbc.Col(dbc.Card(affected_card, color="dark", inverse=True, className='card-style'), width=12, lg=2),
            ],
            no_gutters=True,
        ),
    ])

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF',
    'secondary':'#2B2B2B'
}

modal = html.Div(
    [
        dbc.Button("Tips to Stay Safe", id="open", className="btn btn-outline-primary", style={'float':'right', 'background-color':'transparent'}),
        dbc.Modal(
            [
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width':'100px', 'margin':'0 auto', 'margin-top':'20px'}),
                dbc.ModalHeader("STAY HOME, SAVE LIVES", style={'margin':'0 auto'}),
                dbc.ModalBody(["The virus is believed to spread mainly through the respiratory droplets formed whenever an infected individual coughs or sneezes through human interaction.", 
                               html.Br(), html.Br(),
                               "Frequently Wash your hands with soap and water for at least 30 seconds. Avoid touching your eyes, nose, and mouth with unwashed hands."],
                              style={'textAlign':'center'}),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close", className="ml-auto"),
                    #dbc.Button("Next", id="next", className="ml-auto")
                    ]
                ),
            ],
            id="modal",
            centered=True,
            scrollable=True,
        ), 
    ], style={'padding-right':'20px','padding-bottom':'40px'},
)

modal2 = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader("STAY HOME, SAVE LIVES", style={'margin':'0 auto'}),
                dbc.ModalBody("Frequently Wash your hands with soap and water for at least 20 seconds. Always Carry a hand sanitizer that contains at least 60% alcohol. Avoid touching your eyes, nose, and mouth with unwashed hands.",
                              style={'textAlign':'center'}),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close2", className="ml-auto"),
                ]),
            ],
            id="modal2",
            centered=True,
        ), 
    ],
)

body = html.Div([
    html.Div(children=[ Navbar(), html.H1('Coronavirus (COVID-19) Global Tracker',
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
            min = getTimeScaleUnix()[0],
            max = getTimeScaleUnix()[-1],
            value = getTimeScaleUnix()[-1],
            # #updatemode='drag',
            # #tooltip = { 'always_visible': True },
            marks=getMarks(6),
            step=1,
            ),

    ]),
    
    dcc.Interval(id='data-interval-component',
        interval=3600000*3,
        n_intervals=0,
    ),
    
    html.Div(modal),
    html.Div(modal2),
        
    ## CHARTS ROW
    html.Div([
        dbc.Row(
            [
                
            ## PIE CHART
            dbc.Col(
                dcc.Loading(
                    children=[
                        html.Div(
                            [
                                #html.P('Cases Distribution', style={'color':colors['text'], 'textAlign':'left'}),
                                dcc.Graph(id='pie-chart',)
                            ]
                        )
                    ], type='circle'
                ), width=12,lg=3),          
            
            ## LINE GRAPH
            dbc.Col(
                html.Div(
                    [
                        dcc.Graph(id='time-series-confirmed'),
                    ]
            ), width=12, lg=9),
             
            ]
        )
    ], style={'padding-bottom':'20px'}),
    #style={'padding-bottom': 40, 'padding-right': 40, 'padding-left': 40,}
    
    ## DROPDOWN ROW
    html.Div([
        dbc.Row(
            [
                dbc.Col([NationsDropdown(get_data_from_postgres()[0])]),
                dbc.Col([CasesDropdown()]),
            ]
        )
    ]),
    
    html.Div([
        daq.ToggleSwitch(
            id='exclude-china',
            value=True,
            label=['Excluding China', 'Including China'],
            color='#0275d8',
            style={
                'color': 'white',
                'width':'350px'
            }
        ),
    ]),
    
    dcc.Loading(
        children=[
            html.Div([
              dcc.Graph(
                id='corona-map',
                #figure=fig,
                style={'margin' : '0'}        
              ),
            ]),
        ], type='circle',
    ),
    
    ##TODO: trackcorona api stopped working
    # html.Div([
    #     dbc.Row([
    #         dbc.Col(
    #             dash_table.DataTable(
    #                 id='table',
    #                 columns=[{"name": i, "id": i, "selectable": True} for i in get_daily_report().columns],
    #                 data=get_daily_report().to_dict("rows"),
    #                 filter_action="native",
    #                 sort_action="native",
    #                 style_table={'color': 'white', 'overflowY': 'scroll', 'overflowX': 'hidden', 'height':'600px'},
    #                 style_data={'color':'white'},
    #                 style_header={'backgroundColor': 'rgb(30, 30, 30)'},
    #                 fixed_rows={ 'headers': True, 'data': 0 },
    #                 style_cell={
    #                     'backgroundColor': 'rgb(50, 50, 50)',
    #                     'color': 'white',
    #                     'minWidth': '80px', 
    #                     'width': '80px', 
    #                     'maxWidth': '100px', 
    #                     'font_size': '20px',
    #                     'textAlign':'center',
    #                 },
    #             )
    #         )
    #     ])
    # ], style={'padding': '50px'} ),
    
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
    
    html.Div(id='recovery-intermediate-value', style={'display': 'none'}),
 
  ])

def Homepage():
    layout = html.Div([
    Navbar(),
    body,
    Footer(),
    Banner()
    ], style={'backgroundColor': colors['background'], 'overflow-x': 'hidden'})
    return layout

# we need to set layout to be a function so that for each new page load                                                                                                       
# the layout is re-created with the current data, otherwise they will see                                                                                                     
# data that was generated when the Dash app was first initialised             
app.layout = Homepage()

#https://community.plotly.com/t/solved-updating-server-side-app-data-on-a-schedule/6612/3
# Runs get_new_data function in another thread
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)

# @app.callback(Output('time-frame','min'),
#               [Input("data-interval-component", "n_intervals")])
# def update_slider_example_min(input):   
#     min_value = min(df_data_FW[input])
#     return min_value

# @app.callback(Output('time-frame','max'),
#               [Input("data-interval-component", "n_intervals")])
# def update_slider_example_max(input):
#     max_value = max(df_data_FW[input])
#     return max_value

@app.callback(Output("pie-chart", "figure"),[Input('time-frame','value')])
def update_pie(unix_date):
    
    
    ts_confirmed, ts_death, ts_recovered = get_data_from_postgres()
    
    # ts_recovered = pd.read_csv('recovered.csv')
    # ts_death = pd.read_csv('deaths.csv')
    # ts_confirmed = pd.read_csv('confirmed.csv')

    #unix_date=1585440000
    
    date = unix_to_date(unix_date)
    
    active = ts_confirmed[date].sum() - ts_death[date].sum() - ts_recovered[date].sum()
    
    labels = ['Recovered','Deaths','Active']
    values = [ts_recovered[date].sum(),ts_death[date].sum(),active]
    
    #df = pd.DataFrame(data)
    
    # ts_recovered[date].sum()
    # ts_death[date].sum()
    # ts_confirmed[date].sum()

    colors = ['#5cb85c', '#d9534f', '#f0ad4e']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, titlefont=dict(color='white', size=20) )])
    
    fig.update_traces(hoverinfo='label+percent+value', textinfo='none', textfont_size=20,
                  marker=dict(colors=colors))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend = dict(font = dict(color='white')),
                               transition={
                            'duration': 500,
                            'easing': 'cubic-in-out',}
        )
    
    
    return fig

@app.callback(
    [#Output('time-frame','value'),
     Output('time-frame','min'),
     Output('time-frame','max'),
     Output('time-frame','marks'),],
    [Input("data-interval-component", "n_intervals")])
def update_slider(n): 
    #print("slide frank ocean")
    return getTimeScaleUnix()[0], getTimeScaleUnix()[-1], getMarks(6)

### Animate map using method above
'''
on button click
input nintervals every second slider goes up one therefore change map
'''

# @app.callback(Output("recovery-intermediate-value", "children"),[Input("data-interval-component", "n_intervals")])
# def update_data(n):
   
#     ts_confirmed, ts_death = get_jhu_dataset()
#     ts_recovered = pd.read_csv('recovered.csv')
#     #ts_recovered = get_recovery_dataset() 

#     clean_data(ts_confirmed)
#     clean_data(ts_death)
#     clean_data(ts_recovered)

#     ts_confirmed.to_csv('confirmed.csv', index=False)
#     ts_death.to_csv('deaths.csv', index=False)
#     ts_recovered.to_csv('recovered.csv', index=False)
    
#     print("All Data Updated")
    
#     return "Data Updated"

@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = int(pull_total('Recovered:\s*(\d+.*\d+)') / (pull_total('Coronavirus Cases:\s*(\d+.*\d+)') - pull_total('Deaths:\s*(\d+.*\d+)')) *100)
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %"

## Using multi output slowed down dash considerably
@app.callback([Output('reco','children'),
               Output('con','children'),
               Output('dea','children'),],
              [Input('recovery-interval-component','n_intervals')])
def update_cards(n):
    
    ## Randomise scraping site times
    global interval_state
    interval_state = randint(60000, 180000)
    
    return "{:,d}".format(pull_total('Recovered:\s*(\d+.*\d+)')), "{:,d}".format(int(pull_total('Coronavirus Cases:\s*(\d+.*\d+)'))), "{:,d}".format(int(pull_total('Deaths:\s*(\d+.*\d+)')))

# @app.callback(Output('con','children'), [Input('recovery-interval-component','n_intervals')])
# def update_confirmed(n):
#     return "{:,d}".format(int(pull_total('Coronavirus Cases:\s*(\d+.\d+)')))

# @app.callback(Output('dea','children'), [Input('recovery-interval-component','n_intervals')])
# def update_deaths(n):    
#     return "{:,d}".format(int(pull_total('Deaths:\s*(\d+.\d+)')))

@app.callback(Output('time-series-confirmed','figure'), [Input('time-frame','value')])
def update_graph(unix_date):    
    
    ts_confirmed, ts_death, ts_recovered = get_data_from_postgres()
    
    #unix_date=1585440000
    
    date = unix_to_date(unix_date)
      
    listy = []
    
    for a in getTimeScale():
        listy.append(a)
        #print(a +' ? '+ date)
        if a == date:
            #print('-------------------------')
            break
    
    #listy.insert(0,'City/Country')
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
                        fill='tozeroy'
                        )
    
    trace1 = go.Scatter(x=listy[1:], y=filtered_ts_death,
                    mode='lines',
                    name='Deaths',
                    line = {'color':'#d9534f'},
                    fill='tozeroy'
                    )

    trace2 = go.Scatter(x=listy[1:], y=filtered_ts_recovered,
                    mode='lines',
                    name='Recovered',
                    line = {'color':'#5cb85c'},
                    fill='tozeroy'
                    )
    
    data = [trace0, trace2, trace1]
    
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


# @app.callback(
#     [Output("modal2", "is_open"), Output("modal", "is_open")],
#     [Input("next", "n_clicks"), Input("close2", "n_clicks")],
#     [State("modal2", "is_open")],
# )
# def toggle_modal2(n1, n2, is_open2, is_open):
#     if n1 or n2:
#         return not is_open2 and not is_open
#     return is_open2 and not is_open
                                     
@app.callback(Output('corona-map', 'figure'), [Input('nation','value'), Input('case','value'), 
                                               Input('exclude-china','value'), Input('time-frame','value')])
def update_map(selected_nation, selected_case, click, unix_date):
    
    #unix_date=1585008000
    #selected_nation=['Worldwide']
    
    ts_confirmed, ts_death, ts_recovered = get_data_from_postgres()
    
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
    temp_recovered_df = filtered_ts_recovered.rename(columns = {date:'Recovered', 'Lat':'Latitude', 'Long':'Longitude'})
    temp_confirmed_df = filtered_ts_confirmed.rename(columns = {date:'Confirmed', 'Lat':'Latitude', 'Long':'Longitude'})

    #Some data from JHU appears as -1 unsure why
    temp_recovered_df[temp_recovered_df['Recovered'] < 0] = 0
    temp_confirmed_df[temp_confirmed_df['Confirmed'] < 0] = 0
    temp_deaths_df[temp_deaths_df['Deaths'] < 0] = 0

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
                              #hover_data=["Confirmed", "Recovered", "Deaths"], 
                              hover_data=["Confirmed", "Deaths"], 
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
        legend=dict(
            font={'color':colors['background']},
            ),
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

# if __name__ == '__main__':
#     app.run_server(debug=True, use_reloader=False)
#     #app.run_server()



































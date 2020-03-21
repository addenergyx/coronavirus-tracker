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

old_total_deaths = old_df['Deaths'].sum(axis = 0, skipna = True)
old_total_recovered = old_df['Recovered'].sum(axis = 0, skipna = True)
old_total_cases = old_df['Confirmed'].sum(axis = 0, skipna = True)

## Change in stats
death_change = total_deaths - old_total_deaths
recovery_change = total_recovered - old_total_recovered
cases_change = total_cases - old_total_cases

import dash_table

mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

import plotly.express as px

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
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output

#external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
#external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css','https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
external_stylesheets =['https://codepen.io/IvanNieto/pen/bRPJyb.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(name='tracker', server=server, url_base_pathname='/tracker/', external_stylesheets=external_stylesheets )

### Bootstrap doesn't like this code, find fix for buy me a coffee widget
# app.index_string = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         <script data-name="BMC-Widget" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="addenergyx" data-description="Support me on Buy me a coffee!" 
#         data-message="Thank you for visiting. Please support this project" data-color="#FF813F" data-position="right" data-x_margin="18" data-y_margin="18"></script>
#     </head>
#     <body>
#         <div></div>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#         <div>My Custom footer</div>
#     </body>
# </html>
# '''

app.title = 'Coranavirus Tracker'

nation_options = []
nations = df['Country/Region'].unique()
for nation in df['Country/Region'].unique():
    nation_options.append({'label':str(nation), 'value': nation})
nation_options.append({'label':'Worldwide', 'value': 'Worldwide'})

 
navbar = dbc.NavbarSimple( 
    #id='navbar',
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="../", external_link=True, className='col-8')),
        dbc.NavItem(dbc.NavLink("Latest News", href="../news", external_link=True)),
        dbc.NavItem(dbc.NavLink("Audiobooks", href="../books", external_link=True)),
    ],
    brand="Coronavirus (COVID-19) Global Tracker",
    brand_href="../",
    expand=True,
    dark=True,
    className='navbar-transparent bg-transparent'
)

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

cards = html.Div([
        dbc.Row(
            [
                dbc.Col(dbc.Card(confirmed_card, color="primary", inverse=True, style={'margin':'10px'}),width=12,lg=4),
                dbc.Col(dbc.Card(death_card, color="danger", inverse=True, style={'margin':'10px'}),width=12,lg=4),
                dbc.Col(dbc.Card(recovered_card, color="success", inverse=True, style={'margin':'10px'}),width=12,lg=4),
            ],
            no_gutters=True
        ),
    ])

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF'
}

# dropdown_style = {
#         'border': '1px solid white',
#         'background': '#82caff',
#         'width': '50%', 
#         'display':'inline-block'
# }

app.layout = html.Div(children=[
    html.Div([navbar], style={'backgroundColor':'transparent'}),
    
    html.Div(children=[ html.H1('Coronavirus (COVID-19) Global Tracker', 
                                style={'border':'1px solid #FFFFFF',
                                       'padding':'20px',
                                       'width':'40%',
                                       'color':'#FFF',
                                       'text-align':'center'
                                       }
                                )
        ],className='section', style={'height':'65vh',
                                      'min-height':'65vh',
                                      'background-image': 'linear-gradient(to top, #191A1A 0%, transparent 75%), url(https://pmcdeadline2.files.wordpress.com/2020/03/coronavirus.jpg)',
                                      #'background-position': 'center center',
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
    
    
    ## DROPDOWN ROW
    html.Div([
        dbc.Row(
            [
                dbc.Col(dcc.Dropdown( 
                id='nation',
                options=nation_options,
                value='Worldwide',
                #multi=True
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
    
    html.Div([
        dcc.Checklist(id='exclude-china', 
                       options=[{'label':'Include China','value':1}],
                       value=[1],
                       labelStyle=dict(color='white'))    
    ]),
    
    html.Div([
        dbc.Row(
            [ 
                dbc.Col(
                    dcc.Graph(
                        id='corona-map',
                        #figure=fig,
                        style={'margin' : '0'}        
                    ),
                ),       
                dbc.Col(
                    dash_table.DataTable(
                        id='datatable-interactivity',
                        columns=[
                            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                        ],
                        data=df.to_dict('records'),
                        hidden_columns = ["Latitude","Longitude",'City/Country', 'Last Update'],
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        column_selectable="single",
                        # row_selectable="multi",
                        # row_deletable=True,
                        # selected_columns=[],
                        # selected_rows=[],
                        page_action="native",
                        # page_current= 0,
                        # page_size= 20,
                        style_table={'color': 'white','overflowY': 'scroll'},
                        style_data={'color':'white'},
                        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                        style_cell={
                            'backgroundColor': 'rgb(50, 50, 50)',
                            'color': 'white',
                            'minWidth': '80px', 'width': '80px', 'maxWidth': '100px', 'font_size': '20px'
                        },
                        #style_cell={'minWidth': '80px', 'width': '80px', 'maxWidth': '80px', 'font_size': '20px',},
                        fixed_rows={ 'headers': True, 'data': 0 }
                    ),
                ),
            ], style={'padding-top': '50px'}),
    ]),
    
    html.Div([
        html.H3("Coronavirus News", style={'color': colors['text']}),
        generate_html_table()
    ], className='col-3'),
    
    #html.Div(id='datatable-interactivity-container')
  ], style={'backgroundColor': colors['background']})

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

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
    #app.run_server()



































# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 18:16:34 2020

@author: david
"""

import base64
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

colors = {
    'background': '#191A1A',
    'text': '#FFFFFF',
    'secondary':'#2B2B2B'
}

image_filename = 'assets/img/Coronavirus.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

def Navbar():
    navbar = dbc.NavbarSimple( 
        #id='navbar',
        children=[
            #html.A(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="50px"), href="../", className='mr-auto'),
            dbc.NavItem(dbc.NavLink("Home", href="../", external_link=True,)),
            dbc.NavItem(dbc.NavLink("Tracker", href="../tracker/", external_link=True)),
            dbc.NavItem(dbc.NavLink("Map", href="../map/", external_link=True)),
            dbc.NavItem(dbc.NavLink("Latest News", href="../news", external_link=True)),
            dbc.NavItem(dbc.NavLink("Audiobooks", href="../books", external_link=True)),
        ],
        brand="Coronavirus (COVID-19) Global Tracker",
        brand_href="../",
        brand_external_link=True,
        expand=True,
        dark=True,
        color='default',
        sticky="top",
        fluid=True,
        style={'position':'absolute', 'width':'100%'}
        #className=" bg-transparent",
    )
    return navbar

def NationsDropdown(frame):
    nation_options = []
    #nations = ts_confirmed['Country/Region'].unique()
    for nation in frame['Country/Region'].unique():
        nation_options.append({'label':str(nation), 'value': nation})
    nation_options.append({'label':'Worldwide', 'value': 'Worldwide'})
    
    nations_dropdown = dcc.Dropdown( 
                         id='nation',
                         options=nation_options,
                         value=['Worldwide'],
                         multi=True,
                         className='dropdown'
    )
    return nations_dropdown                            
    
def CasesDropdown():
    cases_dropdown = dcc.Dropdown( 
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
    )
    return cases_dropdown
    
def Footer():    
    footer =  html.Div(
                    className='row',
                    children=[
                      html.Div(
                        className='col',
                        children=[
                          html.P(['Data source ', html.Span(className="fa fa-pie-chart")],style={'color': colors['text']}, ),
                          html.A(
                              'Johns Hopkins University',
                              href='https://github.com/CSSEGISandData/COVID-19',
                              className="a links",
                          ),
                          # html.Br(),
                          # html.A(
                          #     'TrackCorona',
                          #     href='https://www.trackcorona.live/api',
                          #     className="a links",
                          # ), 
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
                              href='https://github.com/addenergyx/coronavirus-tracker',
                              className="a links",
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
                              href='https://plot.ly/dash/', 
                              className="a links",
                          ),
                          html.Br(),
                          html.A(
                              'News API',
                              href='https://newsapi.org/',
                              className="a links",
                          ), 
                          html.Br(),
                          html.A(
                              'Flaticon',
                              href='https://www.flaticon.com/authors/photo3idea-studio',
                              className="a links",
                          ),
                        ]
                      ),                                                         
                    ],        
                    style={
                        'padding': 40
                    }
                )
    return footer
    
def Banner():    
    banner = html.Div(
                html.P(['2020 © Developed with ', 
                        html.Span(className='fa fa-heart', style={'color':'red'}), 
                        ' by ',
                        html.A('David', href='https://github.com/addenergyx')], style={'color':colors['text']}), 
                className="footer-copyright", style={'text-align':'center'})
    return banner
    
    
    
    
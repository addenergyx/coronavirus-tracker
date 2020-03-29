# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 18:16:34 2020

@author: david
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc

def Navbar():
    navbar = dbc.NavbarSimple( 
        #id='navbar',
        children=[
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
        #sticky="top",
        fluid=True,
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
    
    
    
    
    
    
    
    
    
    
    
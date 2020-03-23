# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 18:16:34 2020

@author: david
"""

import dash_bootstrap_components as dbc

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

# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 09:01:07 2020

@author: david
"""

import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np

# number of seconds between re-calculating the data                                                                                                                           
UPDADE_INTERVAL = 5

def get_new_data():
    """Updates the global variable 'data' with new data"""
    global data
    data = np.random.normal(size=1000)


def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""
    while True:
        get_new_data()
        print("data updated")
        time.sleep(period)


def make_layout():
    chart_title = "data updates server-side every {} seconds".format(UPDADE_INTERVAL)
    return html.Div(
        dcc.Graph(
            id='chart',
            figure={
                'data': [go.Histogram(x=data)],
                'layout': {'title': chart_title}
            }
        )
    )

app = dash.Dash(__name__)

# get initial data                                                                                                                                                            
get_new_data()

# we need to set layout to be a function so that for each new page load                                                                                                       
# the layout is re-created with the current data, otherwise they will see                                                                                                     
# data that was generated when the Dash app was first initialised                                                                                                             
app.layout = make_layout

# Run the function in another thread
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(get_new_data_every)


if __name__ == '__main__':
    app.run_server()
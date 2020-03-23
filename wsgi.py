# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:41:12 2020

@author: david
"""
import datetime
from dash import Dash
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from tracker import app as app1
from mapout import app as app2

application = DispatcherMiddleware(flask_app, {
    '/app1': app1.server,
    '/app2': app2.server,
})  
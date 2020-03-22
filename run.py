# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 22:26:56 2020

@author: david
"""

from server import server
from tracker import app as tracker
from map import app as map
if __name__ == '__main__':
    server.run()
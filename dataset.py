# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 13:26:07 2020

@author: david
"""

## Rebuilding JHU Dataset from api request

import datetime
import pandas as pd
import COVID19Py

## Date column names
def getList(dict): 
    return list(dict.keys()) 

## Date data
def getValues(dict): 
    return list(dict.values())

def get_jhu_dataset():

    covid19 = COVID19Py.COVID19(data_source="jhu")
    
    ## Timeseries pull request
    data = covid19.getAll(timelines=True)
    
    ## Timeseries data
    timeline = data["locations"]
    
    
    
    iso_dict = timeline[0]['timelines']['confirmed']['timeline']
    
    iso_datetime = getList(iso_dict)
    
    ## Format date to match JHU Dataset
    date_column_names = [datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").strftime("%#m/%#d/%y") for x in iso_datetime]
    
    names = ['Province/State', 'Country/Region', 'Lat', 'Long']
    
    names.extend(date_column_names)
    
    #ace = pd.DataFrame(timeline)
    
    # row_list = []
    # crow = []
    # for a in timeline:
       
    #    row = [a['province'],a['country'],a['coordinates']['latitude'],a['coordinates']['longitude']]
    #    row.extend(getValues(a['timelines']['confirmed']['timeline']))
    #    row_list.append(row)
    
    # confirmed_df = pd.DataFrame(row_list, columns=names)               
    
    confirmed_row_list = []
    deaths_row_list = []
    
    for a in timeline:
       
        crow = [ None if not a['province'] else a['province'], a['country'],float(a['coordinates']['latitude']),float(a['coordinates']['longitude'])]
        drow = [ None if not a['province'] else a['province'],a['country'],float(a['coordinates']['latitude']), float(a['coordinates']['longitude'])]
        fff = a['coordinates']['latitude']
        crow.extend(getValues(a['timelines']['confirmed']['timeline']))
        drow.extend(getValues(a['timelines']['deaths']['timeline']))
       
        confirmed_row_list.append(crow)
        deaths_row_list.append(drow)
    
    confirmed_df = pd.DataFrame(confirmed_row_list, columns=names)               
    deaths_df = pd.DataFrame(deaths_row_list, columns=names)

    return confirmed_df, deaths_df

c,j = get_jhu_dataset()
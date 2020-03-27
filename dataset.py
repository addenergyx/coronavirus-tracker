# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 13:26:07 2020

@author: david
"""

## Rebuilding JHU Dataset from api request

import datetime
import pandas as pd
import COVID19Py
import os
import numpy as np

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
    if os.name == 'nt':
        date_column_names = [datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").strftime("%#m/%#d/%y") for x in iso_datetime]
    else:
        date_column_names = [datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").strftime("%-m/%-d/%y") for x in iso_datetime]
        
    names = ['Province/State', 'Country/Region', 'Lat', 'Long']
    
    names.extend(date_column_names)            
    
    confirmed_row_list = []
    deaths_row_list = []
    
    for a in timeline:
       
        crow = [ None if not a['province'] else a['province'], a['country'],float(a['coordinates']['latitude']),float(a['coordinates']['longitude'])]
        drow = [ None if not a['province'] else a['province'],a['country'],float(a['coordinates']['latitude']), float(a['coordinates']['longitude'])]
        crow.extend(getValues(a['timelines']['confirmed']['timeline']))
        drow.extend(getValues(a['timelines']['deaths']['timeline']))
       
        confirmed_row_list.append(crow)
        deaths_row_list.append(drow)
    
    confirmed_df = pd.DataFrame(confirmed_row_list, columns=names)               
    deaths_df = pd.DataFrame(deaths_row_list, columns=names)

    return confirmed_df, deaths_df

def clean_data(frame):
    for index, row in frame.iterrows():
      if row['Province/State'] == row['Country/Region'] or row['Province/State'] == 'UK':
          frame['Province/State'][index] = None
    
    city_country = np.array(frame['Province/State'] + ", " + frame['Country/Region'] )
    frame["City/Country"] = city_country
    #df['Province/State'].fillna(df['Country/Region'], inplace=True)
    frame['City/Country'].fillna(frame['Country/Region'], inplace=True)
    #frame.ffill()

def get_recovery_frame(confirmed, death):

    aaa = confirmed[confirmed.columns[4:]]
    bbb = death[death.columns[4:]]
    
    ccc = aaa.subtract(bbb)

    ts_recovered = confirmed[['Province/State','Country/Region', 'Lat','Long']]
    ts_recovered = ts_recovered.join(ccc)
    
    return ts_recovered

def getMarks(time_scale, time_scale_unix, Nth=4):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    result = {}
    for i, date in enumerate(time_scale):
        if(i%Nth == 1):
            # Append value to dict
            result[time_scale_unix[i]] = time_scale[i]
    return result

def get_total(frame):
    return frame.iloc[:,-2].sum(axis = 0, skipna = True)

def get_previous_total(frame):
    return frame.iloc[:,-3].sum(axis = 0, skipna = True)

def unix_to_date(unix_date):
    ## In unix use - to remove leading 0 e.g %-m/%-d/%y
    if os.name == 'nt':
        date=datetime.datetime.fromtimestamp(unix_date).strftime("%#m/%#d/%y")
    else:
        date=datetime.datetime.fromtimestamp(unix_date).strftime("%-m/%-d/%y")     
    return date







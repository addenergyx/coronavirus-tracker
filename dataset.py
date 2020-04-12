# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 13:26:07 2020

@author: david
"""

## Rebuilding JHU Dataset from api requests

import datetime
import time
import pandas as pd
import COVID19Py
import os
import numpy as np
import requests
from geopy.geocoders import Nominatim, GoogleV3
from sqlalchemy import create_engine
import dateparser



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
    
    clean_data(confirmed_df)
    clean_data(deaths_df)

    # confirmed_df.to_csv('confirmed.csv', index=False)
    # deaths_df.to_csv('deaths.csv', index=False)

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

    aaa = confirmed[confirmed.columns[4:-1]]
    bbb = death[death.columns[4:-1]]
    
    ccc = aaa.subtract(bbb)

    ts_recovered = confirmed[['Province/State','Country/Region', 'Lat','Long']]
    ts_recovered = ts_recovered.join(ccc)
    
    return ts_recovered

def getTimeScale():
    return get_data_from_postgres()[0].columns[4:-1]

def getTimeScaleUnix():
    '''
    Dash does not support datetime objects by default.
    You can solve this issue by converting your datetime object into an unix timestamp.
    '''
    return [int(time.mktime(datetime.datetime.strptime(x, "%m/%d/%y").timetuple())) for x in getTimeScale()]

def getMarks(Nth=4):
    
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    
    time_scale = getTimeScale()
    time_scale_unix = getTimeScaleUnix()
    
    result = {}
    for i, date in enumerate(time_scale):
        if(i%Nth == 1):
            # Append value to dict
            result[time_scale_unix[i]] = time_scale[i]
    return result

def get_deaths_diff():
    frame = pd.read_csv('deaths.csv')
    return frame.iloc[:,-2].sum(axis = 0, skipna = True) - (frame.iloc[:,-3].sum(axis = 0, skipna = True))

def get_cases_diff():
    frame = pd.read_csv('confirmed.csv')
    return frame.iloc[:,-2].sum(axis = 0, skipna = True) - (frame.iloc[:,-3].sum(axis = 0, skipna = True))

def get_recovery_diff():
    frame = pd.read_csv('recovered.csv')
    return frame.iloc[:,-2].sum(axis = 0, skipna = True) - (frame.iloc[:,-3].sum(axis = 0, skipna = True))

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

def get_recovery_dataset():
    
    url = 'https://pomber.github.io/covid19/timeseries.json'
    
    r = requests.get(url)
    
    countries = r.json()
    
    temp = countries['Italy']
    
    dates = [x['date'] for x in temp]
    
    column_names = ['Province/State','Country/Region', 'Lat', 'Long']
    
    if os.name == 'nt':
        column_names.extend([datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%#m/%#d/%y") for x in dates])
    else:
        column_names.extend([datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%-m/%-d/%y") for x in dates])
        
    recovery_row_list = []
    
    geolocator = Nominatim(timeout=1000 , user_agent="http://www.coronavirustracker.co.uk/tracker/")
    
    print("Updating Recovery Data")
    for country,times in countries.items():
        
        geolocator = GoogleV3(api_key=os.getenv('MAPS_API_KEY') , user_agent="http://www.coronavirustracker.co.uk/tracker/") #Google is faster but breaks
        location = geolocator.geocode(country)
        print(location)

        if location is None:
            geolocator = Nominatim(timeout=1000 , user_agent="http://www.coronavirustracker.co.uk/tracker/") #Google can't find ms zaandam
            location = geolocator.geocode(country)
            print(f"Nominatim - {location}")

        # print(location.latitude)
        # print(location.longitude)
        # print("--------------------------------")
        row = [None, country, location.latitude, location.longitude]
        
        for a in times:
            row.append(a['recovered'])
        
        recovery_row_list.append(row)
    
    recovery = pd.DataFrame(recovery_row_list, columns=column_names)
    
    clean_data(recovery)
       
    #recovery.to_csv('recovered.csv', index=False)
    
    return recovery



def get_data_from_postgres():
    
    ### Google Sheets
    # scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    
    # creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
    
    # client = gspread.authorize(creds)

    # #Google sheets
    # confirmed_sheet = client.open("confirmed").sheet1
    # recovered_sheet = client.open("recovered").sheet1
    # death_sheet = client.open("deaths").sheet1
    
    # ts_recovered = pd.DataFrame(recovered_sheet.get_all_records())
    # ts_death = pd.DataFrame(death_sheet.get_all_records())
    # ts_confirmed = pd.DataFrame(confirmed_sheet.get_all_records())
        
    db_URI = os.getenv('DATABASE_URL')
    engine = create_engine(db_URI)
    
    ts_confirmed = pd.read_sql_table("confirmed", con=engine, index_col='index')
    ts_recovered = pd.read_sql_table("recovered", con=engine, index_col='index')
    ts_death = pd.read_sql_table("deaths", con=engine, index_col='index')
    
    return ts_confirmed, ts_death, ts_recovered

def get_animation_from_postgres():
    db_URI = os.getenv('AWS_DATABASE_URL')
    engine = create_engine(db_URI)
    
    time_lapse = pd.read_sql_table("timelapse", con=engine, index_col='index')
    return time_lapse
    

def get_daily_report():
    
    url = 'https://www.trackcorona.live/api/countries/'
    r = requests.get(url)
    
    countries = r.json()['data']
    
    daily_report = pd.DataFrame(countries)
    
    daily_report.drop(['country_code','latitude','longitude'], axis=1, inplace=True)
    
    daily_report.columns = ['Country', 'Confirmed','Deaths','Recovered','Last Updated']
    today = datetime.datetime.utcnow()
    
    #time = '2020-04-04 14:20:15.168554+00:00'
    
    for i, row in daily_report.iterrows():
        time = row['Last Updated']
        datetime_object = dateparser.parse(time)
        start = datetime_object.replace(tzinfo=None)
        delta = today - start
              
        if delta.days == 1:
            daily_report.loc[i,'Last Updated'] = f"{delta.days} day ago"
        elif delta.days > 0:
            daily_report.loc[i,'Last Updated'] = f"{delta.days} days ago"
        elif (delta.seconds // 3600) == 0:
            daily_report.loc[i,'Last Updated'] = f"{(delta.seconds//60)%60} minutes ago"
        elif (delta.seconds//3600) == 1:
            daily_report.loc[i,'Last Updated'] = "1 hour ago"
        else:
            daily_report.loc[i,'Last Updated'] = f"{(delta.seconds//3600)} hours ago"
            
    return daily_report


def get_animation_frame():
    lookup = pd.read_csv('UID_ISO_FIPS_LookUp_Table.csv')
    
    url = 'https://pomber.github.io/covid19/timeseries.json'
    r = requests.get(url)
    
    countries = r.json()
    
    df = pd.DataFrame(columns=['country','date','confirmed','deaths','recovered'])
    
    for country, data in countries.items():
        print(country)
        a = lookup[lookup['Country_Region'] == country]
    
        for dic in data:
            dic.update({'country' : country, 
                        'Latitude': a['Lat'].iloc[0],
                        'Longitude': a['Long_'].iloc[0]
                        })
            df = df.append(dic, ignore_index=True)
            
            # df.to_csv('animation.csv')
    return df 























# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 10:38:54 2020

@author: david
"""

from dataset import get_jhu_dataset, get_recovery_dataset

import os

from sqlalchemy import create_engine

db_URI = os.getenv('DATABASE_URL')

engine = create_engine(db_URI)

# def iter_pd(df):
#     for val in df.columns:
#         yield val
#     for row in df.to_numpy():
#         for val in row:
#             if pd.isna(val):
#                 yield ""
#             else:
#                 yield val

# def pandas_to_sheets(pandas_df, sheet, clear = True):
#     # Updates all values in a workbook to match a pandas dataframe
#     if clear:
#         sheet.clear()
#     (row, col) = pandas_df.shape
#     cells = sheet.range("A1:{}".format(gspread.utils.rowcol_to_a1(row + 1, col)))
#     for cell, val in zip(cells, iter_pd(pandas_df)):
#         cell.value = val
#     sheet.update_cells(cells)

# scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

# creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)

# client = gspread.authorize(creds)

ts_confirmed, ts_death = get_jhu_dataset()
#ts_recovered = get_recovery_dataset() 
ts_recovered = pd.read_csv('recovered.csv')

# clean_data(ts_confirmed)
# clean_data(ts_death)
# clean_data(ts_recovered)

# confirmed_sheet = client.open("confirmed").sheet1
# recovered_sheet = client.open("recovered").sheet1
# death_sheet = client.open("deaths").sheet1

# pandas_to_sheets(ts_confirmed, confirmed_sheet)
# pandas_to_sheets(ts_death, death_sheet)
# pandas_to_sheets(ts_recovered, recovered_sheet)

ts_confirmed.to_sql('confirmed', engine, if_exists='replace')
ts_recovered.to_sql('recovered', engine, if_exists='replace')
ts_death.to_sql('deaths', engine, if_exists='replace')

print("All Data Updated")
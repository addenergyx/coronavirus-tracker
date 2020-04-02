# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 10:38:54 2020

@author: david
"""

from dataset import get_jhu_dataset, clean_data, get_recovery_dataset

ts_confirmed, ts_death = get_jhu_dataset()
#ts_recovered = pd.read_csv('recovered.csv')
ts_recovered = get_recovery_dataset() 

clean_data(ts_confirmed)
clean_data(ts_death)
clean_data(ts_recovered)

ts_confirmed.to_csv('confirmed.csv', index=False)
ts_death.to_csv('deaths.csv', index=False)
ts_recovered.to_csv('recovered.csv', index=False)

print("All Data Updated")
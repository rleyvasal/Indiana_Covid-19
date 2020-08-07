# -*- coding: utf-8 -*-
"""
Created on Thursday, August 6 01:35:49 2020

@author: Rigoberto Leyva Salmeron
"""

# %%
import pandas as pd
df = pd.read_csv('run_results.csv', header=0)
print(df.head())
del df['counties_index']

# rename columns
df = df.rename(columns={'counties_selection1_1_CountyName':'CountyName', 'counties_selection1_1_Tcases':'Tcases', 
    'counties_race_1_name':'r1', 'counties_race_1_percentage':'rp1', 'counties_race_2_name':'r2',
    'counties_race_2_percentage':'rp2', 'counties_race_3_name':'r3', 'counties_race_3_percentage':'rp3', 
    'counties_race_4_name':'r4', 'counties_race_4_percentage':'rp4', 'counties_race_5_name':'r5', 
    'counties_race_5_percentage':'rp5', 'counties_ethnicity_1_name':'e1', 'counties_ethnicity_1_percentage':'ep1',
    'counties_ethnicity_2_name':'e2', 'counties_ethnicity_2_percentage':'ep2', 'counties_ethnicity_3_name':'e3', 
    'counties_ethnicity_3_percentage':'ep3'})
# remove characters from county name
df['CountyName'] = df['CountyName'].str.replace('Filtering on: ', '')

# %%
# todo delete this section
#df2= df.loc[:,['CountyName', 'Tcases', 'r1', 'rp1', 'r2', 'rp2','r3', 'rp3', 'r4', 'rp4', 'r5', 'rp5', 'e1', 'ep1',
#               'e2', 'ep2', 'e3', 'ep3']]
print(list(df.columns))
print(df.isna().count())
print(df)


#%%
#replace the commas in thousands place in total cases and convert to number
df['Tcases'] = pd.to_numeric(df['Tcases'].astype(str).str.replace(',',''))

#%%
# substitute missing values on race with 0 in percentages
df['rp1'].fillna(0, inplace=True)
df['rp1'].fillna(0, inplace=True)
df['rp3'].fillna(0, inplace=True)
df['rp4'].fillna(0, inplace=True)
df['rp5'].fillna(0, inplace=True)


#%%
#remove percentage symbol from race and convert to number
df['rp1'] = pd.to_numeric(df['rp1'].astype(str).str.strip('%'))
df['rp2'] = pd.to_numeric(df['rp2'].astype(str).str.strip('%'))
df['rp3'] = pd.to_numeric(df['rp3'].astype(str).str.strip('%'))
df['rp4'] = pd.to_numeric(df['rp4'].astype(str).str.strip('%'))
df['rp5'] = pd.to_numeric(df['rp5'].astype(str).str.strip('%'))

#%%
# Calculate cases per race
df['r1cases'] = (df['Tcases'] *(df['rp1'])/100).round().astype(int)
df['r2cases'] = (df['Tcases'] *(df['rp2'])/100).round().astype(int)
df['r3cases'] = (df['Tcases'] *(df['rp3'])/100).round().astype(int)
df['r4cases'] = (df['Tcases'] *(df['rp4'])/100).round().astype(int)
df['r5cases'] = (df['Tcases'] *(df['rp5'])/100).round().astype(int)

#%%
# substitute missing values on ethnicity with 0 in percentages
df['ep1'].fillna(0, inplace=True)
df['ep1'].fillna(0, inplace=True)
df['ep3'].fillna(0, inplace=True)

#%%
# Remove percentage symbol from ethnicity and convert to number
df['ep1'] = pd.to_numeric(df['ep1'].astype(str).str.strip('%'))
df['ep2'] = pd.to_numeric(df['ep2'].astype(str).str.strip('%'))
df['ep3'] = pd.to_numeric(df['ep3'].astype(str).str.strip('%'))

#%%
# calculate  cases per ethnicity
df['e1cases'] = (df['Tcases'] *(df['ep1'])/100).round().astype(int)
df['e2cases'] = (df['Tcases'] *(df['ep2'])/100).round().astype(int)
df['e3cases'] = (df['Tcases'] *(df['ep3'])/100).round().astype(int)


#%%
# Capitalize county name to make sorting work correctly
df['CountyName']= df.CountyName.str.capitalize()


#%%
#  Pivot race
rc1 =(df.pivot_table(index='CountyName', columns='r1', values = 'r1cases'))
rc2 =(df.pivot_table(index='CountyName', columns='r2', values = 'r2cases'))
rc3 =(df.pivot_table(index='CountyName', columns='r3', values = 'r3cases'))
rc4 =(df.pivot_table(index='CountyName', columns='r4', values = 'r4cases'))
rc5 =(df.pivot_table(index='CountyName', columns='r5', values = 'r5cases'))


#%%
# Pivot ethnicity
et1 = df.pivot_table(index='CountyName', columns ='e1', values = 'e1cases')
et2 = df.pivot_table(index='CountyName', columns ='e2', values = 'e2cases')
et3 = df.pivot_table(index='CountyName', columns ='e3', values = 'e3cases')

#%%
# combine race
combined_race = rc5.combine_first(rc2).combine_first(rc3).combine_first(rc4).combine_first(rc1)
combined_race = combined_race[['White','Black or African American', 'Asian', 'Other Race', 'Unknown']]

#%%
# combine ethnicity and rename Unknown column to make sure merges with the other Unknown column for race
combined_ethnicity = et1.combine_first(et2).combine_first(et3)
combined_ethnicity = combined_ethnicity.rename(columns = {'Unknown':'Unknown_eth'})
combined_ethnicity = combined_ethnicity[['Hispanic or Latino', 'Not Hispanic or Latino', 'Unknown_eth']] 

#%%
# place total number of cases reported per county a dataframe
Treported = df[['CountyName','Tcases']]
# have to use inplace and drop to make the index change
Treported.set_index('CountyName', inplace=True, drop=True)

#%%
#  join race and ethicity and total numbe of cases reported
dff = combined_race.join(combined_ethnicity).join(Treported)


#%%
#  Add all races and add all ethnicities
dff['T_race']= dff.White.fillna(0) + dff['Black or African American'].fillna(0) + dff['Asian'].fillna(0) + dff['Other Race'].fillna(0) + dff['Unknown'].fillna(0) 
dff['T_eth'] = dff['Hispanic or Latino'] + dff['Not Hispanic or Latino'].fillna(0) + dff['Unknown_eth'].fillna(0)


# Create a check to compare total number cases race and ethnicity against total cases reported
import numpy as np
dff['T_C_race'] =np.where(dff['Tcases'] == dff['T_race'], 'Ok', 'Not Match!!!')
dff['T_C_eth'] =np.where(dff['Tcases'] == dff['T_eth'], 'Ok', 'Not Match!!!')


#%%
# Send  dataframe to csv
dff.to_csv('Indiana.csv')



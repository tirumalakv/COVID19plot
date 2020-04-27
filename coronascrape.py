#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 00:05:13 2020

@author: Tiru
"""

from selenium import webdriver
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

country = 'India'
website = 'https://www.worldometers.info/coronavirus/'
#Add correct path to your driver here before running
driver = webdriver.Chrome('your-path-to-webdriver/chromedriver')


driver.get(website)
table = driver.find_element_by_xpath('//*[@id="main_table_countries_today"]/tbody[1]')


# Get row count
rowcount = len(table.find_elements_by_tag_name('tr')) - 1

# Get column count
colcount = len(table.find_elements_by_xpath('//tr[2]/td'))
print(rowcount, colcount)

# Make list of countries on the site
listofcountries=[]
for i in range(1, rowcount):
    listofcountries.append(table.find_element_by_xpath("//tr[" + str(i) + "]/td[1]").text)
# Remove empty items in the list    
listofcountries[:]=[item for item in listofcountries if item != '']

listofcols = ['Total_cases', 'New_cases', 'Total_deaths', 'New-deaths', 'Total_recovered', 'Active_cases', 'Critical', 'Cases_per_million', 'Deaths_per_million', 'Total_tests', 'Tests_per_million']

#Make empty list of countries
colsofcountry = [[] for _ in range(rowcount)]


#Populate the list from the site
for i in range(1, rowcount):
    if (table.find_element_by_xpath("//tr[" + str(i) + "]/td[1]").text in listofcountries):
        for j in range(1, 13):
            colsofcountry[i].append(table.find_element_by_xpath("//tr[" + str(i) + "]/td[" + str(j) + "]").text)

datacountries = pd.DataFrame()
#Print the data scraped
for i in range(rowcount):
    datacountries[i]=pd.Series(colsofcountry[i])

# Transpose the data and reindex to countries, drop NaNs form values
    
dataT = datacountries.T # Transposes
dataC = dataT.set_index(keys=0) # Sets index to countries
dataC = dataC.fillna(0) # fills all NaNs with zeros
dataC = dataC[dataC[1] != 0] # drops zero population countries and hence NaNs
dataC.columns = listofcols
dataC.rename_axis("Countries", axis='index', inplace=True)
dataC = dataC.apply(lambda x: pd.to_numeric(x.astype(str).str.replace(',',''), errors='coerce'))
dataC.fillna(0)

driver.quit()


# Drops the outliers where % detection is above 60% to make figure look better
dataC['colY']=(dataC['Total_cases']/dataC['Total_tests']*100)
dataC.drop(dataC[dataC.colY>60].index, inplace=True)
     

# Random colors for countries
colors=cm.rainbow(np.random.rand(len(dataC['colY'])))


x=dataC['Tests_per_million']
y=(dataC['Total_cases']/dataC['Total_tests']*100)

country=dataC.index
size = dataC['Total_cases']


#Plot the scatter plot

plt.figure(figsize=(6, 3), dpi=800)

plt.scatter(x, y, color=colors, s=size*800/max(size), alpha=0.7)
    
plt.xscale('log')
plt.xlabel('Tests Per M capita (Tests/1Million Population) - log scale', fontsize=8)
plt.ylabel('Positive cases per 100 tests\n (%+ve for tested cases)', fontsize=8)

#Annotate selected countries
names=['India', 'France', 'Spain', 'Iran', 'Brazil', 'UK', 'USA', 'Italy', 'Germany', 'Pakistan', 'Sri Lanka', 'Russia', 'Iceland', 'Mozambique']
for name in names:
    plt.annotate(s=name, xy=(x.loc[name], y.loc[name]), fontsize=6)

#Save the plot
plt.savefig('COVID19_26_Apr.png', dpi=800, bbox_inches='tight', pad_inches=0.1)

#Display the plot   
plt.show()


'''
Script to get Counter Strike item names largely based on: https://www.blakeporterneuro.com/learning-python-project-3-scrapping-data-from-steams-community-market/
Program only needs to be run when new items are released.
'''

'''
Last ran on September 1, 2021
'''

import requests
import json
import time
import random
import pickle

# Counter Strike Game ID 730 - Used in search requests below
gameID = '730'

# Get all item names from marketplace
allItemNames = [] # Initialize

allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid='+gameID+'&norender=1&count=100') # Get page
allItems = allItemsGet.content # Get contents
allItems = json.loads(allItems) # Convert to JSON

totalItems = allItems['total_count']
print('Total items: ' + str(totalItems))

# Get all item names by looping through steam community marketplace - limit 100 per page
for currPos in range(0, totalItems + 50, 50):
    time.sleep(random.uniform(0.5, 5))

    allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?start='+str(currPos)+'&count=100000&search_descriptions=0&sort_column=name&appid='+gameID+'&norender=1&count=50000')
    print('Items ' + str(currPos) + ' out of ' + str(totalItems) + ' code: ' + str(allItemsGet.status_code))

    # If status code not 200 then sleep program for 5 minutes and retry get request
    while not allItemsGet.status_code == 200:
        print('Steam overwhelmed by requests - sleeping for 5 minutes')
        time.sleep(60 * 5)
        allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?start='+str(currPos)+'&count=100000&search_descriptions=0&sort_column=name&appid='+gameID+'&norender=1&count=50000')
        print('Items ' + str(currPos) + ' out of ' + str(totalItems) + ' code: ' + str(allItemsGet.status_code))    

    allItems = allItemsGet.content
    allItems = json.loads(allItems)
    allItems = allItems['results']

    for item in allItems:
        allItemNames.append(item['hash_name'])

allItemNames = list(dict.fromkeys(allItemNames)) # Convert to dictionary and back to list to remove duplicates

with open(gameID+'ItemNames.txt', "wb") as file:
    pickle.dump(allItemNames, file)
'''
Script to get Counter Strike item names largely based on: https://www.blakeporterneuro.com/learning-python-project-3-scrapping-data-from-steams-community-market/
'''

import requests
import json
import time
from datetime import datetime
import random
import pickle
import pandas as pd
import numpy as np

# Import auth
with open('./config/auth.json') as file:
    auth = json.load(file)

# Set cookies for steam login
cookie = {'steamLoginSecure' : auth['steamCookie']}

# Counter Strike Game ID 730 - Used in search requests below
gameID = '730'

# Open txt file with all csgo item names
with open(gameID+'ItemNames.txt', 'rb') as file:
    allItemNames = pickle.load(file)

    # Initialize Panda's dataframe with the data we want from each item
    allItemsPD = pd.DataFrame(data = None, index = None, columns = ['itemName', 'timeOnMarket', 'priceIncrease', 'priceAvg', 'priceSD', 'maxPrice', 'maxIdx', 'minPrice', 'minIdx', 'swing', 'volAvg', 'volSD'])

    currItem = 1 # Initialize to keep track of for loop below
    for item in allItemNames:
        
        # Replace symbols with ASCII for URL request
        itemHTTP = item.replace(' ', '%20')
        itemHTTP = itemHTTP.replace('&', '%26')
        itemHTTP = itemHTTP.replace('|', '%7C')

        itemGet = requests.get('https://steamcommunity.com/market/pricehistory/?appid='+gameID+'&market_hash_name='+itemHTTP, cookies=cookie)
        print(str(currItem) + ' out of ' + str(len(allItemNames)) + ' code: ' + str(itemGet.status_code))
        
        # Check that there were no errors with GET request
        if not itemGet.status_code == 200:
            # If issue with GET request, sleep program and try again
            retry = 0
            while retry < 3 or not itemGet.status_code == 200:
                time.sleep(60 * 5)
                itemGet = requests.get('https://steamcommunity.com/market/pricehistory/?appid='+gameID+'&market_hash_name='+itemHTTP, cookies=cookie)
                print(str(currItem) + 'out of ' + str(len(allItemNames)) + ' code: ' + str(itemGet.status_code))
                retry += 1
            
            continue # If error persists, just skip the item

        # No issues with GET request
        else:
            currItem += 1 # Add one to current item counter

            itemData = itemGet.content
            itemData = json.loads(itemData)

            if itemData: # Check that we got data back
                itemPricesRaw = itemData['prices']
                if itemPricesRaw == False or not itemPricesRaw: # Check that there was no issue with request
                    continue # If issue, just skip the item
                else:
                    # Initialize price, volume, time variables
                    itemPrices = []
                    itemVol = []
                    itemDate = []

                    for currDay in itemPricesRaw: # Pull out actual data
                        itemPrices.append(currDay[1]) # idx 1 is price
                        itemVol.append(currDay[2]) # idx 2 is volume
                        itemDate.append(datetime.strptime(currDay[0][0:11], '%b %d %Y')) # idx 0 is date
                    
                    # Convert list strings into numbers
                    itemPrices = list(map(float, itemPrices))
                    itemVol = list(map(float, itemVol))

                    # Combine sales that occur on same day and calc average price
                    for currDay in range(len(itemDate)-1, 1, -1):
                        if itemDate[currDay] == itemDate[currDay-1]:
                            itemPrices[currDay-1] = np.mean([itemPrices[currDay], itemPrices[currDay-1]])
                            itemVol[currDay-1] = np.sum([itemVol[currDay], itemVol[currDay-1]])

                            # Delete repeat data
                            del itemDate[currDay]
                            del itemVol[currDay]
                            del itemPrices[currDay]

                    # Create new list that "normalizes" days from 0 to n
                    normTime = list(range(0, len(itemPrices)))

                    # Basic data
                    timeOnMarket = (datetime.today() - itemDate[0]).days
                    priceIncrease = itemPrices[-1] - itemPrices[0]
                    maxPrice = max(itemPrices)
                    maxIdx = itemPrices.index(maxPrice)
                    minPrice = min(itemPrices)
                    minIdx = itemPrices.index(minPrice)
                    swing = maxPrice - minPrice

                    # Descriptive Stats
                    itemPriceAvg = np.mean(itemPrices)
                    if len(itemPrices) > 1:
                        itemPriceInitial = itemPrices[1] - itemPrices[0]
                    else:
                        itemPriceInitial = itemPrices[0]
                    itemVolAvg = np.mean(itemVol)
                    itemPriceSD = np.std(itemPrices)
                    itemVolSD = np.std(itemVol)

                    # Save data
                    currItemDict = {'itemName':item, 'initial':itemPriceInitial, 'timeOnMarket':timeOnMarket, 'priceIncrease':priceIncrease, 'priceAvg':itemPriceAvg, 'priceSD':itemPriceSD, 'maxPrice':maxPrice, 'maxIdx':maxIdx, 'minPrice':minPrice, 'minIdx':minIdx, 'swing':swing, 'volAvg':itemVolAvg, 'volSD':itemVolSD}
                    currItemPD = pd.DataFrame(currItemDict, index=[0])
                    
                    allItemsPD.append(currItemPD, ignore_index=True)

                    time.sleep(random.uniform(0.1, 1))

print('All item data collected')

# Save dataframe
allItemsPD.to_pickle(gameID + 'PriceData.pkl')

                

 




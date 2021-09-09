import os
import json
import requests
import urllib.parse
import sqlite3

from flask import redirect, render_template, request, session
from functools import wraps


# Render apology message if error - taken from CS50 Finance
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


# Convert item name symbols to ASCII for Steam requests
def steamhash(item):
    # Replace symbols with ASCII for URL request
    itemHash = item.replace(' ', '%20')
    itemHash = itemHash.replace('&', '%26')
    itemHash = itemHash.replace('|', '%7C')

    return itemHash


# Get price data from steam
def steamlookup(item, cookie):
    # Convert item name symbols to ASCII for Steam request
    market_hash_name = steamhash(item)

    # Get item data from Steam
    try:
        url = 'https://steamcommunity.com/market/pricehistory/?appid=730&market_hash_name='+market_hash_name
        response = requests.get(url, cookies=cookie)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse reponse and calculate latest price
    itemData = response.content
    itemData = json.loads(itemData)

    if not itemData: # Check that data exists, otherwise return none
        return None
    else:
        itemPriceHist = itemData['prices']
    if itemPriceHist == False or not itemPriceHist:
        return None

    lastPrice = itemPriceHist[-1][1]

    return {
        'name' : item,
        'lastprice' : lastPrice,
        'source' : 'Steam Market'
    }


# Get prices from Skinport
def splookup(item, api_key):
    # Convert item name symbols to ASCII for Steam request
    market_hash_name = steamhash(item)

    # Get item data from Skinport
    try:
        url = 'https://api.skinport.com/v1/sales/history?app_id=730&currency=CAD&market_hash_name='+market_hash_name
        response = requests.get(url, headers=api_key)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response and calculate last price
    itemData = response.content
    itemData = json.loads(itemData)

    itemPriceHist = itemData[0]['sales']
    lastPrice = itemPriceHist[0]['price']

    return {
        'name' : item,
        'lastprice' : lastPrice,
        'source' : 'Skinport'
    }


# Format values as $x.xx
def dollars(value):
    return f"${value:,.2f}"


    



import os

import requests
import json
import time
from datetime import datetime
import random
import pandas as pd
import numpy as np
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

from helpers import apology, splookup, steamlookup, dollars


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure SQLite db for use
conn = sqlite3.connect('skins.db', check_same_thread=False) # Check same thread set to False to share across application
db = conn.cursor()

# Custom filter
app.jinja_env.filters["dollars"] = dollars

# Import auth
with open('./config/auth.json') as file:
    auth = json.load(file)


# Make sure Steam cookies and API key set
#if not os.environ.get('STEAM_COOKIES'):
#    raise RuntimeError('STEAM_COOKIES not set')
#if not os.environ.get('header'):
#    raise RuntimeError('SKINPORT HEADER not set')


@app.route('/', methods = ['GET', 'POST'])
def index():
    
    # Reached route via POST
    if request.method == 'POST':
        # Get price data for skin submitted 
        itemSearch = request.form.get('item')
        print(itemSearch)

        cookie = {'steamLoginSecure' : auth['steamCookie']}
        steamData = steamlookup(itemSearch, cookie)
        print(steamData)

        header = {'Authorization' : auth['skinportAuth']}
        spData = splookup(itemSearch, header)
        print(spData)

        # Query db for all item names and save into variable to pass back into HTML
        db.execute('SELECT item_name FROM skins')

        allItems = []
        fetch = list(db.fetchall())
        for item in fetch:
            allItems.append(item[0])

        return render_template('index.html', allItems = allItems, steamData = steamData, spData = spData)
    
    # Reached route via GET
    else:
        # Query db for all item names and save into variable to pass into HTML
        db.execute('SELECT item_name FROM skins')

        allItems = []
        fetch = list(db.fetchall())
        for item in fetch:
            allItems.append(item[0])

        return render_template('index.html', allItems = allItems)



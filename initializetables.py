import pickle
import sqlite3

conn = sqlite3.connect('skins.db') # Create db if does not exist and connect

c = conn.cursor() # Create cursor to be able to interact with db

#c.execute('''CREATE TABLE skins (
#    item_name TEXT,
#    weapon_type TEXT,
#    item_skin TEXT,
#    item_wear TEXT,
#    market_hash_name TEXT
#)''')


# Counter Strike Game ID 730 - Used in search requests below
gameID = '730'

# Open txt file with all csgo item names
with open(gameID+'ItemNames.txt', 'rb') as file:
    allItemNames = pickle.load(file)

    for item in allItemNames:
        print(item)
        
        # Replace symbols with ASCII for URL request
        itemHash = item.replace(' ', '%20')
        itemHash = itemHash.replace('&', '%26')
        itemHash = itemHash.replace('|', '%7C')

        # Isolate weapon type/skin type/item wear
        try:
            weapon_type = item.split(' | ')[0]
            item_skin = item.split(' | ')[1].split('(')[0]
            item_wear = '(' + item.split(' | ')[1].split('(')[1]
        except IndexError:
            continue

        c.execute('INSERT INTO skins VALUES (?, ?, ?, ?, ?)', (item, weapon_type, item_skin, item_wear, itemHash)) # Insert item + hash into db
        conn.commit() # Commit changes to db

conn.close() # Good practice to close db

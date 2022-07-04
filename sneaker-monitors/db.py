import sqlite3
import os

monitors = [
    dict(
        name='footlocker',
        username='Footlocker Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='offspring',
        username='Offspring Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='shopify',
        username='Shopify Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='sivasdescalzo',
        username='Sivasdescalzo Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='snipes',
        username='Snipes Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='snkrs',
        username='SNKRS Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
    dict(
        name='ssense',
        username='Ssense Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
        dict(
        name='supreme',
        username='Supreme Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
    dict(
        name='zalando',
        username='Zalando Monitor',
        avatar_url='',
        colour=16777215,
        delay=1,
        details=''
    ),
]

columns = [
    'webhook',
    'username',
    'avatar_url',
    'colour',
    'delay',
    'keywords',
    'proxies',
    'free_proxy',
    'details'
]

def create_config_db():
    if os.path.isfile('config.db'):
        con = sqlite3.connect('config.db')
    else:
        con = sqlite3.connect('config.db')
        cur = con.cursor()
        cur.execute("create table monitors (name, webhook, username, avatar_url, colour, delay, keywords, proxies, free_proxy, details)")
        
        for item in monitors:
            cur.execute(f"INSERT INTO monitors (name, username, avatar_url, colour, delay, details) VALUES ('{item['name']}', '{item['username']}', '{item['avatar_url']}', '{item['colour']}', '{item['delay']}', '{item['details']}')")
        con.commit()


def get_config(monitor):
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    item = cur.execute(f"SELECT * FROM monitors WHERE name = '{monitor}'")
    try:
        for i in item:
            return i
    except:
        return None


def update_config(monitor, webhook=None, username=None, avatar_url=None, colour=None, delay=None, keywords=None,proxies=None, free_proxy=None, details=None):
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    query = 'UPDATE monitors SET '
    start = 0
    for col in columns:
        if eval(col) == 'null':
            if start == 0:
                query += f"{col} = null"
                start = 1
            else:
                query += f", {col} = null"
        elif eval(col) is not None:
            if start == 0:
                query += f"{col} = '{eval(col)}'"
                start = 1
            else:
                query += f", {col} = '{eval(col)}'"

    query += f" WHERE name = '{monitor}';"
    cur.execute(query)
    con.commit()


def get_all_config():
    con = sqlite3.connect('config.db')
    cur = con.cursor()
    item = cur.execute("SELECT * FROM monitors;")
    try:
        items = []
        for i in item:
            items.append(i)
        return items
    except:
        return None


from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import requests

from datetime import datetime
import time

import json
import logging
import dotenv
import traceback

logging.basicConfig(filename='Solebox.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

INSTOCK = []


def scrape_main_site(headers, proxy):
    """
    Scrapes Solebox site
    """
    items = []
    
    # Makes request to site
    url = f'https://www.solebox.com/{CONFIG["LOC"]}/c/footwear?srule=standard&openCategory=true&sz=96'
    html = requests.get(url=url, headers=headers, timeout=15, proxies=proxy)
    output = BeautifulSoup(html.text, 'html.parser')
    array = output.find_all('div', {'class': 'b-product-grid-tile js-tile-container'})

    # Stores particular details in array
    for ele in array:
        data = json.loads(ele.find('div', {'class': 'b-product-tile js-product-tile'})['data-gtm'])
        item = [ele.find('span', {'class': 'b-product-tile-brand b-product-tile-text js-product-tile-link'}).text.replace(' ','').replace('\n',''),
                ele.find('div', {'class': 't-heading-main b-product-tile-title b-product-tile-text'}).text.replace('\n',''),
                ele.find('span', {'class': 'b-product-tile-link js-product-tile-link'})['href'],
                ele.find('source', {'media': "(min-width: 1024px)"})['data-srcset'].split(',')[0],
                data['id'],
                data['price'],
                data['dimension25']
        ]
        items.append(item)
    
    logging.info(msg='Successfully scraped site')
    return items


def checker(product):
    """
    Determines whether the product status has changed
    """
    return product in INSTOCK


def test_webhook():
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these monitors!",
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(title, url, thumbnail, price, colour, id):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "url": f'https://www.solebox.com{url}',
            "thumbnail": {"url": thumbnail},
            "color": int(CONFIG['COLOUR']),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "Price", "value": price},
                {"name": "Colour", "value": colour},
                {"name": "ID", "value": id}
            ]
        }]
    }

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(product, start):
    if not checker(product):
        # If product is available but not stored - sends notification and stores
        INSTOCK.append(product)
        if start == 0:
            discord_webhook(
                title=f'{product[0]} {product[1]}',
                url=product[2],
                thumbnail=product[3],
                id=product[4],
                price=product[5],
                colour=product[6]
            )
            print(product)


def monitor():
    """
    Initiates monitor for Solebox site
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')

    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    proxy_no = 0
    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    
    # Collecting all keywords (if any)
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        try:
            # Makes request to site and stores products 
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for item in items:

                if keywords == "":
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in keywords:
                        if key.lower() in item[0].lower():
                            comparitor(item, start)
            
            # Allows changes to be notified
            start = 0
            
            # User set delay
            time.sleep(float(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            
            if CONFIG['PROXY'] != "":
                # If optional proxy set, rotates if there are multipl proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    monitor()

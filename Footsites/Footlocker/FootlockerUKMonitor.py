# No restocks, only releases
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import requests
import urllib3

from datetime import datetime
import time

import json
import logging
import dotenv
import traceback


logging.basicConfig(filename='Footlockerlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

INSTOCK = []

def test_webhook():
    """
    Sends a test Discord webhook notification
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these montiors!",
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


def discord_webhook(title, url, thumbnail, style, sku, price):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title, 
            "url": url,
            "thumbnail": {"url": thumbnail},
            "color": int(CONFIG['COLOUR']),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "Style", "value": style},
                {"name": "SKU", "value": sku},
                {"name": "Price", "value": price},
            ]
        }]
    }

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(result.status_code))


def checker(sku):
    """
    Determines whether the product status has changed
    """
    return sku in INSTOCK


def scrape_main_site(headers, proxy):
    """
    Scrape the Footlocker site and adds each item to an array
    """
    # Makes request to site
    s = requests.Session()
    html = s.get('https://www.footlocker.co.uk/en/men/shoes/', headers=headers, proxies=proxy, verify=False, timeout=10)
    soup = BeautifulSoup(html.text, 'html.parser')
    data = soup.select('body > script:nth-child(3)')
    output = json.loads(str(data).split('window.digitalData')[0][82:-7])

    logging.info(msg='Successfully scraped site')
    s.close()
    return output['search']['products']


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item['sku']):
        # If product is available but not stored - sends notification and stores
        INSTOCK.append(item['sku'])
        if start == 0:            
            discord_webhook(
                title=item['name'],
                style=item['baseOptions'][0]['selected']['style'],
                url='https://www.footlocker.co.uk/product/' + item['name'].replace(' ','-') + '/' + item['sku'] + '.html',
                thumbnail=f'https://images.footlocker.com/is/image/FLEU/{item["sku"]}?wid=500&hei=500&fmt=png-alpha',
                price=item['price']['formattedValue'],
                sku=item['sku'],
            )


def monitor():
    """
    Initiates monitor
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
            items = scrape_main_site(headers, proxy)
            for item in items:

                if keywords == '' or keywords == ['']:
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
            time.sleep(int(CONFIG['DELAY']))

        except Exception as e:
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            print(traceback.format_exc())
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
            
            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {}
                
            else:
                # if optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"https://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

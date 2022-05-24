# No restocks, only releases
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from bs4 import BeautifulSoup
import requests
import urllib3
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback
import config

logging.basicConfig(filename='Zalandolog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

proxy_obj = FreeProxy(country_id=config.FREE_PROXY_LOCATION, rand=True)

INSTOCK = []


def scrape_main_site(headers, proxy):
    """
    Scrape the Zalando site and adds each item to an array
    """
    items = []
    
    # Makes request to site
    url = 'https://m.zalando.co.uk/mens-shoes-trainers/?order=activation_date'
    s = requests.Session()
    html = s.get(url=url, headers=headers, proxies=proxy, verify=False, timeout=15)
    soup = BeautifulSoup(html.text, 'html.parser')
    products = soup.find_all('div', {'class': 'DT5BTM w8MdNG cYylcv QylWsg _75qWlu iOzucJ JT3_zV DvypSJ'})

    # Stores particular details in array 
    for product in products:
        try:
            span = product.find_all('span')
            item = [
                product.find('h3').text,    #name
                product.find('a')['href'],  #url
                span[2].text,               #brand
                span[3].text,               #price
                product.find('img')['src']  #image
            ]
            items.append(item)
        except Exception as e:
            pass
    
    logging.info(msg='Successfully scraped site')
    s.close()
    return items


def test_webhook():
    """
    Sends a test Discord webhook notification
    """
    data = {
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": "Testing Webhook",
            "description": "This is just a quick test to ensure the webhook works. Thanks again for using these monitors!",
            "color": int(config.COLOUR),
            "footer": {'text': 'Made by Yasser'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = requests.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(product):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": product[0],
            "url": product[1],
            "thumbnail": {"url": product[4]},
            "color": int(config.COLOUR),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "Brand", "value": product[2]},
                {"name": "Price", "value": product[3]}
            ]

        }]
    }

    result = requests.post(config.WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info("Payload delivered successfully, code {}.".format(result.status_code))


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        # If product is available but not stored - sends notification and stores
        print(item)
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(item)


def monitor():
    """
    Initiates monitor
    """
    print('''\n---------------------------
--- MONITOR HAS STARTED ---
---------------------------\n''')
    print(''' ** Now you will recieve notifications when an item drops or restocks **
This may take some time so you have to leave this script running. It's best to do this on a server (you can get a free one via AWS)!
    
Check out the docs at https://yasserqureshi1.github.io/Sneaker-Monitors/ for more info.
    
Join the Sneakers & Code family via Discord and subscribe to my YouTube channel https://www.youtube.com/c/YasCode\n\n''')
    logging.info(msg='Successfully started monitor')

    # Tests webhook URL
    test_webhook()

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    if config.ENABLE_FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    else:
        proxy_no = 0
        proxy = {} if config.PROXY == [] else {"http": f"http://{config.PROXY[proxy_no]}"}
   
    headers = {
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
    
    # Collecting all keywords (if any)
    keywords = config.KEYWORDS
    while True:
        try:
            # Makes request to site and stores products 
            items = remove_duplicates(scrape_main_site(headers, proxy))
            for item in items:

                if keywords == []:
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
            time.sleep(float(config.DELAY))
            
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.HTTPError,
            requests.exceptions.ProxyError,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.RetryError,
            requests.exceptions.SSLError,
            requests.exceptions.TooManyRedirects
        ) as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            headers['User-Agent'] = user_agent_rotator.get_random_user_agent()
        
            if config.ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif config.PROXY != []:
                proxy_no = 0 if proxy_no == (len(config.PROXY)-1) else proxy_no + 1
                proxy = {"http": f"http://{config.PROXY[proxy_no]}"}

        
        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

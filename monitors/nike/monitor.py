from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

import requests as rq
import urllib3
from fp.fp import FreeProxy

from datetime import datetime
import time

import json
import logging
import traceback

import locations
from config import WEBHOOK, LOCATION, LANGUAGE, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR


logging.basicConfig(filename='nike-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:  
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)


INSTOCK = []

def discord_webhook(title, colour, url, thumbnail, price, style_code):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        'username': USERNAME,
        'avatar_url':  AVATAR_URL,
        'embeds': [{
            'title': title,
            'url': url,
            'thumbnail': {'url': thumbnail},
            'color': int(COLOUR),
            'footer': {'text': 'Developed by GitHub:yasserqureshi1'},
            'timestamp': str(datetime.utcnow()),
            'fields': [
                {'name': 'Colour', 'value': colour},
                {'name': 'Price', 'value': price},
                {'name': 'Style Code', 'value': style_code},
            ]
        }]
    }
    
    result = rq.post(WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def monitor():
    """
    Initiates the monitor
    """
    print('''\n---------------------------------
--- NIKE MONITOR HAS STARTED ---
---------------------------------\n''')
    logging.info(msg='Successfully started monitor')

    # Ensures that first scrape does not notify all products
    start = 1

    # Initialising proxy and headers
    if ENABLE_FREE_PROXY:
        proxy = {'http': proxy_obj.get()}
    elif PROXY != []:
        proxy_no = 0
        proxy = {} if PROXY == [] else {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}
    else:
        proxy = {}
    user_agent = user_agent_rotator.get_random_user_agent()

    while True:
        # Makes request to site and stores products 
        try:
            if LOCATION in locations.___standard_api___:
                to_discord = locations.standard_api(INSTOCK, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start)
            
            else:
                print(f'LOCATION "{LOCATION}" CURRENTLY NOT AVAILABLE. IF YOU BELIEVE THIS IS A MISTAKE PLEASE CREATE AN ISSUE ON GITHUB OR MESSAGE THE #issues CHANNEL IN DISCORD.')
                return
            
            for product in to_discord:
                discord_webhook(product['title'], product['colour'], product['url'], product['thumbnail'], product['price'], product['style_code'])
                print(product['title'])

        except rq.exceptions.RequestException as e:
            logging.error(e)
            logging.info('Rotating headers and proxy')

            # Rotates headers
            user_agent = user_agent_rotator.get_random_user_agent()
            
            if ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif PROXY != []:
                proxy_no = 0 if proxy_no == (len(PROXY)-1) else proxy_no + 1
                proxy = {"http": PROXY[proxy_no], "https": PROXY[proxy_no]}

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

        # Allows changes to be notified
        start = 0

        # User set delay
        time.sleep(float(DELAY))

if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

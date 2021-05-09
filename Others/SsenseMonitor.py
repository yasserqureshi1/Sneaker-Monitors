# No restocks, only releases
from random_user_agent.params import SoftwareName, HardwareType
from random_user_agent.user_agent import UserAgent

from fp.fp import FreeProxy

from bs4 import BeautifulSoup
import requests
import urllib3

from datetime import datetime
import time

import json
import logging
import dotenv

logging.basicConfig(filename='Ssenselog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

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


def discord_webhook(title, id, price, url, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "url": f'https://www.ssense.com/en-gb{url}',
            "thumbnail": {"url": thumbnail},
            "colour": int(CONFIG["COLOUR"]),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "ID", "value": id},
                {"name": "Price", "value": price}
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


def checker(item):
    """
    Determines whether the product status has changed
    """
    return item in INSTOCK


def scrape_main_site(headers, proxy):
    """
    Scrape the Ssense site and adds each item to an array
    """
    items = []

    # Makes request to site
    s = requests.Session()
    url = 'https://www.ssense.com/en-gb/men/shoes/'
    html = s.get(url=url, headers=headers, verify=False, timeout=15, proxies=proxy)
    soup = BeautifulSoup(html.text, 'html.parser')

    data = str(soup.find_all('script')[68]).replace('<script>window.INITIAL_STATE=', '').replace('</script>', '')
    products = json.loads(data)

    # Stores particular details in array
    for i in products['products']['all']:
        item = [
            f"{i['brand']['name']['all']['en']}: {i['name']['all']['en']}",
            i['id'],
            i['price']['formattedPrice'],
            i['image'][0].replace('/__IMAGE_PARAMS__', ''),
            i['url']
        ]
        items.append(item)

    logging.info(msg='Successfully scraped site')
    s.close()
    return items


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(item, start):
    if not checker(item):
        # If product is available but not stored - sends notification and stores
        INSTOCK.append(item)
        if start == 0:
            discord_webhook(
                title=item[0],
                id=item[1],
                price=item[2],
                thumbnail=item[3],
                url=item[4]
            )
            print(item)


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
    proxy = {"http": proxyObject.get()} if proxy_list[0] == "" else {"http": f"http://{proxy_list[proxy_no]}"}
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                         'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}

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
            print(f"Exception found '{e}' - Rotating proxy and user-agent")
            logging.error(e)

            # Rotates headers
            headers = {'User-Agent': user_agent_rotator.get_random_user_agent(),
                       'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                                 'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
            
            if CONFIG['PROXY'] == "":
                # If no optional proxy set, rotates free proxy
                proxy = {"http": proxyObject.get()}

            else:
                # If optional proxy set, rotates if there are multiple proxies
                proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                proxy = {"http": f"http://{proxy_list[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

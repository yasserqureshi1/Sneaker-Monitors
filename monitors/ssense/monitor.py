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

import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

from config import WEBHOOK, ENABLE_FREE_PROXY, FREE_PROXY_LOCATION, DELAY, PROXY, KEYWORDS, USERNAME, AVATAR_URL, COLOUR

logging.basicConfig(filename='ssense-monitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

if ENABLE_FREE_PROXY:
    proxy_obj = FreeProxy(country_id=FREE_PROXY_LOCATION, rand=True)

INSTOCK = []



def discord_webhook(title, id, price, url, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": USERNAME,
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": url,
            "thumbnail": {"url": thumbnail},
            "colour": int(COLOUR),
            "footer": {"text": "Developed by GitHub:yasserqureshi1"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "ID", "value": id},
                {"name": "Price", "value": price}
            ]
        }]
    }

    result = requests.post(WEBHOOK, data=json.dumps(data), headers={"Content-Type": "application/json"})

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


async def get_content(user_agent, proxy):
    if proxy == None:
        browser = await launch()
    else:
        browser = await launch({'http_proxy': proxy})
    page = await browser.newPage()
    await stealth(page)
    await page.emulate({
        'userAgent': user_agent,
        'viewport': {
            'width': 414,
            'height': 736,
            'deviceScaleFactor': 3,
            'isMobile': True,
            'hasTouch': True,
            'isLandscape': False
        }
    })
    await page.goto('https://www.ssense.com/en-gb/men/shoes')
    content = await page.content()
    await page.close()
    return content


def scrape_main_site(user_agent, proxy):
    """
    Scrape the Ssense site and adds each item to an array
    """
    items = []

    # Makes request to site
    html = asyncio.get_event_loop().run_until_complete(get_content(user_agent, proxy))
    soup = BeautifulSoup(html, 'html.parser')

    products = soup.find_all('div', {'class': 'plp-products__product-tile'})
    for product in products:
        prod = str(product.find('script', {'type': 'application/ld+json'})).replace(
            '<script type="application/ld+json">',
            ''
        ).replace('</script>','')
        prod = json.loads(prod)
        item = [
            prod["name"],
            prod["productID"],
            prod["offers"]["price"],
            prod["image"],
            "https://www.ssense.com/en-gb"+prod["url"]
        ]
        items.append(item)

    logging.info(msg='Successfully scraped site')
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
    print('''\n----------------------------------
--- SSENSE MONITOR HAS STARTED ---
----------------------------------\n''')
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
        try:
            # Makes request to site and stores products
            items = remove_duplicates(scrape_main_site(user_agent, proxy))
            for item in items:

                if KEYWORDS == []:
                    # If no keywords set, checks whether item status has changed
                    comparitor(item, start)

                else:
                    # For each keyword, checks whether particular item status has changed
                    for key in KEYWORDS:
                        if key.lower() in item[0].lower():
                            comparitor(item, start)

            # Allows changes to be notified
            start = 0

        except requests.exceptions.RequestException as e:
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

        # User set delay
        time.sleep(float(DELAY))


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

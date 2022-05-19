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

import config

logging.basicConfig(filename='ssense.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)

proxy_obj = FreeProxy(country_id=[config.FREE_PROXY_LOCATION], rand=True)

INSTOCK = []

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
        logging.error(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def discord_webhook(title, id, price, url, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": config.USERNAME,
        "avatar_url": config.AVATAR_URL,
        "embeds": [{
            "title": title,
            "url": url,
            "thumbnail": {"url": thumbnail},
            "colour": int(config.COLOUR),
            "footer": {"text": "Made by Yasser"},
            "timestamp": str(datetime.utcnow()),
            "fields": [
                {"name": "ID", "value": id},
                {"name": "Price", "value": price}
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
    user_agent = user_agent_rotator.get_random_user_agent()

    # Collecting all keywords (if any)
    keywords = config.KEYWORDS
    while True:
        try:
            # Makes request to site and stores products
            items = remove_duplicates(scrape_main_site(user_agent, proxy))
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

        except Exception as e:
            print(f"Exception found: {traceback.format_exc()}")
            logging.error(e)

            # Rotates headers
            user_agent = user_agent_rotator.get_random_user_agent()
            
            if config.ENABLE_FREE_PROXY:
                proxy = {'http': proxy_obj.get()}

            elif config.PROXY != []:
                proxy_no = 0 if proxy_no == (len(config.PROXY)-1) else proxy_no + 1
                proxy = {"http": f"http://{config.PROXY[proxy_no]}"}


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

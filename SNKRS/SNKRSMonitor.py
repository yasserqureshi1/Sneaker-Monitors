import requests as rq
import json
import time
import datetime
import urllib3
import logging
import dotenv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy

logging.basicConfig(filename='SNKRSlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=[CONFIG['LOCATION']], rand=True)

INSTOCK = []


def scrape_site(headers, proxy):
    """
    Scrapes SNKRS site and adds items to array
    :return: None
    """
    items = []
    anchor = 0
    while anchor < 180:
        url = f'https://api.nike.com/product_feed/threads/v2/?anchor={anchor}&count=60&filter=marketplace%28{CONFIG["LOC"]}%29&filter=language%28{CONFIG["LAN"]}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'

        html = rq.get(url=url, timeout=20, verify=False, headers=headers, proxies=proxy)
        output = json.loads(html.text)
        for item in output['objects']:
            items.append(item)
            logging.info(msg='Successfully scraped SNKRS site')

        anchor += 60
        time.sleep(float(CONFIG['DELAY']))
    return items


def checker(product, colour):
    """
    Determines whether the product status has changed
    :param product: Shoe name
    :param colour: Shoe colour
    :return: None
    """
    for item in INSTOCK:
        if item == [product, colour]:
            return True
    return False


def discord_webhook(title, colour, slug, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param title: Shoe name
    :param colour: Shoe Colour
    :param slug: Shoe URL
    :param thumbnail: URL to shoe image
    :return: None
    """
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if title != '' and colour != '' and slug != '':
        embed["title"] = title
        embed["fields"] = [{'name': 'Colour', 'value': colour}]
        embed["url"] = f'https://www.nike.com/{CONFIG["LOC"]}/launch/t/' + slug
        embed["thumbnail"] = {'url': thumbnail}
    else:
        embed["description"] = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know " \
                               "that everything is working fine! You can find more monitoring solutions at " \
                               "https://github.com/yasserqureshi1/Sneaker-Monitors "
    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'Made by Yasser'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    :param mylist: list
    :return: list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(j, start):
    if checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
        pass
    else:
        INSTOCK.append([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
        if start == 0:
            print('Sending notification to Discord...')
            discord_webhook(j['merchProduct']['labelName'], j['productContent']['colorDescription'],
                            j['productContent']['slug'], j['imageUrls']['productImageUrl'])
            logging.info(msg='Sending new notification')


def monitor():
    """
    Initiates the monitor
    :return: None
    """
    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook(title='', slug='', colour='', thumbnail='')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else proxy_list[proxy_no]
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        items = scrape_site(proxy, headers)
        for item in items:
            try:
                for j in item['productInfo']:
                    if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                        check = False
                        if keywords == "":
                            comparitor(j, start)
                        else:
                            for key in keywords:
                                if key.lower() in j['merchProduct']['labelName'].lower() or key.lower() in j['productContent']['colorDescription'].lower():
                                    check = True
                                    break
                            if check:
                                comparitor(j, start)
                    else:
                        if checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                            INSTOCK.remove([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
            except rq.exceptions.HTTPError as e:
                print(f"Exception found '{e}' - Rotating proxy and user-agent")
                logging.error(e)
                headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
                if CONFIG['PROXY'] == "":
                    proxy = {"http": f"http://{proxyObject.get()}"}
                else:
                    proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                    proxy = proxy_list[proxy_no]
            except Exception as e:
                logging.error(e)
        start = 0


if __name__ == '__main__':
    urllib3.disable_warnings()
    monitor()

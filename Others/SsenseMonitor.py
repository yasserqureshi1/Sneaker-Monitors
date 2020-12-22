# No restocks, only releases
import requests
import datetime
import json
from bs4 import BeautifulSoup
import urllib3
import time
import logging
import dotenv

logging.basicConfig(filename='Ssenselog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)
CONFIG = dotenv.dotenv_values(dotenv_path='.env')


class SsenseBot:
    def __init__(self, webhook, proxy):
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'}
        self.all_items = []
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"https": f"https://{proxy}"}

    def discord_webhook(self, product_item):
        """
        Sends a Discord webhook notification to the specified webhook URL
        :param product_item: An array of the product's details
        :return: None
        """
        data = {}
        data["username"] = CONFIG['USERNAME']
        data["avatar_url"] = CONFIG['AVATAR_URL']
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0]  # Item Name
        embed["description"] = product_item[1]
        embed['url'] = f'https://www.ssense.com{product_item[2]}'  # Item link
        embed["color"] = int(CONFIG['COLOUR'])
        embed["thumbnail"] = {'url': product_item[3]}  # Item image
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            logging.error(msg=err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info("Payload delivered successfully, code {}.".format(result.status_code))

    def checker(self, item):
        """
        Determines whether the product status has changed
        :param item: list of item details
        :return: Boolean whether the status has changed or not
        """
        for product in self.instock_copy:
            if product == item:
                self.instock_copy.remove(product)
                return True
        return False

    def scrape_main_site(self):
        """
        Scrape the Ssense site and adds each item to an array
        :return: None
        """
        s = requests.Session()
        try:
            html = s.get('https://www.ssense.com/en-gb/men/shoes/', headers=self.headers, verify=False, timeout=10, proxies=self.proxy)
            soup = BeautifulSoup(html.text, 'html.parser')
            array = soup.find_all('div', {'class': 'plp-products__column'})
            for i in array:
                item = [i.find('span', {'class': 's-text s-text--uppercase'}).text,
                        i.find('div', {'class': 'product-tile__description'}).text.replace(
                            i.find('span', {'class': 's-text'}).text, '').split('£')[0], i.find('a')['href'],
                        i.find('img')['data-srcset']]
                self.all_items.append(item)
            logging.info(msg='Successfully scraped site')
        except Exception as e:
            print('There was an Error - main site - ', e)
            logging.error(msg=e)
        s.close()

    def remove_duplicates(self, mylist):
        """
        Removes duplicate values from a list
        :param mylist: list
        :return: list
        """
        return [list(t) for t in set(tuple(element) for element in mylist)]

    def monitor(self):
        """
        Initiates monitor
        :return: None
        """
        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        start = 1
        while True:
            self.scrape_main_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_copy = self.instock.copy()
            for item in self.all_items:
                if not self.checker(item):
                    self.instock.append(item)
                    if start == 0:
                        self.discord_webhook(item)
                        print(item)
            start = 0
            time.sleep(0.1)


if __name__ == '__main__':
    urllib3.disable_warnings()
    bot = SsenseBot(webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY'])
    bot.monitor()

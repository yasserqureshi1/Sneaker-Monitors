# No restocks, only releases
import requests
import datetime
import json
from bs4 import BeautifulSoup
import urllib3
import time
import logging
import dotenv

logging.basicConfig(filename='Footlockerlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class FootlockerBot:
    def __init__(self, webhook, proxy):
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.all_items = []
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"http": f"http://{proxy}"}

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
        if product_item == 'initial':
            embed["description"] = "Thank you for using Yasser's Sneaker Monitors. This message is to let you know " \
                                   "that everything is working fine! You can find more monitoring solutions at " \
                                   "https://github.com/yasserqureshi1/Sneaker-Monitors "
        else:
            embed["title"] = product_item[0]
            embed["description"] = f'{product_item[1]} \n*Colour:* {product_item[2]}'
            embed["thumbnail"] = {'url': product_item[3]}
            embed['url'] = f'https://www.footlocker.ca{product_item[4]}'
        embed["color"] = int(CONFIG['COLOUR'])
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.utcnow())
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
        Scrape the Footlocker site and adds each item to an array
        :return: None
        """
        s = requests.Session()
        try:
            url = 'https://www.footlocker.com.au/en/men/'
            html = s.get(url=url, headers=self.headers, proxies=self.proxy, verify=False, timeout=10)
            soup = BeautifulSoup(html.text, 'html.parser')
            array = soup.find_all('div', {'class': 'fl-category--productlist--item'})
            for i in array:
                item = [i.find('span', {'class': 'ProductName-primary'}).text,
                        i.find('span', {'class': 'ProductName-alt'}).text.split(chr(8226))[0],
                        i.find('span', {'class': 'ProductName-alt'}).text.split(chr(8226))[1],
                        i.find('img')['src'],
                        i.find('a', {'class': 'ProductCard-link ProductCard-content'})['href']]
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
        self.discord_webhook('initial')
        start = 1
        while True:
            self.scrape_main_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_copy = self.instock.copy()
            for item in self.all_items:
                if self.checker(item):
                    pass
                else:
                    self.instock.append(item)
                    if start == 0:
                        print(item)
                        self.discord_webhook(item)
            start = 0
            time.sleep(1)


if __name__ == '__main__':
    urllib3.disable_warnings()
    bot = FootlockerBot(webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY']).monitor()

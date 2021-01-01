import requests as rq
import json
import time
from datetime import datetime
import urllib3
import logging
import dotenv


logging.basicConfig(filename='suplog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)
CONFIG = dotenv.dotenv_values()


class SupremeMonitor:
    def __init__(self, webhook, proxy):
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.instock = []
        self.webhook = webhook
        if proxy is None:
            self.proxy = {}
        else:
            self.proxy = {"http": f"http://{proxy}"}

    def get_stock(self):
        """
        Makes a request to Supreme's mobile_stock endpoint.
        Return its content.
        """

        url = "https://www.supremenewyork.com/mobile_stock.json"
        stock = rq.get(url, headers=self.headers, proxies=self.proxy, timeout=10).json()['products_and_categories']

        return stock

    def get_item_variants(self, item_id, item_name, start):
        """
        Scrapes each item on the webstore and checks whether the product is in-stock or not. If in-stock
        it will send a Discord notification
        """

        item_url = f"https://www.supremenewyork.com/shop/{item_id}.json"

        item_variants = rq.get(item_url, headers=self.headers, proxies=self.proxy).json()

        for stylename in item_variants["styles"]:
            for itemsize in stylename["sizes"]:
                item = [item_name, stylename["name"], itemsize['name'], item_variants["description"], 'https:' + stylename["image_url"], item_url.split('.json')[0]]
                if itemsize["stock_level"] != 0:
                    # Checks if it already exists in our instock
                    if self.checker(item):
                        pass
                    else:
                        # Add to instock dict
                        self.instock.append(item)
                        
                        # Send a notification to the discord webhook with the in-stock product
                        if start == 0:
                            print('Sending new Notification')
                            self.discord_webhook(item)
                            logging.info(msg='Successfully sent Discord notification')

                else:
                    if self.checker(item):
                        self.instock.remove(item)

    def discord_webhook(self, product_item):
        """
        Sends a Discord webhook notification to the specified webhook URL
        :param product_item: A list of the product's details
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
            embed["title"] = product_item[0] + ' - ' + product_item[1] + ' - ' + product_item[2]
            embed["description"] = product_item[3]
            embed["thumbnail"] = {'url': product_item[4]}
            embed['url'] = product_item[5]

        embed["color"] = CONFIG['COLOUR']
        embed["footer"] = {'text': 'Made by Yasser & Bogdan'}
        embed["timestamp"] = str(datetime.utcnow())
        data["embeds"].append(embed)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            print(err)
            logging.error(msg=err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))
            logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))

    def checker(self, product):
        """
        Determines whether the product status has changed
        :return: Boolean whether the status has changed or not
        """
        for item in self.instock:
            if item == product:
                return True
        return False

    def monitor(self):
        """
        Initiates the monitor
        :return: None
        """
        print('STARTING MONITOR')
        logging.info(msg='Successfully started monitor')
        initial = ['','','',"Thank you for using Yasser's Sneaker Monitors. This message is to let you know that "
                            "everything is working fine! You can find more monitoring solutions at "
                            "https://github.com/yasserqureshi1/Sneaker-Monitors",'','']
        self.discord_webhook(initial)
        start = 1
        while True:
            try:
                stock = self.get_stock()
                time.sleep(0.5)
                for cat in stock:
                    for product_item in stock[cat]:
                        self.get_item_variants(product_item['id'], product_item['name'], start)
                        time.sleep(0.5)
                start = 0
                logging.info(msg='Successfully monitored site')
            except:
                pass


if __name__ == '__main__':
    urllib3.disable_warnings()
    SupremeMonitor(webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY']).monitor()

import requests as rq
import json
import time
import datetime
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
        stock = rq.get(url, headers=self.headers, proxies=self.proxy).json()['products_and_categories']

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
        
        # Item Name and Style Name
        embed["title"] = product_item[0] + ' - ' + product_item[1] + ' - ' + product_item[2]

        # Product Description
        if product_item[3]:
            embed["description"] = product_item[3]

        # Product Link
        embed['url'] = product_item[5]

        embed["color"] = CONFIG['COLOUR']

        # Product Image
        embed["thumbnail"] = {'url': product_item[4]}

        embed["footer"] = {'text': 'Made by Yasser & Bogdan'}
        embed["timestamp"] = str(datetime.datetime.now())
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
        start = 1
        while True:
            stock = self.get_stock()
            time.sleep(1)
            for cat in stock:
                for product_item in stock[cat]:
                    self.get_item_variants(product_item['id'], product_item['name'], start)
                    time.sleep(1)
            start = 0
            logging.info(msg='Successfully monitored site')


if __name__ == '__main__':
    urllib3.disable_warnings()
    supremeMonitor = SupremeMonitor(webhook=CONFIG['WEBHOOK'], proxy=CONFIG['PROXY'])
    supremeMonitor.monitor()

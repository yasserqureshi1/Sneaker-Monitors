# For the Palace Site Site (Type of Shopify Store)

import requests as rq
import json
import time


class PalaceMonitor:
    def __init__(self, webhook):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock_products = []
        self.instock_products_copy = []
        self.webhook = webhook

    def scrape_site(self):
        self.pages.clear()
        s = rq.Session()
        num = 1
        # scrape each product page
        while num > 0:
            try:
                html = s.get(
                    'https://shop.palaceskateboards.com/collections/all/products.json?page=' + str(num) + '&limit=250',
                    headers=self.headers, verify=False, timeout=1)
                output = json.loads(html.text)['products']
                if output == []:
                    # once there are no more products - exit loop
                    num = 0
                else:
                    # add product page to list
                    self.pages.append(output)
                    num = num + 1
            except:
                print('There was an Error')
                num = 0

    def checker(self, product, size):
        # check if item is in list
        for item in self.instock_products_copy:
            if item == [product, size]:
                self.instock_products_copy.remove([product, size])
                return True
        return

    def discord_notification(self, title, shoe_size):
        data = {}
        data["username"] = "Palace Monitor"

        data["embeds"] = []
        embed = {}
        embed["title"] = title
        embed["description"] = shoe_size
        embed["color"] = 15258703
        data["embeds"].append(embed)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def monitor(self):
        while True:
            self.scrape_site()
            self.instock_products_copy = self.instock_products.copy()
            for page in self.pages:
                for product in page:
                    for size in product['variants']:
                        # if the product is available....
                        if size['available'] == True:
                            # check if product is already stored ...
                            if self.checker(product['title'], size['title']):
                                # nothing
                                pass
                            # if not, means its a restock or a newly added item ...
                            else:
                                self.instock_products.append([product['title'], size['title']])
                                # restock = 'RESTOCK: ' + str(product['title']) + ' in size ' + str(size['title'])
                                # message = {"content": restock}
                                # print(message)
                                self.discord_notification(product['title'], size['title'])
                                # sends message to discord
                                #rq.post(discord_webhook_url, data=message)

                        # if not available, but stored, remove it
                        else:
                            if self.checker(product['title'], size['title']):
                                self.instock_products.remove([product['title'], size['title']])
            time.sleep(3)


if __name__ == '__main__':
    discord_webhook_url = ''
    test = PalaceMonitor(discord_webhook_url)
    test.monitor()


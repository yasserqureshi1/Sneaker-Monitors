# Problem:
# - Most sites dont have stock inventory in their single product .json files (only on the dir before)
# - Some sites use "inventory_quantity":1,"old_inventory_quantity":1 (e.g. https://stay-rooted.com/)
# TODO Find other way of scraping info (possibly backtracking through javascript, or using headless selenium)

import requests as rq
import json
import time
import datetime


class ShopifyMonitor:
    def __init__(self, list_of_urls, webhook):
        self.list_of_urls = list_of_urls
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock_products = []
        self.instock_products_copy = []
        self.webhook = webhook

    def scrape_site(self, url):
        self.pages.clear()
        s = rq.Session()
        try:
            # html = s.get(self.url + str(num) + '&limit=250', headers=self.headers, verify=False, timeout=1)
            html = s.get(url, headers=self.headers, verify=False, timeout=1)
            output = json.loads(html.text)['product']
            if output == []:
                pass
            else:
                self.pages.append(output)
        except:
            print('There was an Error')

        s.close()

    def checker(self, product, size):
        # check if item is in list
        for item in self.instock_products_copy:
            if item == [product, size]:
                self.instock_products_copy.remove([product, size])
                return True
        return


    def item_stock_checker(self, list, item):
        try:
            # inventory_quantity and old_inventory_quantity

        except:
            try:
                # Check previous directory
            except:
                # Try Javascript method

    def discord_webhook(self, product_item, url):
        description = ''
        for i in range(len(product_item[1])):
            if i % 2 == 1:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '\n'
            else:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '     |     '
        link = url.replace('.json', '/') + product_item[3]

        data = {}
        data["username"] = "Nike SNKRS EU"
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0]
        embed["description"] = '**Size Restock:** \n' + description
        embed['url'] = link
        embed["color"] = 15258703
        embed["image"] = {'url': product_item[2]}
        embed["footer"] = {'text': 'Made by Yasser Qureshi'}
        embed["timestamp"] = str(datetime.datetime.now())
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
            for url in self.list_of_urls:
                self.scrape_site(url)
                self.instock_products_copy = self.instock_products.copy()
                for product in self.pages:
                    product_item = [product['title'], [], product['images'][0]['src'], product['handle']]
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
                                product_item[1].append(size['title'])
                    
                        # if not available, but stored, remove it
                        else:
                            if self.checker(product['title'], size['title']):
                                self.instock_products.remove([product['title'], size['title']])
                    
                    if product_item[1] == []:
                        pass
                    else:
                        self.discord_webhook(product_item, url)
                        print(product_item)
                time.sleep(3)


if __name__ == '__main__':
    webhook = ''
    urls = ['https://www.hanon-shop.com/collections/whats-new/products/nike-air-max-iii-cj6779100.json',
            'https://www.hanon-shop.com/collections/whats-new/products/nike-jordan-zoom-92-ck9183103.json']
    test = ShopifyMonitor(urls, webhook)
    # test.check_url()
    test.monitor()


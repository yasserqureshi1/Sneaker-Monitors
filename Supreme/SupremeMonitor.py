# Fix Discord notification

import requests as rq
import json
import time
import datetime


class SupremeMonitor:
    def __init__(self):
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, '
                                      'like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        self.pages = []
        self.instock = []
        self.instock_copy = []

    def scrape_main_site(self):
        self.pages.clear()
        s = rq.Session()
        try:
            html = s.get('https://www.supremenewyork.com/mobile_stock.json', headers=self.headers, verify=False,
                         timeout=1)
            output = json.loads(html.text)['products_and_categories']
            self.pages.append(output)
        except:
            print('There was an Error')

    def scrape_item_site(self, name, id):
        try:
            url = 'https://www.supremenewyork.com/shop/' + str(id) + '.json'
            html = rq.get(url, headers=self.headers, verify=False, timeout=0.3)
            output = json.loads(html.text)['styles']

            for colour in output:
                for size in colour['sizes']:
                    if size['stock_level'] == 1:
                        if self.checker(name, colour['name'], size['name']):
                            pass
                        else:
                            self.instock.append([name, colour['name'], size['name']])
                            restock = 'RESTOCK: ' + str(name) + ' in ' + str(colour['name']) + ' in size ' + str(
                                size['name'])
                            print(restock)
                            message = {"content": restock}
                            #rq.post(discord_webhook_url, data=message)
                    else:
                        if self.checker(name, colour['name'], size['name']):
                            self.instock.remove([name, colour['name'], size['name']])
        except:
            print('There was an Error')

    def checker(self, product, colour, size):
        # check if item is in list
        for item in self.instock_copy:
            if item == [product, colour, size]:
                self.instock_copy.remove([product, colour, size])
                return True
        return False

    def discord_webhook(self, product_item):
        description = ''
        for i in range(len(product_item[1])):
            if i % 2 == 1:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '\n'
            else:
                description = description + str(product_item[1][i].replace(' : ', '/')) + '\t\t'

        link = self.url.replace('.json', '/') + product_item[3]

        data = {}
        data["username"] = "[insert name]"
        data["avatar_url"] = '[insert image url]'
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0]
        embed["description"] = "**SHOP: **" + self.url.split('.com/')[0] + '.com/ \n\n' + '**SIZES:** \n' + description
        embed['url'] = link
        embed["color"] = 15258703
        embed["thumbnail"] = {'url': product_item[2]}
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
            self.scrape_main_site()
            self.instock_copy = self.instock.copy()
            for cat in self.pages:
                for i in cat:
                    for j in cat[i]:
                        self.scrape_item_site(j['name'], j['id'])


if __name__ == '__main__':
    t0 = time.time()
    discord_webhook_url = ''
    test = SupremeMonitor()
    test.monitor()
    t1 = time.time()
    print('Time Taken: ', t1 - t0)


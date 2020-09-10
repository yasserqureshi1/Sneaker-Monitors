import requests as rq
import json
import time
import datetime


class SupremeMonitor:
    def __init__(self, webhook):
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.pages = []
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook
        self.first = 1

    def discord_webhook(self, product_item):
        description = ''
        for i in range(len(product_item[4])):
            if i % 2 == 1:
                description = description + str(product_item[4][i].replace(' : ', '/')) + '\n'
            else:
                description = description + str(product_item[4][i].replace(' : ', '/')) + '\t\t'

        data = {}
        data["username"] = "Supreme Monitor"
        data["avatar_url"] = 'https://lh3.googleusercontent.com/lPUZwKE_VV6_UxQOE_MlXVSYi77LssHVK0T9zZFFERORHI7ZhQXD-WvsMKXu5822NQ'
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0] + ' - ' + product_item[1]               # Item Name
        if description != '':
            embed["description"] = '**SIZES:** \n' + description                     # Item Sizes
        embed['url'] = product_item[3]                                           # Item link
        embed["color"] = 15258703
        embed["thumbnail"] = {'url': product_item[2]}                            # Item image
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)
        print(data)

        result = rq.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except rq.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def scrape_main_site(self):
        self.pages.clear()
        s = rq.Session()
        try:
            html = s.get('https://www.supremenewyork.com/mobile_stock.json', headers=self.headers, verify=False,
                         timeout=3)
            output = json.loads(html.text)['products_and_categories']
            self.pages.append(output)
        except Exception as e:
            print('There was an Error - main site - ', e)

    def scrape_item_site(self, name, id):
        try:
            url = 'https://www.supremenewyork.com/shop/' + str(id) + '.json'
            html = rq.get(url, headers=self.headers, verify=False, timeout=3)
            output = json.loads(html.text)['styles']

            for colour in output:
                instock = [name, colour['name'], 'https:' + colour['image_url'], url.split('.json')[0], []]
                for size in colour['sizes']:
                    if size['stock_level'] == 1:
                        if self.checker(name, colour['name'], size['name']):
                            pass
                        else:
                            instock[4].append(size['name'])
                            self.instock.append([name, colour['name'], size['name']])

                    else:
                        if self.checker(name, colour['name'], size['name']):
                            self.instock.remove([name, colour['name'], size['name']])

                if instock[1] == [] or self.first == 1:
                    pass
                else:
                    self.discord_webhook(instock)
        except Exception as e:
            print('There was an Error - single site - ', e)

    def checker(self, product, colour, size):
        for item in self.instock_copy:
            if item == [product, colour, size]:
                self.instock_copy.remove([product, colour, size])
                return True
        return False

    def monitor(self):
        while True:
            self.scrape_main_site()
            time.sleep(1)
            self.instock_copy = self.instock.copy()
            for cat in self.pages:
                for i in cat:
                    for j in cat[i]:
                        self.scrape_item_site(j['name'], j['id'])
                        time.sleep(1)
            self.first = 0


if __name__ == '__main__':
    discord_webhook_url = ''
    test = SupremeMonitor(webhook=discord_webhook_url)
    test.monitor()

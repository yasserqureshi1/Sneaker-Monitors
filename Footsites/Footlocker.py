# No restocks, only releases
import requests
import datetime
import json
from bs4 import BeautifulSoup
import time


class FootlockerBot:
    def __init__(self, webhook):
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.all_items = []
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook

    def discord_webhook(self, product_item):
        data = {}
        data["username"] = "Footlocker Monitor"
        data["avatar_url"] = 'https://therockbury.com/wp-content/uploads/2014/03/footlocker-logo.jpg'
        data["embeds"] = []
        embed = {}
        embed["title"] = product_item[0]            # Item Name
        # if description != '':
        #     embed["description"] = '**SIZES:** \n' + description                     # Item Sizes
        embed['url'] = product_item[1]                                           # Item link
        embed["color"] = 12845619
        #embed["thumbnail"] = {'url': product_item[2]}                            # Item image
        embed["footer"] = {'text': 'Made by Yasser'}
        embed["timestamp"] = str(datetime.datetime.now())
        data["embeds"].append(embed)

        result = requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

    def checker(self, item):
        for product in self.instock_copy:
            if product == item:
                self.instock_copy.remove(product)
                return True
        return False

    def scrape_main_site(self):
        s = requests.Session()
        try:
            html = s.get('https://www.footlocker.co.uk/en/men/shoes/', headers=self.headers, verify=False, timeout=3)
            soup = BeautifulSoup(html.text, 'html.parser')
            array = soup.find_all('div', {'class': 'fl-category--productlist--item'})
            for i in array:
                self.all_items.append([i.find('span', {'itemprop': 'name'}).text, i.find('a')['href']])
        except Exception as e:
            print('There was an Error - main site - ', e)
        s.close()

    def remove_duplicates(self, mylist):
        return [list(t) for t in set(tuple(element) for element in mylist)]

    def monitor(self):
        print('STARTING MONITOR')
        while True:
            self.scrape_main_site()
            self.all_items = self.remove_duplicates(self.all_items)
            self.instock_copy = self.instock.copy()
            for item in self.all_items:
                if self.checker(item):
                    pass
                else:
                    self.instock.append(item)
                    print(item)
                    self.discord_webhook(item)


if __name__ == '__main__':

    webhook = ''
    bot = FootlockerBot(webhook)
    bot.monitor()

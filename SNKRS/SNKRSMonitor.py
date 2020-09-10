import requests as rq
import json
import time


class SNKRSMonitor:
    def __init__(self, webhook):
        self.url = ['https://api.nike.com/product_feed/threads/v2/?anchor=', '&count=&filter=marketplace%28GB%29&filter' \
                   '=language%28en-GB%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter' \
                   '=exclusiveAccess%28true%2Cfalse%29&fields=active%2Cid%2ClastFetchTime%2CproductInfo' \
                   '%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard' \
                   '%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products' \
                   '%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads' \
                   '%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent' \
                   '.properties.custom%2CpublishedContent.properties.title']
        self.headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        self.items = []
        self.number_of_items = 50
        self.instock = []
        self.instock_copy = []
        self.webhook = webhook

    def get_data(self):
        no_of_pages = self.number_of_items//50
        anchor = 0
        while no_of_pages != 0:
            try:
                html = rq.get(url=self.url[0] + str(anchor) + self.url[1], timeout=5, verify=False, headers=self.headers)
                output = json.loads(html.text)
                for item in output['objects']:
                    self.items.append(item)
            except:
                print('Error')
            anchor += 50
            no_of_pages -= 1

    def checker(self, product, colour):
        # check if item is in list
        for item in self.instock_copy:
            if item == [product, colour]:
                self.instock_copy.remove([product, colour])
                return True
        return

    def discord_webhook(self, title, size):
        data = {}
        data["username"] = "Nike SNKRS EU"
        data["avatar_url"] = ''
        data["embeds"] = []
        embed = {}
        embed["title"] = title
        embed["description"] = 'Size Restock: {}'.format(size)
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
            self.get_data()
            self.instock_copy = self.instock.copy()
            for item in self.items:
                try:
                    for j in item['productInfo']:
                        if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                            if self.checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                                #print('f')
                                # nothing
                                pass
                            else:
                                self.instock.append([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
                                #self.discord_webhook(j['merchProduct']['labelName'], j['productContent']['colorDescription'])
                                restock = 'RESTOCK: ' + str(j['merchProduct']['labelName']) + ' in size ' + str(j['productContent']['colorDescription'])
                                print(restock)
                        else:
                            if self.checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                                self.instock.remove([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
                except:
                    pass
                self.items.remove(item)
            time.sleep(5)


if __name__ == '__main__':
    url = ''
    test = SNKRSMonitor(url)
    #test.get_data()
    test.monitor()

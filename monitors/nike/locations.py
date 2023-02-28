import requests 
import json

___standard_api___ = [
    'GB', 'US', 'AU', 'AT', 'BE', 'BG', 'CA', 'CN', 'HR', 'CZ', 'DK', 'EG', 
    'FI', 'FR', 'DE', 'HU', 'IN', 'ID', 'IE', 'IT', 'MY', 'MX', 'MA', 'NL', 
    'NZ', 'NO', 'PH', 'PL', 'PT', 'PR', 'RO', 'RU', 'SA', 'SG', 'SI', 'ZA', 
    'ES', 'SE', 'CH', 'TR', 'AE', 'VN', 'JP' 
]

def standard_api(ITEMS, LOCATION, LANGUAGE, user_agent, proxy, KEYWORDS, start):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9',
        'dnt': '1',
        'origin': 'https://www.nike.com',
        'referer': 'https://www.nike.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }

    to_discord = []
    
    anchor = 0
    while anchor < 181:
        print('-- scrape --')
        url = f'https://api.nike.com/cic/browse/v2?queryid=products&anonymousId=3BCF9783E5B8CEB165B9DB2C449B7F26&country={LOCATION}&endpoint=%2Fproduct_feed%2Frollup_threads%2Fv2%3Ffilter%3Dmarketplace({LOCATION})%26filter%3Dlanguage({LANGUAGE})%26filter%3DemployeePrice(true)%26filter%3DattributeIds(0f64ecc7-d624-4e91-b171-b83a03dd8550%2C16633190-45e5-4830-a068-232ac7aea82c)%26anchor%3D{anchor}%26consumerChannelId%3Dd9a5bc42-4b9c-4976-858a-f159cf99c647%26count%3D60%26sort%3DeffectiveStartViewDateDesc&language=en-GB&localizedRangeStr=%7BlowestPrice%7D%E2%80%94%7BhighestPrice%7D'
        html = requests.get(url=url, timeout=20, headers=headers, proxies=proxy)
        output = json.loads(html.text)

        for item in output['data']['products']['products']:
            for variant in item['colorways']:
                if KEYWORDS == []:
                    if (variant['inStock'] == True) and (variant['pid'] not in ITEMS):
                        if start == 0:
                            to_discord.append(dict(
                                title=item['title'],
                                colour=variant['colorDescription'],
                                url=f"https://www.nike.com/{LOCATION}/{variant['pdpUrl'].replace('{countryLang}', LANGUAGE)}",
                                thumbnail=variant['images']['squarishURL'],
                                price=str(variant['price']['currentPrice']),
                                style_code=variant['pdpUrl'].split('/')[-1]
                            ))

                    elif (variant['inStock'] == False) and (variant['pid'] in ITEMS):
                        ITEMS.remove(variant['id'])
                
                else:
                    for key in KEYWORDS:
                        if key.lower() in item['title'].lower():
                            if start == 0:
                                to_discord.append(dict(
                                    title=item['title'],
                                    colour=variant['colorDescription'],
                                    url=f"https://www.nike.com/{LOCATION}/{variant['pdpUrl'].replace('{countryLang}', LANGUAGE)}",
                                    thumbnail=variant['images']['squarishURL'],
                                    price=str(variant['price']['currentPrice']),
                                    style_code=variant['pdpUrl'].split('/')[-1]
                                ))
                
        anchor += 60
    return to_discord
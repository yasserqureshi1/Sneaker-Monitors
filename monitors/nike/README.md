# Nike Monitor

Watches Nike for new arrivals (men's shoes) in your country and posts them to your Discord. Looking for SNKRS launch drops instead? Use the [SNKRS monitor](../snkrs).

## Setup

Open [`config.py`](config.py) and set your country and language codes (use the table below):

```python
LOCATION = "GB"       # 2-letter country code
LANGUAGE = "en-GB"    # matching language code
```

If your country isn't listed, Nike runs a different setup there and may need a dedicated fix — open a GitHub issue or ask in the [Discord](https://discord.gg/b6zyJyCQUu).

Country | 2 Letter Country Code | Language Code
--------|-----------------------|--------------
United Kingdom | GB | en-GB
United States | US | en
Australia | AU | en-GB
Austria | AT | en-GB / de
Belgium | BE | en-GB / nl / de / fr
Bulgaria | BG | en-GB
Canada | CA | en-GB / fr
Chile | CL | es-419
China | CN | zh-Hans
Croatia | HR | en-GB
Czechia | CZ | en-GB / cs
Denmark | DK | en-GB / da
Egypt | EG | en-GB
Finland | FI | en-GB
France | FR | fr
Germany | DE | de
Hungary | HU | en-GB
India | IN | en-GB
Indonesia | ID | en-GB
Ireland | IE | en-GB
Italy | IT | it
Malaysia | MY | en-GB
Mexico | MX | es-419
Morocco | MA | en-GB / fr
Netherlands | NL | en-GB / nl 
New Zealand | NZ | en-GB
Norway | NO | en-GB / no
Philippines | PH | en-GB 
Poland | PL | pl
Portugal | PT | en-GB / es-419
Puerto Rico | PR | es-419
Romania | RO | en-GB / 
Russia | RU | ru
Saudi Arabia | SA | en-GB
Singapore | SG | en-GB
Slovenia | SI | en-GB   
South Africa | ZA | en-GB
Spain | ES | es-ES / ca
Sweden | SE | en-GB / sv
Switzerland | CH | en-GB / fr / de / it 
Turkey | TR | tr
UAE | AE | en-GB
Vietnam | VN | en-GB


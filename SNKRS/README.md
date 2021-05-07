# Sneaker Monitors: SNKRS Monitor

This will outline how to use the SNKRS Monitor

If set up properly, the monitor can work in a variety of countries.
Below is a list of the countries that the monitor supports.

To set up the monitor, please put the 2 letter country code into the ```LOC``` variable and one of the corresponding language codes in the ```LAN``` variable found in the ```.env``` file.
See the table below for the country codes and language codes.

For example, if I want a monitor for Belgium, there are multiple languages to choose from.
Looking at the table, I have the choices of ```en-GB```, ```nl```, ```de``` or ```fr```.
If I then want the monitor to refer to the Belgium site in the French language, I can put the following into the ```.env``` file:
```
LOCATION = "BE"
LANGUAGE = "fr"
```

If your country is not found below, it is because Nike use a different set-up.
As a result, we cannot cater to your country.

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


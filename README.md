# Sneaker Monitors
A collection of web monitors that notify of restocks or updates on sneaker related sites through Discord Webhook.

If you have any requests for sites, please let me know via Discord at @TheBrownPanther2#3801

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/YasserQureshi1)

##### NOTE: Info on the Footsites monitor will be updated soon

## Installation
The following modules are required:
```
requests
json
time
datetime
urllib3
logging
```
For the Footsites monitor, you also need:
```
bs4
```

## Introduction

This repo contains different monitors to various sites to notify if a restock or update occurs via Discord Webhook. A list of all the sites are detailed below:
- All shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS
- Footsites (currently only Footlocker)

## How to Use

These scripts should be running continuously for the monitor to work.
As such you will need to host it on a server.
Personally, I use AWS, but nevertheless, there are tonnes out there. 

Each monitor has an associated ```.env``` file. 
This is where you put your webhook URL.
There are also options to change the bot username, avatar and colour.

The Shopify monitors have specific requirements, please refer to the associated ```README.md``` file.


### Proxy Support

Currently, we have proxy support for:
- Supreme

You can enable this by setting the proxy flag:
```
python Supreme/SupremeMonitor.py --proxy <proxy>:<port>
OR WITH CREDENTIALS
python Supreme/SupremeMonitor.py --proxy <proxy_username>:<proxy_password>@<proxy_domain>:<port>
```

## Issues

If you come across any issues, please feel free to reach out.
The monitors will automatically produce a log file - This contains logs of the monitor in action with no personal data being stored.
Please send this log file to me as well as a description of the issues for me to fix.


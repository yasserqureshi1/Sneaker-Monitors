# Sneaker Monitors
*A collection of web monitors that notify of restocks or updates on sneaker related sites through Discord Webhook*

<a href="https://www.buymeacoffee.com/yasserqureshi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

To be notified of changes, please **star** or **watch** this repository.
This will also increase the awareness of the project for others to use or add to. 

I have recently created a Discord server where you can learn to use, get notified of updates and ask questions on the monitors on this repo.
You can join [here](https://discord.gg/jjbtWcBczb) 

## About the Project
This project is aimed to provide different monitors to various sites to the sneaker community for free. 
The monitors currently notify if a restock or update occurs via Discord Webhook.
Today, competition to purchase sneakers is getting increasingly difficult with resellers using paid automated tools to give them a massive advantage over everyone else.
As such, I have and will continue to develop monitors that will help those members to finally get the sneakers they want.

The monitors are developed in a user friendly way for those members that may lack coding experience.
The installation instructions can be found [here](#installation). 

This project is continually expanding, and I would greatly appreciate any contributions. 
When contributing please fork the project and open a Pull Request.
If you'd like a feature to be added, you can either open an issue [here](https://github.com/yasserqureshi1/Sneaker-Monitors/issues/new)
or get in contact with me [here](#contact)

A list of the current sites can be found [here](#monitors) along with the current status.

*Below is a screenshot of the SNKRS monitor in action...*

<p align="center">
  <img width="300" src="https://github.com/yasserqureshi1/Sneaker-Monitors/blob/master/static/SNKRS_example.png?raw=true">
</p>

## Contents
* [About the Project](#about-the-project)
* [Monitors](#monitors)
* [Installation](#installation)
* [Set Up](#set-up)
* [Issues](#issues)
* [To Do](#to-do)
* [License](#license)
* [Contact](#contact)

## Monitors 

Currently the sites that have monitors are:
- All Shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS (Supports 42 countries - see the associated README file)
- Footsites (Footlocker UK, US, CA and AU)
- Ssense
- Zalando (UK)
- Off-Spring (UK)
- Solebox

Below is a table outlining the status on each monitor:

Monitor | Status
--------|--------
Solebox | ![solebox](https://img.shields.io/badge/Solebox-good-brightgreen)
Footlocker | ![footlocker](https://img.shields.io/badge/Footlocker-good-brightgreen)
OffSpring | ![offspring](https://img.shields.io/badge/OffSpring-good-brightgreen)
Ssense | ![ssense](https://img.shields.io/badge/Ssense-good-brightgreen)
Zalando | ![zalando](https://img.shields.io/badge/Zalando-good-brightgreen)
SNKRS | ![snkrs](https://img.shields.io/badge/SNKRS-good-brightgreen)
Shopify | ![shopify](https://img.shields.io/badge/Shopify-issues-red)
Supreme | ![supreme](https://img.shields.io/badge/Supreme-good-brightgreen)

## Installation
To install the modules, use the command in terminal (Mac or Linux) or command prompt (Windows):
```
pip install -r requirements.txt
```

This will install the following dependencies that are needed for the monitors:
```
requests
urllib3
logging
python-dotenv
bs4
```

## Set Up

Ensure you have Python as well as all the dependencies installed.
If you don't have Python, you can download it at this [link](https://www.python.org/downloads/).
To install the dependencies, see [#Installation](#installation) for details.

To start, download the Python file and the ```.env``` file associated with it.
Ensure that both the Python file and ```.env``` file are in the same directory at all times.
You will only need to interact with the ```.env``` file.

In the ```.env``` file, set the ```WEBHOOK``` variable to your Discord webhook URL and your proxy in the ```PROXY``` variable.
Other details can also be edited such as the bot username, avatar and colour.
Below is an example of what the webhook URL should look like:
```
WEBHOOK = "https://discord.com/api/webhooks/..."
```

Some monitors have proxy support. You can enable this by setting the proxy in the ```.env file```.
Below are two different structures:
1. ```PROXY = "<proxy>:<port>"```
2. ```PROXY = "<proxy_username>:<proxy_password>@<proxy_domain>:<port>"```

Other monitors may have other details in their ```.env``` files.
Please refer to that specific README.md file for details on setting up.

These scripts should be running continuously for the monitor to work.
As such you will need to host it on a server.
To set one up yourself, a good article that explains all the hosting methods can be found [here](https://www.writebots.com/discord-bot-hosting/).

I will shortly be releasing a paid (but competitively priced) set of hosted monitors.
This would require only you sending me your webhook url and I will ensure that the monitoring service runs smoothly.
If you are interested in this scheme, let me know [here](#contact) and I can contact you once it is ready.

## Issues

If you find an issue, please open an issue [here](https://github.com/yasserqureshi1/Sneaker-Monitors/issues/new). 
I will respond fairly quickly and try to come up with solution.
I may ask you to provide the log file that is produced by the monitor.
It contains no personal data but may help me diagnose where the issue arises.

## To Do
 - [ ] Create price reduction monitors
 - [ ] Add other requested site (Off-White, Footpatrol, JD, BSTN, Size?, SNS, Naked, Net-a-porter, Footdistrict, oneblockdown, noirfonce and Sivasdescalzo)
 - [ ] Increase number of countries catered for

## License

Distributed under the MIT License. See ```LICENSE``` for more information.

## Contact

For help join my Discord server [here](https://discord.gg/jjbtWcBczb) and post a question in the #questions channel


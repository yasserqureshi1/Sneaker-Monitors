# Sneaker Monitors
*A collection of web monitors that notify of restocks or updates on sneaker related sites through Discord Webhook*

<a href="https://www.buymeacoffee.com/yasserqureshi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## About the Project
This project is aimed to provide different monitors to various sites to the sneaker community for free. 
The monitors currently notify if a restock or update occurs via Discord Webhook.
Today, competition to purchase sneakers is getting increasingly difficult with resellers using paid automated tools to give them a massive advantage over everyone else.
As such, I have and will continue to develop monitors that will help those members to finally get the sneakers they want.

The monitors are developed in a user friendly way for those members that may lack coding experience.
The installation instructions can be found [here](#installation). 

This project is continually expanding, and I would greatly appreciate any contributions. 
When contributing please fork the project and open a Pull Request.

A list of the current sites can be found [here](#monitors)

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
- All shopify sites (e.g. Palace Skateboards, Hanon Shop, OVO, shopnicekicks.com, BDGA Store, Noir Fonce, Travis Scott, etc.)
- Supreme
- Nike SNKRS (Supports 42 countries - see the associated README file)
- Footsites (currently only Footlocker US and UK)
- Ssense
- Zalando (UK)
- Off-Spring (UK)
- Solebox

## Installation
To install the modules, use the command:
```
pip install -r requirements.txt
```

The dependencies that will be installed are:
```
requests
urllib3
logging
python-dotenv
bs4
```

## Set Up

Ensure you have Python as well as all the dependencies installed. See [#Installation](#installation) for details.

To start, download the Python file and the ```.env``` file associated with it.
You will only be interacting with the ```.env``` file.

In the ```.env``` file, set the ```WEBHOOK``` variable to your Discord webhook URL and your proxy in the ```PROXY``` variable.
Other details can also be edited such as the bot username, avatar and colour.
Below is an example of what the webhook URL should look like:
```
WEBHOOK = "https://discord.com/api/webhooks/..."
```

Some monitors have proxy support. You can enable this by setting the proxy in the ```.env file```.
Below is the structure:
```
<proxy>:<port>
OR WITH CREDENTIALS
<proxy_username>:<proxy_password>@<proxy_domain>:<port>
```

These scripts should be running continuously for the monitor to work.
As such you will need to host it on a server.
Personally, I use AWS, but nevertheless, there are tonnes out there. 

Note that the Shopify monitors have specific requirements and you should refer to the specific README file.


## Issues

If you find an issue, please open an issue [here](https://github.com/yasserqureshi1/Sneaker-Monitors/issues/new). 
I will respond fairly quickly and try to come up with solution.
I may ask you to provide the log file that is produced by the monitor.
It contains no personal data but may help me diagnose where the issue arises.

If you are struggling to set up the monitor you can reach out to me via Discord [here](#contact)

## To Do
 - [ ] More items to monitor with SNKRS (currently monitors the 50 recent posts)
 - [ ] Tidy Shopify monitor
 - [ ] Support for Footlocker in CA, AU and US
 - [ ] Add more Footsites (Eastbay, Champsports, Footaction)
 - [ ] Add Demandware sites (Adidas and YeezySupply)
 - [ ] Create price reduction monitors
 - [ ] Add other requested site (Off-White, Footpatrol, JD, BSTN, Size?, SNS, Naked, Net-a-porter, Footdistrict, oneblockdown, noirfonce and Sivasdescalzo)
 - [ ] Increase number of countries catered for


## License

Distributed under the MIT License. See ```LICENSE``` for more information.

## Contact

For help contact me via Discord at @TheBrownPanther2#3801

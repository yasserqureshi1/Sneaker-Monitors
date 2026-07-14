# Sneaker Monitors

*A collection of free web monitors that alert you to restocks and releases on popular sneaker sites — straight to your Discord.*

<p align="center">
  <a href="https://discord.gg/b6zyJyCQUu"><img src="https://img.shields.io/badge/Discord-Join%20the%20community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Join the Discord"></a>
</p>

## About

Hyped sneakers sell out in seconds. Resellers get there first with expensive bots, while everyone else is left refreshing a page and hoping to get lucky.

**Sneaker Monitors levels the playing field.** Each monitor keeps a constant eye on a store and — the moment something drops or restocks — fires an alert straight to your Discord, with the product name, price, image, available sizes and a direct link. You hear about it the instant it happens, completely free.

Point it at your favourite stores, add the keywords you care about, and let it run. Got a question or a site you'd like added? [Come say hi in the Discord](https://discord.gg/b6zyJyCQUu).

<p align="center">
  <img width="300" src="https://github.com/yasserqureshi1/Sneaker-Monitors/blob/master/static/SNKRS_example.png?raw=true">
  <br><em>A live alert from the SNKRS monitor</em>
</p>

## Monitors

Each monitor lives in its own folder under `monitors/`.

| Monitor | What it tracks | Status |
|---|---|---|
| **Shopify** | Any Shopify store (Palace, Hanon, OVO, shopnicekicks, etc.) | ✅ Working |
| **Supreme** | supreme.com — restocks and weekly drops | ✅ Working |
| **SNKRS** | Nike SNKRS launches, 42 countries ([details](monitors/snkrs/README.md)) | ✅ Working |
| **Nike** | Nike new arrivals | ✅ Working |
| **Off-Spring** | Off-Spring (UK) | ✅ Working |
| **Snipes** | Snipes | ✅ Working |
| **Zalando** | Zalando (UK) trainers | ✅ Working |
| **Ssense** | Ssense men's shoes | ✅ Working |
| **Sivasdescalzo** | Sivasdescalzo footwear | ✅ Working |
| **Footlocker** | Footsites (UK / US / AU) | ❌ Not working — blocked by the site's anti-bot protection |

## Setup

You'll need [Python 3](https://www.python.org/downloads/) installed. ([Video walkthrough](https://youtu.be/wlhAtpUxLF4))

**1. Get the code** — clone it (or download the ZIP from the green `Code` button):
```
git clone https://github.com/yasserqureshi1/Sneaker-Monitors.git
cd Sneaker-Monitors
```

**2. Install the dependencies:**
```
pip install -r requirements.txt
```

**3. Configure it** — open the `config.py` file inside the monitor's folder (e.g. `monitors/shopify/config.py`) and add your Discord webhook URL. You can also set keywords, delay and other options there.
> To create a webhook in Discord: **Server Settings → Integrations → Webhooks → New Webhook → Copy Webhook URL**.

**4. Run it** — from inside that monitor's folder:
```
cd monitors/shopify
python monitor.py
```

The monitor keeps checking for as long as it's running. Leave the terminal open, or host it on a server to run 24/7 ([server tutorial](https://youtu.be/nmUSSlt4JKk)). It's best to test on your own computer first.

## License

Distributed under the GNU General Public License v3.0. See `LICENSE` for details. Selling this code without consent is strictly prohibited; any shared or updated copy of this repo must remain freely available.

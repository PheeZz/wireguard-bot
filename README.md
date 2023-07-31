<h1 align="center">PheeZz's Wireguard Bot</h1>
<p align="center">
<img src = "https://github.com/PheeZz/wireguard-bot/blob/master/image/logo_wide.png?raw=true" width = 50%>
</p>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)</br>
[![!Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![!Debian](https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white)](https://www.debian.org/)
[![!Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![!PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![!Wireguard](https://img.shields.io/badge/Wireguard-88171A?style=for-the-badge&logo=wireguard&logoColor=white)](https://www.wireguard.com/)
[![!AdGuard](https://img.shields.io/badge/AdGuard-00A6D6?style=for-the-badge&logo=adguard&logoColor=white)](https://adguard.com/)
[![!Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
## Contents tree:

1. [Description](#description)
2. [Stack](#stack)
3. [Before you start...](#before-you-start)
4. [Setup guide](#setup)

## Description

This bot is designed to manage Wireguard VPN server. It can automatically connect and disconnect users, generate QR codes for mobile clients, and also can be used as a payment system for VPN services.

## Stack

Core: python 3.10, aiogram 2.x<br/>
Database: postgresql<br/>

## Before you start... (if don't want to use semi-automatic installation script)

1. You need to manually install Wireguard on your server. You can find installation guide [here](https://www.wireguard.com/install/).
2. You need to configure Wireguard server. You can find configuration guide [here (RUS)](https://t.me/t0digital/32).
3. You need to create a bot using [BotFather](https://t.me/BotFather).
4. You need to install [PostgreSQL](https://www.postgresql.org/download/).
5. You need to have poetry installed on your system. You can find installation guide [here](https://python-poetry.org/docs/#installation).

## Setup

1. You can use semi-automatic installation script or manual installation guide. If you want to use script, just run it and follow the instructions. If you want to install bot manually, follow the instructions below.
   ### Semi-automatic installation script
   ```bash
   wget https://raw.githubusercontent.com/PheeZz/wireguard-bot/master/SemiAutoInstall.sh && chmod +x SemiAutoInstall.sh && ./SemiAutoInstall.sh
   ```
### Manual installation guide
2. #### Clone this repo and go to project folder<br/>

   ```bash
   git clone https://github.com/PheeZz/wireguard-bot.git && cd wireguard-bot
   ```

3. #### Create your virtualenv inside project dir<br/>

   ```bash
   poetry shell
   ```

4. #### Download required libs<br/>

   ```bash
   poetry install
   ```

5. #### Create your database<br/>

   ```bash
   sudo -u postgres psql
   ```

   ```sql
   CREATE DATABASE <database_name>;
   CREATE USER <user_name> WITH PASSWORD '<password>';
   GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <user_name>;
   GRANT ALL ON ALL TABLES IN SCHEMA "public" TO <user_name>;
   \q
   ```

6. #### Create .env file in data folder and fill it with your data. You can use following example as a template or use .env.sample file (it's the same)<br/>

   ```bash
   cp data/.env.sample data/.env
   nano data/.env
   ```

   #### .env file example

   ```ini
   #telegram bot token
   WG_BOT_TOKEN = <str>
   #ip of your wireguard server
   WG_SERVER_IP = <str>
   #port of your wireguard server
   WG_SERVER_PORT = '51830'
   #server's public key
   WG_SERVER_PUBLIC_KEY = <str>
   #server's preshared key
   WG_SERVER_PRESHARED_KEY= <str>
   #path to wireguard config file, default /etc/wireguard/wg0.conf
   WG_CFG_PATH = '/etc/wireguard/wg0.conf'
   #token for telegram invoice payments, if you don't use payments, just leave it empty (NOW IT'S NOT WORKING)
   PAYMENTS_TOKEN = <str>
   #your telegram id, you can get it from @userinfobot or @myidbot or @RawDataBot
   ADMINS_IDS = <str>
   #your bank card number, if you will use payments with "handmade" method
   PAYMENT_CARD = <str>
   #any text you want to show in the start of every peer config file (for example in case MYVPN_pheezz_PC.conf - "MYVPN" is prefix)
   CONFIGS_PREFIX = <str>
   #how much subscription costs in rubles
   BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES = <int>

   #name of your database
   DATABASE = <str>
   #database user
   DB_USER = <str>
   #database user's password
   DB_USER_PASSWORD = <str>
   #database host, default localhost
   DB_HOST = 'localhost'
   #database port, default 5432
   DB_PORT = '5432'
   ```

7. #### Configure your database tables<br/>
   Move create script from database/create.py to project root folder and run it

   ```bash
   mv database/create.py . && python3.10 create.py
   ```

   Now you can delete create.py file</br>

   ```bash
   rm create.py
   ```
8. #### Install AdGuard Home</br>
   Firtly make installation script executable</br>

   ```bash
   chmod +x AdGuardInstall.sh
   ```

   Then run it</br>

   ```bash
   ./AdGuardInstall.sh
   ```
9.  #### Configure AddGuard Home</br>
   Open AddGuard Home web interface on url ```<your_server_ip>:3000```</br>
   Do the initial setup, it's very simple, just follow the instructions and create admin account</br>
   Go to Settings -> Filters -> DNS blocklists and add some blocklists (I recommend to use add all available blocklists EXCEPT `No Google` list)</br>

10. #### Create .service file for your bot</br>

   Path: `/etc/systemd/system/wireguard-bot.service` </br>
   Code: (if you using python 3.10)</br>

   ```ini
    [Unit]
    Description='Service for wireguard bot'
    After=network.target

    [Service]
    Type=idle
    Restart=on-failure
    User=root
    ExecStart=/bin/bash -c 'cd ~/wireguard-bot/ && $(poetry env info --path)/bin/python3.10 app.py'

    [Install]
    WantedBy=multi-user.target
   ```
11. Enable service and start it</br>

   ```bash
   systemctl enable wireguard-bot.service
   systemctl start wireguard-bot.service
   ```

12. Finally, you can use your bot and enjoy it ❤️

## Extra

### Admin commands (available in chat with bot)

1. `/give <user_id> <days>` - give user access to VPN for \<days> days.<br/>
   Also you can use this command with \<@username> instead of \<user_id>.<br/>
   If you want to disable user's access, just use `/give <user_id> -9999` or any negative number that will be higher than user's access expiration date.<br/>
   <b>WARNING:</b> disconnecting user will not remove his access from database, so you can give him access again later.<br/>
   Example: `/give 123456789 30` - give user with id 123456789 access to VPN for 30 days.
2. `/stats` - show stats about users and their access expiration dates.<br/>
   Aviable options: `/stats active` - show active users.<br/>
   `/stats inactive` - show inactive users.<br/>
   `/stats` without options will show all users.<br/>
   `/wgrestart` - restart wireguard service



## Support

You can support me by give star to this repo or.. Donation..<br/>


<a href = "https://www.donationalerts.com/r/pheezz"><img src = "https://upload.wikimedia.org/wikipedia/ru/thumb/a/ad/DA_Logo_Color.svg/640px-DA_Logo_Color.svg.png" width = 20%></a>

#### ETH - 0x56936AE100f52F99E87767773Ccb2615f1E06ae4<br/>
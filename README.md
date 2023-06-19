<h1 align="center">PheeZz's Wireguard Bot</h1>
<p align="center">
<img src = "https://github.com/PheeZz/wireguard-bot/blob/master/image/logo_wide.png?raw=true" width = 50%>
</p>

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
QR code generator: qrencode<br/>

## Before you start...

1. You need to manually install Wireguard on your server. You can find installation guide [here](https://www.wireguard.com/install/).
2. You need to configure Wireguard server. You can find configuration guide [here (RUS)](https://t.me/t0digital/32).
3. You need to create a bot using [BotFather](https://t.me/BotFather).
4. You need to install [PostgreSQL](https://www.postgresql.org/download/).
5. You need to configure <b>AT LEAST ONE PEER</b> in your Wireguard config file.

## Setup

1. Clone this repo and go to project folder<br/>

   ```bash
   git clone https://github.com/PheeZz/wireguard-bot.git && cd wireguard-bot
   ```

2. Setup your virtualenv<br/>

   ```bash
   python3.10 -m venv .venv
   ```

3. Next step activate it<br/>

- On linux systems:<br/>

  ```bash
  source .venv/bin/activate
  ```

- On Windows:<br/>
  ```cmd
  .venv\Scripts\activate
  ```

3. Download required libs<br/>

   ```bash
   pip install -r requirements.txt
   ```

4. Create your database<br/>

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

5. Create .env file in data folder and fill it with your data. You can use following example as a template.<br/>

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
   #port of your wireguard server, default 51820
   WG_SERVER_PORT = '51820'
   #server's public key
   WG_SERVER_PUBLIC_KEY = <str>
   #server's preshared key
   WG_SERVER_PRESHARED_KEY= <str>
   #path to wireguard config file, default /etc/wireguard/wg0.conf
   WG_CFG_PATH = '/etc/wireguard/wg0.conf'
   #token for telegram invoice payments, if you don't use payments, just leave it empty
   PAYMENTS_TOKEN = <str>
   #your telegram id, you can get it from @userinfobot or @myidbot or @RawDataBot
   ADMINS_IDS = <str>
   #your bank card number, if you will use payments with "handmade" method
   PAYMENT_CARD = <str>

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

6. Configure your database tables<br/>
   Move create script from database/create.py to project root folder and run it

   ```bash
   mv database/create.py . && python3.10 create.py
   ```

   Now you can delete create.py file</br>

   ```bash
   rm create.py
   ```

7. Install <b>qrencode</b> package for generating QR code for mobile configs

   ```bash
   sudo apt install qrencode
   ```

8. Create .service file for your bot</br>
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
    ExecStart=/bin/bash -c 'cd ~/wireguard-bot/ && source .venv/bin/activate && python3.10 app.py'

    [Install]
    WantedBy=multi-user.target
   ```

9. Enable service and start it</br>

   ```bash
   systemctl enable wireguard-bot.service
   systemctl start wireguard-bot.service
   ```

10. Finally, you can use your bot and enjoy it ❤️

## Extra

### Admin commands (aviable in chat with bot)

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

### You can use pip-review for updating your libs

```bash
pip-review --local --auto
```

## TODO
1. Migrate from pip to poetry.
2. Refactor code in utils/Watchdog.py
3. Simplify installation.
4. Maybe add docker-file. 

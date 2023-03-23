# Setup

> Note: if you know how to setup venv go to step 4

1. Setup your virtualenv<br/>
   `python -m venv .venv`

2. Next step activate it<br/>

- On linux systems:<br/>
  `source .venv/bin/activate`

- On Windows:<br/>
  `.venv\Scripts\activate`

3. Download required libs<br/>
   `pip install -r requirements.txt`

4. Create .env file in `data\.env` with BOT_TOKEN

5. Launch bot in `app.py` file

6. Sample .service file

   Path: `/etc/systemd/system/wireguard-bot.service` </br>
   Code: (if you using python 3.10)</br>

   ```
    [Unit]
    Description='Service for my new bot'
    After=network.target

    [Service]
    Type=idle
    Restart=on-failure
    User=root
    ExecStart=/bin/bash -c 'cd ~/wireguard-bot/ && source .venv/bin/activate && python3.10 app.py'

    [Install]
    WantedBy=multi-user.target
   ```

7. Enable service and start it</br>
   ```
   systemctl enable wireguard-bot.service
   systemctl start wireguard-bot.service
   ```

8. Install qrencode package for generating QR code for mobile configs
   ```
   sudo apt install qrencode
   ```
## Extra

`pip-review --local --auto` - update all libs

### data/.env sample

```
WG_BOT_TOKEN = <str>
WG_SERVER_IP = <str>
WG_SERVER_PORT = <str>
WG_SERVER_PUBLIC_KEY = <str>
WG_SERVER_PRESHARED_KEY= <str>
WG_CFG_PATH = <str>
PAYMENTS_TOKEN = <str>
ADMINS_IDS = <list>
PAYMENT_CARD = <str>

DATABASE = <str>
DB_USER = <str>
DB_USER_PASSWORD = <str>
DB_HOST = <str>
DB_PORT = <str>

```

## As database used `Postgres`

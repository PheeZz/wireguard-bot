#answer user for bot token
echo "Enter bot token:"
read bot_token

#answer user for payment card
echo "Enter payment card number:"
read payment_card

#answer user for admins ids
echo "Enter admins ids (separated by comma):"
read admins_ids

sudo apt update && sudo apt upgrade -y
sudo apt install -y git
git clone https://github.com/PheeZz/wireguard-bot.git

#install zsh, curl
sudo apt install -y zsh curl

#install python3.10
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3.10-venv python3.10-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

#install tmux, mosh, wireguard, and postgres
sudo apt install -y tmux mosh wireguard postgresql postgresql-contrib
sudo systemctl start postgresql.service

#create wg keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey | tee /etc/wireguard/publickey
wg genpsk | tee /etc/wireguard/presharedkey
sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 600 /etc/wireguard/presharedkey
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf


# Determine the correct network interface
if ip link show eth0 &> /dev/null; then
    interface=eth0
elif ip link show ens3 &> /dev/null; then
    interface=ens3
else
    echo "Error: could not determine network interface" >&2
    exit 1
fi

# Create WireGuard configuration file
sudo cat << EOF > /etc/wireguard/wg0.conf
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $interface -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $interface -j MASQUERADE


EOF

# Restart WireGuard service
systemctl restart wg-quick@wg0.service

# Install AdGuard Home and configure it to use WireGuard as upstream DNS server
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
cd /opt/AdGuardHome/
sudo ./AdGuardHome -s install
sudo ./AdGuardHome -s start
sudo ./AdGuardHome -s status
sudo ./AdGuardHome -s stop
sudo mkdir -p /etc/systemd/resolved.conf.d
sudo echo << EOF >> /etc/systemd/resolved.conf.d/adguardhome.conf
[Resolve]
DNS=127.0.0.1
DNSStubListener=no
EOF
sudo mv /etc/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl daemon-reload
sudo systemctl reload-or-restart systemd-resolved
sudo systemctl restart systemd-resolved
sudo ./AdGuardHome -s start

#configure postgres
sudo -u postgres psql -c "CREATE DATABASE wireguardbot;"
#create user
sudo -u postgres psql -c "CREATE USER wireguard_manager_user WITH PASSWORD 'bestpassword123';"
#grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wireguardbot TO wireguard_manager_user;"
#grant privileges to wireguard_manager_user on shema public
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO wireguard_manager_user;"

#get server external ip
server_ip=$(curl -s https://api.ipify.org)
#get server public and preshared keys
server_public_key=$(cat /etc/wireguard/publickey)
server_preshared_key=$(cat /etc/wireguard/presharedkey)

cd
cd wireguard-bot
#write .env file
cat << EOF >> data/.env
WG_BOT_TOKEN = $bot_token
WG_SERVER_IP = $server_ip
WG_SERVER_PORT = '51820'
WG_SERVER_PUBLIC_KEY = $server_public_key
WG_SERVER_PRESHARED_KEY= $server_preshared_key
WG_CFG_PATH = '/etc/wireguard/wg0.conf'
PAYMENTS_TOKEN = 'PAYMENTS_TOKEN_HERE'
ADMINS_IDS = $admins_ids
PAYMENT_CARD = $payment_card
CONFIGS_PREFIX = 'WG_VPN_BOT_BY_PHEEZZ'
BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES = 100

DATABASE = 'wireguardbot'
DB_USER = 'wireguard_manager_user'
DB_USER_PASSWORD = 'bestpassword123'
DB_HOST = 'localhost'
DB_PORT = '5432'

EOF

#install poetry and install dependencies
sudo python3.10 -m pip install poetry
poetry install

#try to run create.py if it fails, then give db user superuser privileges
mv database/create.py . && python3.10 create.py
rm create.py
python3.10 create.py || sudo -u postgres psql -c "ALTER USER wireguard_manager_user WITH SUPERUSER;"
python3.10 create.py

#create .service file
sudo cat << EOF >> /etc/systemd/system/wireguard-bot.service
[Unit]
Description=WireGuard VPN Bot
After=network.target

[Service]
Type=simple
User=root
ExecStart=/bin/bash -c 'cd ~/wireguard-bot/ && $(poetry env info --path)/bin/python3.10 app.py'

[Install]
WantedBy=multi-user.target
EOF

#enable and start wireguard-bot.service
systemctl daemon-reload
systemctl enable wireguard-bot.service
systemctl start wireguard-bot.service

#show message about configuring AdGuard Home
for i in {1..5}; do echo "HEY USER, configure ADGUARD HOME at url http://$server_ip:3000"; done
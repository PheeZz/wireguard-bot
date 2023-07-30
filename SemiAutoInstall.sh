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

#install zsh, oh-my-zsh, and some plugins
sudo apt install -y zsh curl
sudo chsh -s $(which zsh) $(whoami)
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
sudo apt install -y fonts-powerline
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
echo "plugins=(git zsh-syntax-highlighting\nzsh-autosuggestions\ngit\nfancy-ctrl-z\ncolored-man-pages\nsudo\ntmux\nzsh-autosuggestions\nzsh-syntax-highlighting)" >> ~/.zshrc
#this is my favorite theme, but you can change it to whatever you want
echo "ZSH_THEME=\"xiong-chiamiov\"" >> ~/.zshrc

#install python3.10
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3.10-venv python3.10-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

#install tmux, mosh, wireguard, and postgres
sudo apt install -y tmux mosh wireguard postgresql postgresql-contrib
sudo systemctl start postgresql.service

#create wg keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey | tee /etc/wireguard/publickey
wg genpsk | tee /etc/wireguard/presharedkey
chmod 600 /etc/wireguard/privatekey
chmod 600 /etc/wireguard/presharedkey
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf


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
cat << EOF > /etc/wireguard/wg0.conf
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
echo << EOF >> /etc/systemd/resolved.conf.d/adguardhome.conf
[Resolve]
DNS=127.0.0.1
DNSStubListener=no
EOF
sudo mv /etc/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl daemon-reload
sudo systemctl restart systemd-resolved.service
sudo ./AdGuardHome -s start

#configure postgres
sudo -u postgres psql -c "CREATE DATABASE wireguardbot;"
#create user
sudo -u postgres psql -c "CREATE USER wireguard-manager WITH PASSWORD 'bestpassword123';"
#grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wireguardbot TO wireguard-manager;"
#grant privileges to wireguard-manager on shema public
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO wireguard-manager;"

#get server external ip
server_ip=$(curl -s https://api.ipify.org)
#get server public and preshared keys
server_public_key=$(cat /etc/wireguard/publickey)
server_preshared_key=$(cat /etc/wireguard/presharedkey)

cd wireguard-bot
#write .env file
echo << EOF >> data/.env
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
DB_USER = 'wireguard-manager'
DB_USER_PASSWORD = 'bestpassword123'
DB_HOST = 'localhost'
DB_PORT = '5432'
EOF

#install poetry and install dependencies
sudo python3.10 -m pip install poetry
cd wireguard-bot
poetry shell | head -n 1 | cut -d ' ' -f 5 > venv_path.txt
poetry install

#try to run create.py if it fails, then give db user superuser privileges
mv database/create.py . && python3.10 create.py
rm create.py
python3.10 create.py || sudo -u postgres psql -c "ALTER USER wireguard-manager WITH SUPERUSER;"
python3.10 create.py

#create .service file
echo << EOF >> /etc/systemd/system/wireguard-bot.service
[Unit]
Description=WireGuard VPN Bot
After=network.target

[Service]
Type=simple
User=root
ExecStart=/bin/bash -c 'cd /~/wireguard-bot && $(cat venv_path.txt)/bin/python3.10 main.py'

[Install]
WantedBy=multi-user.target
EOF

#enable and start wireguard-bot.service
systemctl daemon-reload
systemctl enable wireguard-bot.service
systemctl start wireguard-bot.service

#show message about configuring AdGuard Home
for i in {1..5}; do echo "HEY USER, configure ADGUARD HOME at url http://$server_ip:3000"; done
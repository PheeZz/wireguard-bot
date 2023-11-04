#color codes for terminal
Red=$'\e[1;31m'
Green=$'\e[1;32m'
Blue=$'\e[1;34m'
Defaul_color=$'\e[0m'
Orange=$'\e[1;33m'
White=$'\e[1;37m'

# disable firewall
sudo ufw disable

sudo apt install -y curl iptables
#clear screen after install curl
clear

#get server external ip
server_ip=$(curl -s https://ifconfig.me)

if [ -z "$server_ip" ]
then
      echo "$Red Can't get server external ip" | sed 's/\$//g'
      echo "$Red Check your internet connection" | sed 's/\$//g'
      echo "$Red Fail on command: curl -s https://ifconfig.me" | sed 's/\$//g'
      exit 1
fi

echo $Blue | sed 's/\$//g'
echo "This script will install WireGuard VPN Bot on your server"
echo "It will install and configure:"
echo $Orange | sed 's/\$//g'
echo "- WireGuard VPN"
echo "- AdGuard Home"
echo "- PostgreSQL"
echo "- Python 3.10"
echo "- Poetry"
echo "- Telegram Bot"
echo $Red | sed 's/\$//g'
echo "............................................................"
echo "...................made by PheeZz..........................."
echo "............................................................"

echo $White | sed 's/\$//g'

echo "Now need to input some data for bot configuration"
echo "You can change it later in ~/wireguard-bot/data/.env file"
echo ""

#ask for bot token
echo "Enter bot token:"
echo "You can get it from $Blue @BotFather"
read bot_token

#ask user for payment card
echo "$White" | sed 's/\$//g'
echo "Enter payment card number:"
echo "Just press ENTER for use default card [$Blue 4242424242424242 $White]" | sed 's/\$//g'
read payment_card
if [ -z "$payment_card" ]
then
      payment_card="4242424242424242"
fi

#ask user for admins ids
echo ""
echo "Enter admins ids (separated by comma):"
echo "Just press ENTER for use default ids [$Blue 123456789, $White]" | sed 's/\$//g'
echo "You can get your id by sending /id command to @userinfobot"
read admins_ids
if [ -z "$admins_ids" ]
then
      admins_ids="123456789,"
fi

#ask user for Database name
echo ""
echo "Enter Database name:"
echo "Just press ENTER for use default name [$Blue wireguardbot $White]" | sed 's/\$//g'
read database_name
if [ -z "$database_name" ]
then
      database_name="wireguardbot"
fi

#ask user for Database user
echo ""
echo "Enter Database user:"
echo "Just press ENTER for use default user [$Blue wireguard_manager_user $White]" | sed 's/\$//g'
read database_user
if [ -z "$database_user" ]
then
      database_user="wireguard_manager_user"
fi

echo ""
echo "Enter Database user password:"
echo "Just press ENTER for use default password [$Blue bestpassword123 $White]" | sed 's/\$//g'
read database_passwd
if [ -z "$database_passwd" ]
then
      database_passwd="bestpassword123"
fi

echo ""
echo "Enter config name prefix:"
echo "Just press ENTER for use default prefix [$Blue WG_VPN_BOT_BY_PHEEZZ $White]" | sed 's/\$//g'
read config_prefix

if [ -z "$config_prefix" ]
then
      config_prefix="WG_VPN_BOT_BY_PHEEZZ"
fi

echo ""
echo "Enter base subscription monthly price in rubles:"
echo "Just press ENTER for use default price [$Blue 100 $White]" | sed 's/\$//g'
read base_subscription_monthly_price_rubles

if [ -z "$base_subscription_monthly_price_rubles" ]
then
      base_subscription_monthly_price_rubles="100"
fi

echo ""
echo "Do u want to use domain name instead of ip? [$Blue enter domain name$White or press ENTER to skip ]" | sed 's/\$//g'
read domain_name

#if domain name not empty then switch variable server ip with it
if [ -n "$domain_name" ]
then
      server_ip=$domain_name
fi

echo ""
echo "Do you want to install AdGuard Home? [ y / $Blue [n] $White]" | sed 's/\$//g'
read install_adguard_home

if [ "$install_adguard_home" = "y" ]
then
      install_adguard_home="true"
else
      install_adguard_home="false"
fi

#if install_adguard_home is false ask for peer dns server
if [ "$install_adguard_home" = "false" ]
then
      echo ""
      echo "Enter peer dns server(-s):"
      echo "Just press ENTER for use default dns server [$Blue 1.1.1.1, 8.8.8.8 $White]" | sed 's/\$//g'

      read peer_dns
      #if peer dns is empty then set default dns server
      if [ -z "$peer_dns" ]
        then
            peer_dns="1.1.1.1, 8.8.8.8"
      fi
else
      #if install_adguard_home is true then set peer dns to "10.0.0.1"
      peer_dns="10.0.0.1"

fi
echo "$White peer dns: $Blue $peer_dns" | sed 's/\$//g'
sleep 5

sudo apt update && sudo apt upgrade -y
sudo apt install -y git bat
git clone https://github.com/PheeZz/wireguard-bot.git

#install zsh, curl
sudo apt install -y curl

#install python3.10
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3.10-venv python3.10-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

#install tmux, mosh, wireguard, and postgres
sudo apt install -y tmux mosh wireguard postgresql postgresql-contrib
sudo systemctl start postgresql.service

#create wg keys
sudo wg genkey | sudo tee /etc/wireguard/privatekey | sudo wg pubkey | sudo tee /etc/wireguard/publickey
sudo wg genpsk | sudo tee /etc/wireguard/presharedkey
sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 600 /etc/wireguard/presharedkey


# Determine the correct network interface
if ip link show eth0 &> /dev/null; then
    interface=eth0
elif ip link show ens3 &> /dev/null; then
    interface=ens3
elif ip link show enp0s5 &> /dev/null; then
    interface=enp0s5
else
    echo "Error: could not determine network interface" >&2
    exit 1
fi

# Create WireGuard configuration file
sudo cat << EOF > /etc/wireguard/wg0.conf
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.1/24
ListenPort = 51830
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $interface -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $interface -j MASQUERADE


EOF

# Enable IP forwarding
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sudo sysctl -p 

#enable and start wiregiard service
sudo systemctl enable wg-quick@wg0.service
sudo systemctl start wg-quick@wg0.service

#configure postgres
su - postgres -c "psql -c \"CREATE DATABASE $database_name;\""
#create user
su - postgres -c "psql -c \"CREATE USER $database_user WITH PASSWORD '$database_passwd';\""
#grant privileges
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $database_name TO $database_user;\""
#grant privileges to wireguard_manager_user on shema public
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO $database_user;\""

#get server public and preshared keys
server_public_key=$(sudo cat /etc/wireguard/publickey)
server_preshared_key=$(sudo cat /etc/wireguard/presharedkey)

#configure .env file
cd ~/wireguard-bot
#write .env file
cat << EOF >> data/.env
WG_BOT_TOKEN = $bot_token
WG_SERVER_IP = $server_ip
WG_SERVER_PORT = '51830'
WG_SERVER_PUBLIC_KEY = $server_public_key
WG_SERVER_PRESHARED_KEY= $server_preshared_key
WG_CFG_PATH = '/etc/wireguard/wg0.conf'
ADMINS_IDS = $admins_ids
PAYMENT_CARD = $payment_card
CONFIGS_PREFIX = $config_prefix
BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES = $base_subscription_monthly_price_rubles
PEER_DNS = '$peer_dns'


DATABASE = $database_name
DB_USER = $database_user
DB_USER_PASSWORD = $database_passwd
DB_HOST = 'localhost'
DB_PORT = '5432'

EOF

#install poetry and install dependencies
sudo pip3.10 install poetry
#install dependencies
poetry install

#try to run create.py if it fails, then give db user superuser privileges
mv database/create.py .
$(poetry env info --path)/bin/python3.10 create.py || sudo -u postgres psql -c "ALTER USER $database_user WITH SUPERUSER;" && $(poetry env info --path)/bin/python3.10 create.py
rm create.py

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


if [ "$install_adguard_home" = "true" ]
then
    # Install AdGuard Home and configure it to use WireGuard as upstream DNS server
    curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
    cd /opt/AdGuardHome/
    sudo ./AdGuardHome -s install
    sudo ./AdGuardHome -s start
    sudo ./AdGuardHome -s status
    sudo ./AdGuardHome -s stop
    sudo mkdir -p /etc/systemd/resolved.conf.d
    sudo cat << EOF >> /etc/systemd/resolved.conf.d/adguardhome.conf
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
    #show message about configuring AdGuard Home
    for i in {1..5}; do echo "$Blue HEY USER, configure $Green ADGUARD HOME at url $Red http://$server_ip:3000" | sed 's/\$//g'; done
    #show message about get torrrents blocklist
    for i in {1..2}; do echo "$Orange TORRENTS BLOCKLIST at url $Red https://raw.githubusercontent.com/DNCD/block-bittorrent-domains/main/trackers" | sed 's/\$//g'; done

fi

echo "$Green Installation completed successfully" | sed 's/\$//g'
echo "$Defaul_color" | sed 's/\$//g'

echo "$Blue Your .env file located at $Orange ~/wireguard-bot/data/.env" | sed 's/\$//g'
echo "$Blue Do u want to watch it? [ y / $Blue [n] $White]" | sed 's/\$//g'
read watch_env_file

if [ "$watch_env_file" = "y" ]
then
    batcat ~/wireguard-bot/data/.env
fi

echo "$Defaul_color" | sed 's/\$//g'

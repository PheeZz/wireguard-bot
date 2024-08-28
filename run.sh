#!/bin/bash
if [ -f /etc/wireguard/privatekey ] && [ -f /etc/wireguard/publickey ] && [ -f /etc/wireguard/presharedkey ]; then
    echo "Keys already exist"
else
    echo "Keys do not exist, creating new keys"
    wg genkey | tee /etc/wireguard/privatekey | wg pubkey | tee /etc/wireguard/publickey
    wg genpsk | tee /etc/wireguard/presharedkey
    chmod 600 /etc/wireguard/privatekey
    chmod 600 /etc/wireguard/presharedkey
fi

#configure wireguard if it is not already configured
if [ -f /etc/wireguard/wg0.conf ]; then
    echo "Wireguard already configured"
else
    echo "Configuring Wireguard"
    cat << EOF > /etc/wireguard/wg0.conf
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.1/24
ListenPort = $(echo $WG_SERVER_PORT)
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE


EOF
fi

wg-quick up wg0 --config /etc/wireguard/wg0.conf &
alembic upgrade head
python app.py
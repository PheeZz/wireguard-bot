#/bin/bash
wg genkey | tee /etc/wireguard/privatekey | wg pubkey | tee /etc/wireguard/publickey
wg genpsk | tee /etc/wireguard/presharedkey
chmod 600 /etc/wireguard/privatekey
chmod 600 /etc/wireguard/presharedkey
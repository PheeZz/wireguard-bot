#/bin/bash
sudo wg genkey | sudo tee /etc/wireguard/privatekey | sudo wg pubkey | sudo tee /etc/wireguard/publickey
sudo wg genpsk | sudo tee /etc/wireguard/presharedkey
sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 600 /etc/wireguard/presharedkey
# Configure system to use AdGuardHome as DNS server
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

sudo apt install -y curl
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
cd /opt/AdGuardHome/
sudo ./AdGuardHome -s install
sudo ./AdGuardHome -s start
sudo ./AdGuardHome -s status
sudo mkdir -p /etc/systemd/resolved.conf.d
echo "[Resolve]\nDNS=127.0.0.1\nDNSStubListener=no\n" >> /etc/systemd/resolved.conf.d/adguardhome.conf
sudo mv /etc/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl reload-or-restart systemd-resolved
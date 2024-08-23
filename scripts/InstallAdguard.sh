#/bin/bash
curl -sSL https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
cd /opt/AdGuardHome/
./AdGuardHome -s install
./AdGuardHome -s start
./AdGuardHome -s status
./AdGuardHome -s stop
mkdir -p /etc/systemd/resolved.conf.d
cat << EOF >> /etc/systemd/resolved.conf.d/adguardhome.conf
[Resolve]
DNS=127.0.0.1
DNSStubListener=no
EOF
mv /etc/resolv.conf /etc/resolv.conf.backup
ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
systemctl daemon-reload
systemctl reload-or-restart systemd-resolved
systemctl restart systemd-resolved
./AdGuardHome -s start
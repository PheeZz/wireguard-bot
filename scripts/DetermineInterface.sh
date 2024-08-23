#/bin/bash
if ip link show eth0 &> /dev/null; then
    echo "eth0"
elif ip link show ens3 &> /dev/null; then
    echo "ens3"
elif ip link show enp0s5 &> /dev/null; then
    echo "enp0s5"
else
    echo "Error: could not determine network interface" >&2
    exit 1
fi
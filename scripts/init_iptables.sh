#!/bin/sh


#Launching a reboot in 3 minutes in case the scripts crashes and SSH isn't allowed
#shutdown -r -h 3 --> /!\ Doesn't work on the server. Only shuts down :(


#emptying the tables
iptables -t filter -F
iptables -t nat    -F
iptables -t mangle -F
iptables -t raw    -F
iptables -t filter -X VPN_FW
#Dropping common attack patterns : null packets, syn-flood and recon
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP

#allowing answers to outgoing connections
iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

#allowing SSH
iptables -t filter -A INPUT -p tcp --dport 22 -j ACCEPT

#allowing VPN
iptables -t filter -A INPUT -p udp --dport 1194 -j ACCEPT

#Allowing HTTP
iptables -t filter -A INPUT -p tcp --dport 80 -j ACCEPT

#Allowing HTTPS
iptables -t filter -A INPUT -p tcp --dport 443 -j ACCEPT

#allowing all localhost traffic
iptables -t filter -A INPUT -i lo -j ACCEPT

#Creating a chain for VPN traffic and dropping everything by default
iptables -t filter -N VPN_FW
iptables -t filter -A VPN_FW -j DROP

#redirecting everything from the VPN to the new chain
iptables -t filter -I FORWARD -i tun0 -j VPN_FW

#setting the policies
iptables -t filter -P INPUT DROP
iptables -t filter -P FORWARD DROP
iptables -t filter -P OUTPUT ACCEPT



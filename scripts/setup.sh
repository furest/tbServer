#!/bin/bash

if [ "$EUID" -ne 0 ] ; then
	echo "Le script doit être exécuté en tant que root!"
	exit
fi

echo "Les commandes suivantes vont être exécutées"
echo "apt-get update"
echo "apt-get install openvpn python3 python3-pip uml-utilities"
echo "pip3 install pyroute2"
read -p "Etes-vous d'accord? [N]" choix
choix=${choix:-N}

if [ "${choix,,}" != "y" ] ; then
	exit
fi
echo "Installation..."

apt-get update -y
apt-get install -y openvpn python3 python3-pip uml-utilities
pip3 install pyroute2
echo ""
echo ""
echo ""
echo ""
echo "La connexion au serveur peut être établie en lancant le script suivant: "
echo "   sudo python3 init.py"
echo ""
echo "Pour fermer la connexion vers le serveur :"
echo "   sudo sh flush.sh"
echo ""
echo ""



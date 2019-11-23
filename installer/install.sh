install_dir="/etc/tbServer"

# Outputs an Install log line
function install_log() {
    echo -e "\033[1;32mTwinbridge Server Install: $*\033[m"
}

# Outputs an Install Error log line and exits with status code 1
function install_error() {
    echo -e "\033[1;37;41mTwinbridge Server Install Error: $*\033[m"
    exit 1
}

# Outputs a Warning line
function install_warning() {
    echo -e "\033[1;33mWarning: $*\033[m"
}

# Outputs a welcome message
function display_welcome() {
    green='\033[0;32m'
    cyan='\033[1;36m'
    #Font is "Colossal" on http://patorjk.com/software/taag/#p=display&h=0&v=1&f=Colossal&t=Twinbridge
    echo -e "${green}\n"
    echo -e "88888888888               d8b          888              d8b      888                           "
    echo -e "    888                   Y8P          888              Y8P      888                           "
    echo -e "    888                                888                       888                           "
    echo -e "    888     888  888  888 888 88888b.  88888b.  888d888 888  .d88888  .d88b.   .d88b.          "
    echo -e "    888     888  888  888 888 888 \"88b 888 \"88b 888P\"   888 d88\" 888 d88P\"88b d8P  Y8b    "
    echo -e "    888     888  888  888 888 888  888 888  888 888     888 888  888 888  888 88888888         "
    echo -e "    888     Y88b 888 d88P 888 888  888 888 d88P 888     888 Y88b 888 Y88b 888 Y8b.             "
    echo -e "    888      \"Y8888888P\"  888 888  888 88888P\"  888     888  \"Y88888  \"Y88888  \"Y8888    "
    echo -e "                                                                          888                     "
    echo -e "                                                                     Y8b d88P                    "
    echo -e "                                                                      \"Y88P\"                    "
    echo -e "${cyan}"
    echo -e "The Installer will guide you through a few easy steps\n\n"
}

function config_installation() {
    install_log "Configure installation"
    echo "Install directory: ${install_dir}"
    echo -n "Complete installation with these values? [y/N]: "
    read answer
    if [[ $answer != "y" ]]; then
        echo "Installation aborted."
        exit 0
    fi
}

function install_apt_packages() {
    sudo apt-get update
    sudo apt-get install openvpn mariadb-server python3 python3-pip git tcpdump golang libpcap-dev iptables-persistent netfilter-persistent
    mkdir ~/go
    echo "GOPATH=~/go" >> ~/.bashrc
    source ~/.bashrc    
}

function install_pip_packages() {
    sudo pip3 install passlib python-iptables scapy mysql-connector netaddr
}

function create_services() {
    sudo groupadd twinbridge
    sudo cp ${install_dir}/installer/etc/systemd/system/*.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable twinbridge
    sudo systemctl enable twinbridge-labManager
    sudo systemctl enable twinbridge-labCleaner
    sudo systemctl enable twinbridge-labAnalyzer
    sudo systemctl enable twinbridge-listenUDP
}

function configure_openvpn(){
    sudo cp -r ${install_dir}/installer/etc/openvpn/* /etc/openvpn
    cd
    wget https://github.com/OpenVPN/easy-rsa/releases/download/v3.0.6/EasyRSA-unix-v3.0.6.tgz -O EasyRSA.tgz
    tar -xvf EasyRSA.tgz
    rm EasyRSA.tgz
    cd EasyRSA-v3.0.6
    ./easyrsa init-pki
    echo "ca_crt" | ./easyrsa build-ca nopass
    echo "srv_crt" | ./easyrsa build-server-full srv_crt nopass
    ./easyrsa gen-dh
    sudo cp pki/ca.crt /etc/openvpn/
    sudo cp pki/private/srv_crt.key /etc/openvpn/server.key
    sudo cp pki/issued/srv_crt.crt /etc/openvpn/server.crt
    sudo cp pki/dh.pem /etc/openvpn/dh.pem
    sudo openvpn --genkey --secret /etc/openvpn/ta.key
    ip_addr=`ip route show default | sed 's/.*src\s\([0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\).*/\1/g'`
    sudo sed -i -e "s/\(.*\){ip_addr}\(.*\)/\1$ip_addr\2/" /etc/openvpn/*.conf
    sudo systemctl enable openvpn-server@TCPServer
    sudo systemctl enable openvpn-server@UDPServer
}

function download_tbserver() {
    git clone --depth 1 https://github.com/furest/tbServer $install_dir
}

function configure_mysql() {
    sudo mysql < $install_dir/installer/twinbridge.sql
    tb_password=`< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-10};echo;`
    sudo mysql --database twinbridge --execute="CREATE USER 'twinbridge'@'localhost' IDENTIFIED BY '${tb_password}'; GRANT ALL ON twinbridge.* to 'twinbridge'@'localhost'; FLUSH PRIVILEGES;"
}

function compile_analyze() {
	cd ${install_dir}/bin
	sudo go get
	sudo go build "${install_dir}/bin/analyze.go"
	cd -
}

function erase_installfiles() {
    sudo rm -r "${install_dir}/installer"
}

function configure_iptables() {
    sudo bash $install_dir/scripts/init_iptables.sh
    sudo netfilter-persistent save
    sudo netfilter-persistent start
}

function configure_ssh() {
    sudo sed -i "/^#Port 22/c\Port 222" /etc/ssh/sshd_config
    sudo systemctl restart sshd
}

function install_complete() {
    install_log "Installation completed!"
    install_warning "mariadb username is 'twinbridge' and password is '${tb_password}'"
    echo ""
    install_warning "Iptables rules will now be applied. If you are connected using SSH you will be disconnected."
    echo -n "The system needs to be rebooted as a final step. Reboot now? [y/N]: "
    read answer
    configure_iptables
    configure_ssh
    if [[ $answer != "y" ]]; then
        echo "Installation reboot aborted."
        exit 0
    fi
    sudo shutdown -r now || install_error "Unable to execute shutdown"
}
function install() {
    display_welcome
    config_installation
    install_apt_packages
    install_pip_packages
    download_tbserver
    configure_openvpn
    configure_mysql
    compile_analyze
    create_services
    erase_installfiles
    install_complete
}

install



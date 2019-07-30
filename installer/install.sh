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


function install_complete() {
    install_log "Installation completed!"
    install_warning "Please create your own PKI for OpenVPN"
    install_warning "The following files must be created:"
    install_warning "- ca.crt       The CA certificate"
    install_warning "- dh.pem       A diffie-hellman key"
    install_warning "- ta.key       An openvpn static key"
    install_warning "- server.crt   The server certificate"
    install_warning "- server.key   The server public key"
    install_warning "Please check steps 1 to 3 at https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-18-04"
    install_warning ""
    install_warning "mariadb username is 'twinbridge' and password is '${tb_password}'"

    echo -n "The system needs to be rebooted as a final step. Reboot now? [y/N]: "
    read answer
    if [[ $answer != "y" ]]; then
        echo "Installation reboot aborted."
        exit 0
    fi
    sudo shutdown -r now || install_error "Unable to execute shutdown"
}

function install_apt_packages() {
    sudo apt-get update
    sudo apt-get install openvpn mariadb-server python3 python3-pip git tcpdump golang libpcap-dev
    mkdir ~/go
    echo "GOPATH=~/go" >> ~/.bashrc
    source ~/.bashrc
    
}

function install_pip_packages() {
    sudo pip3 install passlib python-iptables scapy
}

function create_services() {
    sudo cp "${install_dir}/installer/etc/systemd/system/*.service" "/etc/systemd/system/" 
    sudo systemctl daemon-reload
    sudo systemctl enable twinbridge
    sudo systemctl enable twinbridge-labManager
    sudo systemctl enable twinbridge-labCleaner
    sudo systemctl enable twinbridge-labAnalyzer
    sudo systemctl enable twinbridge-listenUDP
}

function configure_openvpn(){
    sudo cp -r "${install_dir}/installer/etc/openvpn" "/etc/openvpn"
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



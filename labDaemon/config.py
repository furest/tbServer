config = dict()

config['SRV_IP'] = "172.16.100.1"
config['SRV_PORT'] = 1500
config['PIPE'] = "/tbpipe"
config['PIN_LENGTH'] = 6
config['SMTP_SRV'] = "smtp.gmail.com"
config['SMTP_PORT'] = 587
config['SMTP_USER'] = "team.twinbridge@gmail.com"
config['SMTP_PASS'] = "Km17sAH2ZQg1"
config['SMTP_FROM'] = "team.twinbridge@gmail.com"
config['DB_WP_HOST'] = "localhost"
config['DB_WP_USER'] = "vpn"
config['DB_WP_PASS'] = "vpnpassword"
config['DB_WP_NAME'] = "wordpress"
config['DB_TB_HOST'] = "localhost"
config['DB_TB_USER'] = "vpn"
config['DB_TB_PASS'] = "vpnpassword"
config['DB_TB_NAME'] = "twinbridge"

wpParams = {
        "host": config['DB_WP_HOST'],
        "user":config['DB_WP_USER'],
        "passwd":config['DB_WP_PASS'],
        "database":config['DB_WP_NAME']
    }
tbParams = {
        "host": config['DB_TB_HOST'],
        "user":config['DB_TB_USER'],
        "passwd":config['DB_TB_PASS'],
        "database":config['DB_TB_NAME']
}


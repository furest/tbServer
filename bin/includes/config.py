import json
import os
config =dict()

mod_path = os.path.realpath(__file__)
mod_dir = os.path.dirname(mod_path)

with open(mod_dir + "/config.json") as configfile:
    config = json.load(configfile)
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


import mysql.connector
from config import *
def listTwinings(client_id):
    db = mysql.connector.connect(**wpParams)
    c = db.cursor(dictionary=True)
    client = (client_id, client_id)
    c.execute("SELECT a1.user_login AS login,\
                    a1.user_email AS email,\
                    a1.id AS academy_id,\
                    wp_twinings.id AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.id = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.id = wp_twinings.academy_2\
            WHERE a2.user_email =  %s\
            UNION ALL\
            SELECT a2.user_login AS login,\
                    a2.user_email AS email,\
                    a2.id AS academy_id,\
                    wp_twinings.id AS twining_id\
            FROM wp_twinings\
            INNER JOIN wp_users a1 ON a1.id = wp_twinings.academy_1\
            INNER JOIN wp_users a2 ON a2.id = wp_twinings.academy_2\
            WHERE a1.user_email =  %s", client)
    twlist = c.fetchall()
    return twlist 

from ratelimit import limits,sleep_and_retry
import requests
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
USER = os.getenv("USER")

mydb = mysql.connector.connect(
    host=os.getenv("host"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    database=os.getenv("database")
)

@sleep_and_retry
@limits(calls=45, period=30)
def api_call(url):
    headers = {"User-Agent": USER}
    r = requests.get(url, headers=headers, allow_redirects=True)

    if r.status_code != 200:
        raise Exception(f'API Response: {r.status_code}')
    return r

def updated():
    r = open("update.txt", "r")
    num = r.read()
    r.close()
    return "<t:{}:R>".format(num)

def get_prefix(bot, msg):
    if msg.guild is None:
        return '!'
    else:
        mycursor = mydb.cursor()
        print(msg.guild.id)
        mycursor.execute(f'SELECT prefix FROM guild WHERE serverid = "{msg.guild.id}" LIMIT 1')
        data = mycursor.fetchone()
        print(data)
        return str(data[0])
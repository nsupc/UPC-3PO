from ratelimit import limits,sleep_and_retry
import requests
import os
from dotenv import load_dotenv
import mysql.connector
import time

load_dotenv()
USER = os.getenv("AGENT")

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
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'SELECT prefix FROM guild WHERE serverid = "{msg.guild.id}" LIMIT 1')
        data = mycursor.fetchone()
        return str(data[0])

def get_log(id):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT logchannel FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = mycursor.fetchone()
    return int(data[0])

def get_cogs(id):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT cogs FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = mycursor.fetchone()
    return data[0]
    
def connector():
    mydb = mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )
    return mydb

def logerror(ctx, error):
    f = open("error.txt", "a")
    f.write(f"{int(time.time())}: {type(error)} occured from command invocation {ctx.message.content}\n")
    f.close()
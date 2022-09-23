import os
import mysql.connector
import requests
import time

from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry


@sleep_and_retry
@limits(calls=45, period=30)
def api_call(url: str, mode: int, data: dict = None, pin: str = None):
    '''For requests to the NationStates API. Mode 1: Public requests, Mode 2: Private requests'''

    headers = {
        "User-Agent": os.getenv("USER_AGENT")
    }

    # Mode 1 is for public requests
    if(mode==1):
        r = requests.get(url, headers=headers)
    # Mode 2 is for private requests
    elif(mode==2):
        headers["X-Password"] = os.getenv("NATION_AUTH")

        r = requests.get(url, headers=headers)

    if r.status_code == 404:
        return None
    elif r.status_code != 200:
        print(r)
        print(r.headers)
        raise Exception(f'API Response: {r.status_code}')
    else:
        return r


def connector():
    mydb = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE")
    )
    return mydb


def format_names(name: str, mode: int):
    '''Convert strings to lower or title case. Mode 1: Lower, Mode 2: Title'''
    
    if mode == 1:
        name = name.lower().replace(" ", "_")
    elif mode == 2:
        name = name.replace("_", " ").title()

    return name


def get_cogs(id):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT cogs FROM guild WHERE serverid = "{id}" LIMIT 1')
    data = mycursor.fetchone()
    return data[0]

    
def get_prefix(bot, msg) -> str:
    if msg.guild is None:
        return '!'
    else:
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'SELECT prefix FROM guild WHERE serverid = "{msg.guild.id}" LIMIT 1')
        data = mycursor.fetchone()
        return str(data[0])


def get_roles(serverid: int):
    '''Creates a dictionary containing the region and verification roles for a particular server'''
    mydb = connector()
    mycursor = mydb.cursor()

    items = ["region", "verified", "waresident", "resident", "visitor"]
    roles = {}

    for item in items:
        mycursor.execute(f"SELECT {item} FROM guild WHERE serverid = '{serverid}'")
        returned = mycursor.fetchone()[0]

        roles[item] = returned

    return roles


async def log(bot, id: int, action: str):
    '''Logs admin actions performed by the bot if the server has a designated log channel'''
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f'SELECT logchannel FROM guild WHERE serverid = "{id}" LIMIT 1')
    channel_id = mycursor.fetchone()[0]

    if not channel_id:
        return

    log_channel = bot.get_channel(int(channel_id))

    await log_channel.send(f"<t:{int(time.time())}:f>: {action}")


async def welcome(bot, member):
    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT welcomechannel FROM guild WHERE serverid = '{member.guild.id}'")
    returned = mycursor.fetchone()
    if returned == None:
        return
    else: 
        welcome = bot.get_channel(int(returned[0]))

    mycursor.execute(f"SELECT welcome FROM guild WHERE serverid = '{member.guild.id}'")
    returned = mycursor.fetchone()
    if returned == None:
        return
    else: 
        text = returned[0].replace('<user>', member.mention)

    await welcome.send(text)
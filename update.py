from unicodedata import name
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
import os
import requests
import gzip
from datetime import datetime as dt
import time

from functions import api_call

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database")
)

mycursor = mydb.cursor()

headers = {"User-Agent": "The United Peoples of Centrism"}
r = api_call("https://www.nationstates.net/pages/nations.xml.gz")
open('nations.xml.gz', "wb").write(r.content)

op = open("nations.xml", "w", encoding="utf-8")
with gzip.open("nations.xml.gz","rb") as ip_byte:
    op.write(ip_byte.read().decode("utf-8"))
ip_byte.close()

mycursor.execute("DELETE FROM nations")

tree = ET.parse("nations.xml")
root = tree.getroot()

for child in root:
    if child[6].text is None:
        endos = 0
    else:
        endos = len(child[6].text.split(","))
    sql = "INSERT INTO nations (name, type, motto, category, unstatus, numendos, issues, region, population, founded, lastlogin, influence, dbid, endorsements) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (child[0].text, child[1].text, child[3].text, child[4].text, child[5].text, endos, child[7].text, child[9].text, child[10].text, child[22].text, child[23].text, child[25].text, child[34].text, ",{},".format(child[6].text))
    mycursor.execute(sql, val)

mydb.commit()

mycursor.execute("SELECT COUNT(NAME) FROM nations")
count = mycursor.fetchone()[0]
print(count, "record(s) inserted.")

w = open("update.txt", "w")
w.write(str(int(time.time())))
w.close()

#os.remove("nations.xml")
os.remove("nations.xml.gz")


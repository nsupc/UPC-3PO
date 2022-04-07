from unicodedata import name
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv("host"),
  user=os.getenv("user"),
  password=os.getenv("password"),
  database=os.getenv("database")
)
mycursor = mydb.cursor()

def sqlnat():
    mycursor.execute("DROP TABLE nations")

    mycursor.execute("CREATE TABLE nations (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), type VARCHAR(255), motto VARCHAR(255), category VARCHAR(255), unstatus VARCHAR(255), numendos SMALLINT(10), issues SMALLINT(10), region VARCHAR(255), population INT(10), founded INT(25), lastlogin INT(25), influence VARCHAR(255), dbid INT(25), endorsements LONGTEXT)")

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

    print(mycursor.rowcount, "record(s) inserted.")

def sqlreg():
    mycursor.execute("DROP TABLE reg")
    
    mycursor.execute("CREATE TABLE reg (id INT AUTO_INCREMENT PRIMARY KEY, userid VARCHAR(30), serverid VARCHAR(30), nation VARCHAR(40), timestamp INT(25), verified BOOL)")

    mydb.commit()

def sqlguild():
    mycursor.execute("DROP TABLE guild")
    
    mycursor.execute("CREATE TABLE guild (id INT AUTO_INCREMENT PRIMARY KEY, serverid VARCHAR(30), prefix VARCHAR(10), logchannel VARCHAR(30), welcome VARCHAR(500))")

    #sql = ("INSERT INTO guild (serverid, prefix) VALUES (%s, %s)")
    #val = ("", "!")
    #mycursor.execute(sql, val)

    mydb.commit()

#sqlnat()
#sqlreg()
#sqlguild()
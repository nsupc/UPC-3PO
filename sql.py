import xml.etree.ElementTree as ET
import gzip
from bs4 import BeautifulSoup as bs

from functions import connector

def sqlnat():
    mydb = connector()
    mycursor = mydb.cursor()

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
    mydb = connector()
    mycursor = mydb.cursor()

    mycursor.execute("DROP TABLE reg")
    
    mycursor.execute("CREATE TABLE reg (id INT AUTO_INCREMENT PRIMARY KEY, userid VARCHAR(30), serverid VARCHAR(30), nation VARCHAR(40), timestamp INT(25), verified BOOL)")

    mydb.commit()

def sqlguild():
    mydb = connector()
    mycursor = mydb.cursor()
    
    #mycursor.execute("DROP TABLE guild")
    
    #mycursor.execute("CREATE TABLE guild (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(40), serverid VARCHAR(30), prefix VARCHAR(10), logchannel VARCHAR(30), welcomechannel VARCHAR(30), welcome VARCHAR(500), cogs VARCHAR(30))")

    sql = ("INSERT INTO guild (name, serverid, prefix, cogs) VALUES (%s, %s, %s, %s)")
    val = ("VERY REAL REGION", "949358173444243546", "!", "nva")
    mycursor.execute(sql, val)

    mydb.commit()

def sqls2():
    mydb = connector()
    mycursor = mydb.cursor()

    op = open("cardlist_S2.xml", "w", encoding="utf-8")
    with gzip.open("cardlist_S2.xml.gz","rb") as ip_byte:
        op.write(ip_byte.read().decode("latin-1"))
    ip_byte.close()

    mycursor.execute("DROP TABLE s2")

    mycursor.execute("CREATE TABLE s2 (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(30), dbid INT(25))")

    with open("cardlist_S2.xml", encoding="utf-8") as fp:
        soup = bs(fp, 'xml')
        r = soup.find_all("CARD")

    for x in r:
        sql = ("INSERT INTO s2 (name, dbid) VALUES (%s, %s)")
        val = (x.NAME.text, x.ID.text)
        mycursor.execute(sql, val)
        print(x.NAME.text)

    mydb.commit()

    print(mycursor.rowcount, "record(s) inserted.")

#sqlnat()
#sqlreg()
sqlguild()
#sqls2()
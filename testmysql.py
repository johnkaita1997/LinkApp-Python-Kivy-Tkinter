import mysql.connector
from datetime import datetime


db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "root",
    database = "CocabPos"
)

mycursor = db.cursor(buffered=True)
seccursor = db.cursor(buffered=True)
#Create the database

#mycursor.execute("CREATE TABLE products(buyingprice VARCHAR(50),  category VARCHAR(50), code VARCHAR(50),  name VARCHAR(50), sellingprice VARCHAR (50), id int PRIMARY KEY AUTO_INCREMENT)")
#mycursor.execute("INSERT INTO Braches(name) VALUES ('Kisumu')")
#mycursor.execute('SELECT id, name FROM  Braches WHERE gender = 'M', ORDER BY id DESC)
#db.commit()
#mycursor.execute("ALTER TABLE Braches ADD COLUMN Food VARCHAR(50) NOT NULL")

# mycursor.execute("SELECT * FROM Braches")
#
# for x in mycursor:
#     print(x)

#mycursor.execute("DESCRIBE Braches")
#print(mycursor.fetchall())
import mysql.connector

import pwd

cnx = mysql.connector.connect(user='root', password="stonks", host='34.68.197.158', database='insight_database')

cursor = cnx.cursor()

query = "Select * from User;"

cursor.execute(query)

for (col1) in cursor:
    print(col1)

cursor.close()
cnx.close()
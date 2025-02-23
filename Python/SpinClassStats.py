import pyodbc
from time import sleep

# Connect to database and open SQL cursor
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Get total number of classes downloaded
cursor.execute("""SELECT COUNT(*) FROM [SpinClass].[dbo].[SpinClassCounts]""")
number_of_classes = cursor.fetchone()[0]
print("Number of FFC classes downloaded: " + str(number_of_classes))
print('')

# Get total number of rides taken
cursor.execute("""SELECT SUM([Count]) FROM [SpinClass].[dbo].[SpinClassCounts]""")
number_of_rides = cursor.fetchone()[0]
print("Total number of rides: " + str(number_of_rides))
print('')

# Get total number of riders
cursor.execute("""SELECT COUNT(*) FROM [SpinClass].[dbo].Riders""")
number_of_riders = cursor.fetchone()[0]
print("Total unique riders: " + str(number_of_riders))
print('')

cursor.close()
conn.close()

sleep(10)

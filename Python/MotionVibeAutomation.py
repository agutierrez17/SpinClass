from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidArgumentException, ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

import os
import logging
import pyodbc
from datetime import date, datetime, time
from dateutil import relativedelta
import sys
import glob
import pandas as pd
import xlrd
import shutil
from xls2xlsx import XLS2XLSX
import win32com.client as win32

# Get today's date
today = date.today() #  # date(2023,10,23)
print()
print("Today is " + str(today))
print()

# Connect to database and open SQL cursor
print('Connecting to Spin Class database...')
print('')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Get most recent date for downloaded data
cursor.execute("""SELECT CONVERT(DATE,MAX([DateFormatted])) FROM DBO.Riders_Rides""")
most_recent_class = cursor.fetchone()[0] #date(2024,7,29)#  # 
print("The most recent class taught is " + str(most_recent_class))
print('')

diff = relativedelta.relativedelta(most_recent_class, today)
years = abs(diff.years)
months = abs(diff.months)
days = abs(diff.days)
delta = today - most_recent_class

print('Difference in time: {} months, {} days'.format(months, days))
print('Difference in number of days: ' + str(delta.days))
print('')

# Kill any currently-running chrome driver instances and browser windows
print('Quitting any Chromedriver instances, Chrome windows, and Excel files that are already running...')
print('')
os.system("taskkill /f /im chromedriver.exe")
os.system("taskkill /f /im chrome.exe")
os.system("taskkill /f /im excel.exe")

# Delete previous files in Downloads
print('Clearing out old files from the Downloads folder...')
print('')
filelist = [f for f in os.listdir(downloads) if f.startswith("Grid_") and f.endswith(".xls")]
for f in filelist:
    os.remove(os.path.join(downloads,f))
try:
except:
    pass

# Set options and preferences
print('Setting Chrome options and prefences...')
print('')
chromeoptions = webdriver.ChromeOptions()
service = Service(executable_path="C:\\chromedriver.exe")
driver = webdriver.Chrome(service=service,options=chromeoptions)
driver.maximize_window()
actions = ActionChains(driver)

# Open browser and navigate to MotionVibe URL
print('Opening MotionVibe...')
print('')
url = 'https://motionvibe.com/(S(3dqc2zk4osvv0tlef23chv50))/MyVibe.aspx'
driver.get(url)

sleep(1)

# Enter username and password
print('Logging in...')
print('')
try:
    username = driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[1]/td/input")
    password = driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/input")
    driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[3]/td/span/input").click()
    driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/input").click()
except NoSuchElementException:
    print('Already logged in...')

sleep(1)

# Navigate back to the date of the most recent ride
n = 1
if months > 0 or days > today.day or most_recent_class.day < today.day:
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr/td[3]/div[1]/div/input").click()
    sleep(1)
    
if days > today.day:
    months = months + 1
        
while n <= months:
    sleep(1)
    driver.find_element("xpath","/html/body/div[2]/div/a[1]").click()
    sleep(1)
    print('Going back ' + str(n) + ' months...')
    n = n + 1

sleep(1)

# Pick the correct date on the calendar      
k = 1
l = 1
while k <= 5:
    while l <= 7:
        try:
            if driver.find_element("xpath","/html/body/div[2]/table/tbody/tr["+str(k)+"]/td["+str(l)+"]/a").text == str(most_recent_class.day + 1):
                driver.find_element("xpath","/html/body/div[2]/table/tbody/tr["+str(k)+"]/td["+str(l)+"]/a").click()
                sleep(2)
                break
        except NoSuchElementException:
            pass
        l = l + 1
    
    k = k + 1
    l = 1

# Begin looping through all the days between the most recent ride and today
m = 1
sleep(2)

# Create loop function
def data_scrape(classes, zero):
    
    # Scrape rider names
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a").click()

    # Get top-line ride data
    date = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr/td[2]/span").text
    time = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[1]/td").text
    class_format = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[2]/td/span").text
    location = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[1]/td/table/tbody/tr[1]/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/span").text
    registrants = int(driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td[4]/span").text)
    print(str(date))
    print(str(time))
    print(str(class_format))
    print(str(location))
    print('Number of registrants: ' + str(registrants))
    print('')

    sleep(2)

    # If no riders signed up, move to the next day
    if registrants == 0 and zero == False:
        driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr["+str(classes)+"]/td[4]/input").click()
        return
        sleep(4)
    elif registrants == 0 and zero == True:
        return

    # Print rider names
    print('Riders:')
    for i in range(1,registrants + 1):
        try:
            driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[3]/td/div/table/tbody/tr[3]/td/table/tbody/tr["+str(i)+"]")
        except NoSuchElementException:
            break
        try:
            driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[3]/td/div/table/tbody/tr[3]/td/table/tbody/tr["+str(i)+"]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/span")
            line = 2
        except NoSuchElementException:
            line = 1
        while True:
            try:
                element = driver.find_element("id","ctl00_MainContent_phProDash1_lvGroupFitness_ctrl"+str(classes-1)+"_ctl00_lvClassRoster_ctrl"+str(i-1)+"_btnProfilePreview")
                rider_name = element.text
                print(rider_name)
            except NoSuchElementException:
                driver.execute_script("arguments[0].scrollIntoView(true);", element);
                continue
            break
            
    print('')

    sleep(2)

    print('Downloading rider contact info...')
    print('')

    # Download rider info
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr[3]/td/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[1]/td[2]/a").click()
    sleep(5)
    filepath = max(downloads, key=os.path.getctime)

    # Open with WIN32COM, save as xlsx
    try:
        excel = win32.dynamic.Dispatch('Excel.Application')
    except AttributeError as e:
        print(str(e))
        print("Caught an error with win32com...now deleting gen_py directory...")
        print()
        shutil.rmtree("C:\\Users\\andre\\AppData\\Local\\Temp\\gen_py\\3.11\\00020813-0000-0000-C000-000000000046x0x1x9")
        excel = win32.dynamic.Dispatch('Excel.Application')
    excel.Visible = False
    wb = excel.Workbooks.Open("%s" % (str(filepath)))
    ws = wb.ActiveSheet

    wb.SaveAs("%s" % (str(newfilepath)),FileFormat = 51)
    wb.Close(False)
    wb = None
    excel.Quit()

    print('Downloaded file to: ' + str(newfilepath))
    print('')
    
    # Read file into dataframe
    data = pd.read_excel(r'%s' % (str(newfilepath)),engine='openpyxl')
    df = pd.DataFrame(data, columns=data.columns).fillna(value='')
    #df.replace(pd.NA,'')

    # Insert dataframe values into spin database
    print('Inserting rider data into table...')
    print('')
    for i, row in df.iterrows():
        cursor.execute("""INSERT INTO [dbo].[Riders_Rides] ([Date],[Time],[Class Format],[Location],[FirstName],[LastName],[Email]) VALUES (?,?,?,?,?,?,?)""", (date, time, class_format, location, row['FirstName'], row['LastName'], row['Email']))
        cursor.commit()
        
    print('All rider info inserted...')
    print('')

    cursor.execute("""EXEC [dbo].[Format_Rider_Date];""")
    cursor.commit()

    try:
        os.remove('C:\\Users\\andre\\Documents\\Spinning\\FFCRosterDownload.xlsx')
    except:
        pass
    try:
        driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr["+str(classes)+"]/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[1]/td/div/div/table/tbody/tr[3]/td/div/table/tbody/tr[1]/td[2]/input").click()
    except:
        pass
# End function
    
print('')
print('Starting loop through calendar...')
print('')
while m <= delta.days:
    
    # If no ride, skip to next day
    try:
        if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[3]/td/span").text == 'Nothing on your agenda today':
            driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr/td[4]/input").click()
            m = m + 1
            sleep(4)
            continue
    except:
        sleep(1)

    print('Beginning to scrape rider and class info...')
    print('')

    # Check if there are two classes on the same day
    try:
        two_classes_check = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[1]/a").size
    except NoSuchElementException:
        two_classes_check = 0

    # Run function once or twice depending on the number of classes 
    if two_classes_check != 0:
        data_scrape(1, True)
        sleep(1)
        #driver.execute_script("window.scrollBy(0,500)");
        #leep(2)
        data_scrape(2, False)
    else:
        data_scrape(1, False)

    # Navigate to the next page
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/div/div/table/tbody/tr/td[1]/table/tbody/tr[3]/td/div/table/tbody/tr/td/div/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr/td[4]/input").click()
    m = m + 1
    sleep(4)

driver.quit()

# Run alias procedure
cursor.execute("""EXEC [dbo].[AliasInsert];""")
cursor.commit()
    
cursor.close()
conn.close()

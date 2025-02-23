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

# Get first class date for downloaded data
first_class = date(2023,11,25)
print("The first class taught is " + str(first_class))
print('')

diff = relativedelta.relativedelta(first_class, today)
years = abs(diff.years)
months = abs(diff.months)
days = abs(diff.days)
delta = today - first_class

print('Difference in time: {} years, {} months, {} days'.format(years, months, days))
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
downloads = 'C:\\Users\\andre\\Downloads'
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
url = 'https://motionvibe.com/(S(jikwfmpn1kgdcjqlcmtzyxli))/ManualCounts.aspx'
driver.get(url)

sleep(1)

# Enter username and password
print('Logging in...')
print('')
try:
    username = driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[1]/td/input")
    password = driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/input")
    driver.find_element("xpath","/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[4]/td[2]/input").click()
except NoSuchElementException:
    print('Already logged in...')
    print('')

sleep(1)

######################## CLASS COUNTS #############################

print('Navigate to Class Counts page...')
print('')
if driver.current_url.endswith("MyVibe.aspx"):
    driver.get(driver.current_url.replace("MyVibe","ManualCounts"))
    sleep(1)

# Update report date parameters to all-time
driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/table/tbody/tr[2]/td[1]/table/tbody/tr/td[2]/input").click()
sleep(1)
driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/table/tbody/tr[2]/td[1]/table/tbody/tr/td[3]/input").click()
sleep(1)

# Navigate back to the date of the first ride
n = 1

if days > today.day:
    months = months + 1

if years == 1:
    months = months + 12
        
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
            if driver.find_element("xpath","/html/body/div[2]/table/tbody/tr["+str(k)+"]/td["+str(l)+"]/a").text == str(first_class.day):
                driver.find_element("xpath","/html/body/div[2]/table/tbody/tr["+str(k)+"]/td["+str(l)+"]/a").click()
                sleep(2)
                break
        except NoSuchElementException:
            pass
        l = l + 1
    
    k = k + 1
    l = 1

# Show all classes during timeframe
driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/table/tbody/tr[2]/td[1]/table/tbody/tr/td[6]/input").click()
sleep(5)

# Download list
driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/table/tbody/tr[2]/td[2]/img").click()
sleep(5)

filepath = max(downloads, key=os.path.getctime)

# Open with WIN32COM, save as xlsx
try:
    excel = win32.dynamic.Dispatch('Excel.Application')
except AttributeError as e:
    print(str(e))
    print("Caught an error with win32com...now deleting gen_py directory...")
    print()
    excel = win32.dynamic.Dispatch('Excel.Application')
excel.Visible = False
wb = excel.Workbooks.Open("%s" % (str(filepath)))
wb.Worksheets(1).Name = "Grid"
ws = wb.ActiveSheet

wb.SaveAs("%s" % (str(newfilepath)),FileFormat = 51)
wb.Close(False)
wb = None
excel.Quit()

print('')
print('Downloaded file to: ' + str(newfilepath))
print('')

######################## UPCOMING RIDES #############################

# Navigate to upcoming rides calendar
print('Navigate to upcoming class calendar...')
print('')
driver.get(driver.current_url.replace("ManualCounts","MyVibeSchedule"))
sleep(3)

# Connect to database and open SQL cursor
print('Connecting to Spin Class database...')
print('')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Find the number of weeks in the current month
try:
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[6]")
    r = 6
except:
    r = 5

i = 1

# Loop through all days in the current month until the current date, then increment to the next date
print('Looping through calendar...')
print('')
d = 1
c = 1
while d <= r:
    try:
        if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/a").text == str(today.day):
            # Navigate to next month if today's date is the last day of the current month
            if d == r and c == 7:
                driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[3]/input").click()
                sleep(1)
                i + i + 1
                d = 1
                c = 1
                break

            c = c + 1
            
            if c > 7:
                d = d + 1
                c = 1 
            break
        
        c = c + 1
        
        if c > 7:
            d = d + 1
            c = 1
    except:
        c = c + 1
        continue

# Loop through all subsequent dates and scrape upcoming ride info
print('Scraping upcoming ride data...')
print('')
rowlist = []
while i <= 2:    
    while d <= r:
        try:
            p = 1
            
            # Check for two classes on the same day
            try:
                if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr[2]/td/div/div/div[1]/table/tbody/tr[1]/td[1]/img"):
                    x = 2
                else:
                    x = 1
            except:
                x = 1

            # Loop through all rides on the given day (there may be more than one)
            while p <= x:
                if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr["+str(p)+"]/td/div/div/div[1]/table/tbody/tr[1]/td[1]/img"):
                    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr["+str(p)+"]/td/div/div/div[1]/table/tbody/tr[1]/td[1]/img").click()
                    sleep(3)

                    # Set variables from scraped text
                    class_format = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr["+str(p)+"]/td/div/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td").text
                    time = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr["+str(p)+"]/td/div/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td").text
                    location = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/table/tbody/tr["+str(p)+"]/td/div/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td").text.replace('at ','')
                    datenum = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr["+str(d)+"]/td["+str(c)+"]/a").text
                    day_of_week = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td/table/tbody/tr/td["+str(c)+"]").text
                    
                    # Get current month value
                    m = 1
                    while m <= 12:
                        try:
                            if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[2]/select/option["+str(m)+"]").get_attribute("selected") == 'true':
                                month = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[2]/select/option["+str(m)+"]").get_attribute("value")
                                break
                        except Exception as e:
                            pass
                        m = m + 1

                    # Get current year
                    y = 1
                    while y <= 15:
                        try:
                            if driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[4]/select/option["+str(y)+"]").get_attribute("selected") == 'true':
                                year = driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[2]/td/table/tbody/tr/td[4]/select/option["+str(y)+"]").get_attribute("value")
                                break
                        except Exception as e:
                            pass
                        y = y + 1

                    # Create date field
                    cur_date = datetime(int(year), int(month), int(datenum))

                    # Create and append row
                    row = (cur_date, day_of_week, time, class_format, location)
                    rowlist.append(row)
                    
                    if c > 7:
                        d = d + 1
                        c = 1
                p = p + 1
                
        except Exception as e:
            pass
        
        c = c + 1    
        if c > 7:
            d = d + 1
            c = 1

    i = i + 1

    # Navigate to next month
    driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[3]/input").click()
    sleep(1)
    d = 1
    c = 1

    # Find number of weeks in new month
    try:
        driver.find_element("xpath","/html/body/form/div[3]/table[2]/tbody/tr/td/div/div/div[2]/div/div/div/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[6]")
        r = 6
    except:
        r = 5

# INSERT DATA INTO UPCOMING RIDES TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[UpcomingRides]""")
cursor.commit()

print('Inserting upcoming rides data into database...')
print('')
cursor.executemany("""INSERT INTO [dbo].[UpcomingRides] ([Date],[Day of Week],[Time],[Class Format],[Location]) VALUES (?,?,?,?,?)""",rowlist)
cursor.commit()
sleep(1)

# Run date format procedure
cursor.execute("""EXEC [dbo].[UpcomingRidesDateFormat];""")
cursor.commit()

print('All upcoming rides inserted.')

cursor.close()

driver.quit()

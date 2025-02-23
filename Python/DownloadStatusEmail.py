from datetime import date, datetime
import datetime as d
import smtplib
import ssl
import pyodbc
import email
import email.mime.application
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

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

# Run Query for most recent ride
print("Running query for most recent ride...")
print()
cursor.execute("""
SELECT TOP 1
S.Class,
S.Club,
S.Day,
S.Date,
S.Count
FROM DBO.SpinClassCounts S WITH (NOLOCK)

ORDER BY
[Date] Desc
""")
row = cursor.fetchone()
Class = row[0]
Club = row[1]
Day = row[2]
Date = row[3].strftime("%b %d %Y %H:%M")
Count = int(row[4])
sleep(1)

RiderList = ""

# Run query for riders from most recent ride
print("Running query for riders from most recent ride...")
print('')
cursor.execute("""
SELECT
FirstName,
LastName
FROM DBO.Riders_Rides
WHERE
DateFormatted = (SELECT MAX([Date]) FROM DBO.SpinClassCounts S WITH (NOLOCK))
""")
rows = cursor.fetchall()
for row in rows:
    FirstName = row[0]
    LastName = row[1]
    RiderList = RiderList + '<li class="x_x_ContentPasted0 x_ContentPasted0" style="list-style:disc">' + FirstName + " " + LastName + "<BR>"
RiderList = RiderList + '</li>'
sleep(1)

# Run query for playlist from most recent ride
print("Running query for playlist from most recent ride...")
print("")
cursor.execute("""
SELECT
[Playlist Name]
FROM DBO.Classes_Playlists
WHERE
[Class Date] = (SELECT MAX([Date]) FROM DBO.SpinClassCounts S WITH (NOLOCK))
""")
row = cursor.fetchone()
playlist = row[0]
sleep(1)

ArtistList = ""

# Run query for songs from playlist
print("Running query for songs from playlist...")
print("")
cursor.execute("""
SELECT
[Playlist Order],
T.[Track Name],
(SELECT STUFF((
        SELECT ', ' + A.[Artist Name]
        FROM DBO.Artists A WITH (NOLOCK)
		INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON A.[Artist ID] = TA.[Artist ID]
        WHERE TA.[Track ID] = T.[Track ID]
		ORDER BY A.[Artist Name]
        FOR XML PATH('')), 1, 2, ''))  AS Artists
FROM DBO.PlaylistTracks PT WITH (NOLOCK)
INNER JOIN DBO.Tracks T WITH (NOLOCK) ON PT.[Track ID] = T.[Track ID]
WHERE
PT.[Playlist ID] = (SELECT [Playlist ID] FROM DBO.Classes_Playlists WITH (NOLOCK) WHERE [Class Date] = (SELECT MAX([Date]) FROM DBO.SpinClassCounts S WITH (NOLOCK)))

ORDER BY
[Playlist Order];
""")
rows = cursor.fetchall()
for row in rows:
    TrackNumber = row[0]
    Track = row[1]
    Artists = row[2]
    ArtistList = ArtistList + str(int(TrackNumber)) + ". " + Track + " - " + Artists + "<BR>"
sleep(1)

RidesList = ""

# Run query for upcoming rides
print("Running query for the three next upcoming rides...")
print("")
cursor.execute("""
SELECT TOP 3
ROW_NUMBER() OVER (PARTITION BY '' ORDER BY [Date],[Time]) AS Rw,
[Class Format] + ' - FFC ' + Location AS "Upcoming Ride Location",
[Day of Week] + ', ' + DateFormatted + ' - ' + REPLACE(REPLACE(REPLACE(Time,' AM','am'),' PM','pm'),'-','to') AS "Upcoming Ride Time"
FROM DBO.UpcomingRides
ORDER BY
[DATE], [TIME]
""")
rows = cursor.fetchall()
for row in rows:
    Number = row[0]
    Ride1 = row[1]
    Ride2 = row[2]
    RidesList = RidesList + str(int(Number)) + ". " + Ride1 + " (" + Ride2 + ")<BR>"
sleep(1)

# Run query for total classes taught
print("Running query for total classes taught...")
print("")
cursor.execute("""
SELECT
COUNT(*),
COUNT(*) - SUM(CASE WHEN [DATE] < CONVERT(DATE,GETDATE()) THEN 1 ELSE 0 END)
FROM DBO.SpinClassCounts
""")
row = cursor.fetchone()
no_of_classes = row[0]
no_of_classes_diff = row[1]
sleep(1)

# Run query for total number of rides
print("Running query for total number of rides...")
print("")
cursor.execute("""
SELECT
COUNT(*),
COUNT(*) - SUM(CASE WHEN [DateFormatted] < CONVERT(DATE,GETDATE()) THEN 1 ELSE 0 END)
FROM DBO.Riders_Rides
""")
row = cursor.fetchone()
no_of_rides = row[0]
no_of_rides_diff = row[1]
sleep(1)

# Run query for total number of unique riders
print("Running query for total number of unique riders...")
print("")
cursor.execute("""
SELECT
COUNT(*),
COUNT(*) - SUM(CASE WHEN [First Ride] < CONVERT(DATE,GETDATE()) THEN 1 ELSE 0 END)
FROM DBO.Riders
""")
row = cursor.fetchone()
no_of_riders = row[0]
no_of_riders_diff = row[1]
sleep(1)

# Run query for total number of playlists
print("Running query for total number of playlists...")
print("")
cursor.execute("""
SELECT DISTINCT
COUNT(DISTINCT [Playlist ID]),
SUM(CASE WHEN CP.[Playlist Date] >= CONVERT(DATE,GETDATE()) THEN 1 ELSE 0 END)
FROM DBO.Classes_Playlists CP
WHERE
CP.[Playlist Name] LIKE '%FFC%'
AND
CP.[Playlist Name] LIKE '%[0-9]%%[0-9]%'
""")
row = cursor.fetchone()
no_of_playlists = row[0]
no_of_playlists_diff = row[1]
sleep(3)
##
### Run query for total number of tracks
##print("Running query for total number of tracks...")
##print("")
##cursor.execute("""
##SELECT 
##COUNT(DISTINCT [Track ID]),
##COALESCE((
##SELECT DISTINCT
##COUNT(DISTINCT PT.[Track ID])
##FROM DBO.PlaylistTracks PT WITH (NOLOCK)
##INNER JOIN DBO.Classes_Playlists CP WITH (NOLOCK) ON PT.[Playlist ID] = CP.[Playlist ID]
##
##GROUP BY
##PT.[Track ID]
##HAVING
##MIN(CP.[Class Date]) >= CONVERT(DATE,GETDATE())
##),0)
##FROM DBO.Tracks_Historical WITH (NOLOCK)
##""")
##row = cursor.fetchone()
##no_of_tracks = row[0]
##no_of_tracks_diff = row[1]
##sleep(10)

### Run query for total number of artists
##print("Running query for total number of artists...")
##print("")
##cursor.execute("""
##SELECT
##COUNT(DISTINCT TA.[Artist ID]),
##COALESCE((
##SELECT DISTINCT
##COUNT(DISTINCT TA.[Artist ID])
##FROM DBO.Tracks_Artists TA WITH (NOLOCK)
##INNER JOIN DBO.PlaylistTracks PT WITH (NOLOCK) ON TA.[Track ID] = PT.[Track ID]
##INNER JOIN DBO.Classes_Playlists CP WITH (NOLOCK) ON PT.[Playlist ID] = CP.[Playlist ID]
##
##GROUP BY
##TA.[Artist ID]
##HAVING
##MIN(CP.[Class Date]) >= CONVERT(DATE,GETDATE())
##),0)
##FROM DBO.Tracks_Historical TH WITH (NOLOCK)
##INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON TH.[Track ID] = TA.[Track ID]
##""")
##row = cursor.fetchone()
##no_of_artists = row[0]
##no_of_artists_diff = row[1]
##sleep(10)

# Run query for total Hubspot contacts
print("Running query for total number of Hubspot contacts...")
print("")
cursor.execute("""
SELECT
COUNT(*),
SUM(CASE WHEN [Create Date] AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time' >= CONVERT(DATE,GETDATE()) THEN 1 ELSE 0 END)
FROM DBO.Hubspot_Spin_Contacts
""")
row = cursor.fetchone()
no_of_hubspot_contacts = row[0]
no_of_hubspot_contacts_diff = row[1]
sleep(1)

HubspotList = ""

# Run query for Today's Riders Hubspot list members
print("Running query for Today's Riders Hubspot list members...")
print('')
cursor.execute("""
SELECT
[First Name],
[Last Name],
Email
FROM DBO.Hubspot_Lists HL WITH (NOLOCK)
INNER JOIN DBO.Hubspot_Spin_Contacts H WITH (NOLOCK) ON HL.[Hubspot ID] = H.[Hubspot ID]
WHERE
HL.[List ID] = '3'
""")
rows = cursor.fetchall()
for row in rows:
    FirstName = row[0]
    LastName = row[1]
    Email = row[2]
    HubspotList = HubspotList + '<li class="x_x_ContentPasted0 x_ContentPasted0" style="list-style:disc">' + FirstName + " " + LastName + " - " + Email + "<BR>"
HubspotList = HubspotList + '</li>'
sleep(1)

# Close cursor
cursor.close()
print('Cursor closed.')
print('')

# Sender's email address

# Recipient's email address

# Create message container - the correct MIME type is multipart/alternative
msg = MIMEMultipart()

# Add Subject Line Here
msg['Subject'] = "Spinning Data Download Report - %s" % (today)
print()
print("Email subject: " + msg['Subject'])
print()

msg['From'] = 'Andrew Gutierrez'
msg['To'] = toaddr
print("Sent to: " + toaddr)
print()

# Enter the body of the message here
text = """test"""

html = """\
<html>
<head></head>
<body style='font-size:12.0pt;font-family:"Aptos",sans-serif;color:black'>
<BR>
<B>Most Recent Ride:</B>
<BR>
%s - %s
<BR>
%s, %s
<BR>
Count: %s riders
<BR>
<BR>
<B>Rider List:</B>
<BR>
<span>%s</span>
<BR>
<B>Ride playlist:</B>
<BR>
%s
<BR>
<BR>
<B>Playlist tracks:</B>
<BR>
%s
<BR>
<B>Upcoming Rides:</B>
<BR>
%s
<BR>
<B>FFC Class Stats:</B>
<BR>
Total classes taught: <B>%s <span style="color: #5ABE25;">(+%s)</span></B>
<BR>
Total rides: <B>%s <span style="color: #5ABE25;">(+%s)</span></B>
<BR>
Total unique riders: <B>%s <span style="color: #5ABE25;">(+%s)</span></B>
<BR>
Total playlists: <B>%s <span style="color: #5ABE25;">(+%s)</span></B>
<BR>
<BR>
<B>Hubspot Contacts:</B> %s <B><span style="color: #5ABE25;">(+%s)</span></B>
<BR>
<BR>
<B>"Today's Riders" Hubspot list members:</B>
<BR>
<span>%s</span>
<BR>
<BR>
</body>
</html>
""" % (Class, Club, Day, str(Date), str(Count), RiderList, playlist, ArtistList, RidesList, no_of_classes, no_of_classes_diff, no_of_rides, no_of_rides_diff, no_of_riders, no_of_riders_diff, no_of_playlists, no_of_playlists_diff, no_of_hubspot_contacts, no_of_hubspot_contacts_diff, HubspotList)

# Record the MIME types of both parts - text/plain and text/html
part1 = MIMEText (text, 'plain')
part2 = MIMEText (html, 'html')

# Attach parts into message container
# According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred
# msg.attach(part1)
msg.attach(part2)

# Enter username and password for SMTP Server connection
print()
context = ssl.create_default_context()

# CONNECT TO SMTP SERVER
try:
    s = smtplib.SMTP('smtp.gmail.com',587)
    s.ehlo()
    s.starttls(context=context)
    s.ehlo()
    s.ehlo()
    s.login(me, pw)
    print()
    print("Connected to SMTP server")
    print()
except:
    print("Error: unable to connect to SMTP server")
    print(garbage)

# SEND EMAIL MESSAGE
try:
    s.sendmail(me, toaddr, msg.as_string())
    s.quit()
    print("Successfully sent email")
    print()
except Exception as E:
    print("Error: unable to send email")
    print(str(E))
    s.quit()

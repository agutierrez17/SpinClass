import requests
import json
import pyodbc
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, BatchInputSimplePublicObjectBatchInput, ApiException
from hubspot.crm.lists import ApiException
from time import sleep

# Access token

# Connect to API
client = hubspot.Client.create(access_token="%s" % (token))

##################### GET EXISTING CONTACTS #######################
url = "https://api.hubapi.com/crm/v3/objects/contacts"

def get_all_contacts():
    rowlist = []
    after = None
    print('Retrieving list of all current contacts from Hubspot...')
    while True:
        try:
            contacts = client.crm.contacts.basic_api.get_page(limit=100, properties=["hs_object_id","firstname","lastname","email","hs_email_optout","hs_email_first_click_date","hs_email_first_open_date","hs_email_first_send_date","hs_email_last_click_date","hs_email_last_open_date","hs_email_last_send_date","hs_email_last_email_name","hs_email_bounce","hs_email_click","hs_email_delivered","hs_email_open","hs_email_optout_527137114","hs_email_sends_since_last_engagement",], archived=False, after=after)

            # Loop through contacts in response
            for contact in contacts.results:
                hs_object_id = contact.properties["hs_object_id"]
                email = contact.properties["email"]
                lastname = contact.properties["lastname"]
                firstname = contact.properties["firstname"]
                hs_email_optout = bool(contact.properties["hs_email_optout"])
                hs_email_optout_527137114 = bool(contact.properties["hs_email_optout_527137114"])
                createdate = contact.properties["createdate"]
                lastmodifieddate = contact.properties["lastmodifieddate"]
                hs_email_delivered = contact.properties["hs_email_delivered"]
                hs_email_open = contact.properties["hs_email_open"]
                hs_email_click = contact.properties["hs_email_click"]
                hs_email_bounce = contact.properties["hs_email_bounce"]
                hs_email_first_send_date = contact.properties["hs_email_first_send_date"]
                hs_email_first_open_date = contact.properties["hs_email_first_open_date"]
                hs_email_first_click_date = contact.properties["hs_email_first_click_date"]
                hs_email_last_send_date = contact.properties["hs_email_last_send_date"]
                hs_email_last_open_date = contact.properties["hs_email_last_open_date"]
                hs_email_last_click_date = contact.properties["hs_email_last_click_date"]
                hs_email_sends_since_last_engagement = contact.properties["hs_email_sends_since_last_engagement"]

                row = (hs_object_id,email,lastname,firstname,hs_email_optout,hs_email_optout_527137114,createdate,lastmodifieddate,hs_email_delivered,hs_email_open,hs_email_click,hs_email_bounce,hs_email_first_send_date,hs_email_first_open_date,hs_email_first_click_date,hs_email_last_send_date,hs_email_last_open_date,hs_email_last_click_date,hs_email_sends_since_last_engagement)
                rowlist.append(row)

            if contacts.paging and contacts.paging.next:
                after = contacts.paging.next.after
            else:
                break
                       
        except Exception as e:
            print("Exception when calling basic_api->get_page: %s\n" % e)

    return rowlist

# Call get all contacts function
rowlist = get_all_contacts()

# Connect to database and open SQL cursor
print('Connecting to database...')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Truncate Hubspot Records table
cursor.execute("""TRUNCATE TABLE [dbo].[Hubspot_Spin_Contacts]""")
cursor.commit()

# Insert records into Hubspot Records table
print('Inserting records into Hubspot Records Table...')
cursor.executemany("""
INSERT INTO [dbo].[Hubspot_Spin_Contacts]
           ([Hubspot ID]
           ,[Email]
           ,[Last Name]
           ,[First Name]
           ,[Hubspot Opt Out]
           ,[Marketing Email Opt Out]
           ,[Create Date]
           ,[Last Modified Date]
           ,[Emails Delivered]
           ,[Emails Opened]
           ,[Emails Clicked]
           ,[Emails Bounced]
           ,[First Send Date]
           ,[First Open Date]
           ,[First Click Date]
           ,[Last Send Date]
           ,[Last Open Date]
           ,[Last Click Date]
           ,[Sends Since Last Engagement])
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",rowlist)
cursor.commit()

print('All records inserted')
print('')

##################### CREATE NEW CONTACTS #######################
url = "https://api.hubapi.com/crm/v3/objects/contacts"

# Query Hubspot view
print('Querying data for new Hubspot contacts...')
cursor.execute("""
SELECT 
[First Name],
[Last Name],
[Email],
[First Ride],
[Most Recent Ride],
[Most Recent Ride Format],
[Most Recent Ride Location],
[Most Recent Ride Playlist],
[Number of Rides],
[Most Recent Playlist Image],
[Upcoming Ride Location 1],
[Upcoming Ride Time 1],
[Upcoming Ride Location 2],
[Upcoming Ride Time 2],
[Upcoming Ride Location 3],
[Upcoming Ride Time 3]
FROM [SpinClass].[dbo].[HubspotUpload]
""")
rows = cursor.fetchall()

# Loop through rows in view, add to json
print('Looping through all rows...')
for row in rows:
    firstname = row[0]
    lastname = row[1]
    email = row[2]
    first_ride = row[3]
    most_recent_ride = row[4]
    most_recent_ride_format = row[5]
    most_recent_ride_location = row[6]
    most_recent_ride_playlist = row[7]
    number_of_rides = row[8]
    most_recent_image = row[9]
    upcoming_ride_1 = row[10]
    upcoming_ride_time_1 = row[11]
    upcoming_ride_2 = row[12]
    upcoming_ride_time_2 = row[13]
    upcoming_ride_3 = row[14]
    upcoming_ride_time_3 = row[15]

    properties = {
    "email": email,
    "firstname": firstname,
    "lastname": lastname,
    "first_ride_date": first_ride,
    "most_recent_ride": most_recent_ride,
    "most_recent_format": most_recent_ride_format,
    "most_recent_club": most_recent_ride_location,
    "most_recent_ride_playlist_link": most_recent_ride_playlist,
    "number_of_rides": number_of_rides,
    "most_recent_ride_image": most_recent_image,
    "upcoming_ride_1": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_1+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_1+' '
                    '</span></h2>',
    "upcoming_ride_2": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_2+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_2+' '
                    '</span></h2>',
    "upcoming_ride_3": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_3+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_3+' '
                    '</span></h2>'
    }

    # Create record via API
    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=properties)
    
    try:
        api_response = client.crm.contacts.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)
        #print(api_response)
        sleep(2)
    except Exception as e:
        print("Exception when calling batch_api->create: %s\n" % e)
        cursor.execute("""INSERT INTO [dbo].[BadEmails] VALUES (?)""", (email))
        cursor.commit()

print('All new records created')
print('')

##################### UPDATE EXISTING CONTACTS #######################
url = "https://api.hubapi.com/crm/v3/objects/contacts/batch/update"
rowlist = []

# Query Hubspot view
print('Querying data for updating existing Hubspot contacts...')
cursor.execute("""
SELECT 
[Hubspot ID],
[First Name],
[Last Name],
[Email],
[First Ride],
[Most Recent Ride],
[Most Recent Ride Format],
[Most Recent Ride Location],
[Most Recent Ride Playlist],
[Number of Rides],
[Most Recent Playlist Image],
[Upcoming Ride Location 1],
[Upcoming Ride Time 1],
[Upcoming Ride Location 2],
[Upcoming Ride Time 2],
[Upcoming Ride Location 3],
[Upcoming Ride Time 3]
FROM [SpinClass].[dbo].[HubspotUpdate]
""")
rows = cursor.fetchall()

# Loop through rows in view, add to json
i = 1
o = 1
print('Looping through all rows...')
for row in rows:
    vid = row[0]
    firstname = row[1]
    lastname = row[2]
    email = row[3]
    first_ride = row[4]
    most_recent_ride = row[5]
    most_recent_ride_format = row[6]
    most_recent_ride_location = row[7]
    most_recent_ride_playlist = row[8]
    number_of_rides = row[9]
    most_recent_image = row[10]
    upcoming_ride_1 = row[11]
    upcoming_ride_time_1 = row[12]
    upcoming_ride_2 = row[13]
    upcoming_ride_time_2 = row[14]
    upcoming_ride_3 = row[15]
    upcoming_ride_time_3 = row[16]

    properties = {
    "email": email,
    "firstname": firstname,
    "lastname": lastname,
    "first_ride_date": first_ride,
    "most_recent_ride": most_recent_ride,
    "most_recent_format": most_recent_ride_format,
    "most_recent_club": most_recent_ride_location,
    "most_recent_ride_playlist_link": most_recent_ride_playlist,
    "number_of_rides": number_of_rides,
    "most_recent_ride_image": most_recent_image,
    "upcoming_ride_1": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_1+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_1+' '
                    '</span></h2>',
    "upcoming_ride_2": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_2+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_2+' '
                    '</span></h2>',
    "upcoming_ride_3": '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 16px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="font-family: '
                    'Helvetica, Arial, sans-serif; '
                    'color: '
                    '#ffffff;"><strong>'+upcoming_ride_3+' '
                    '</strong></span></h2>\n '
                    '<h2 style="margin:0; '
                    'mso-line-height-rule:exactly; '
                    'font-size: 14px; '
                    'line-height: 150%; '
                    'text-align: center; '
                    'font-weight: normal;" '
                    'align="center"><span '
                    'style="color: #ffffff; '
                    'font-family: Helvetica, '
                    'Arial, sans-serif;">'+upcoming_ride_time_3+' '
                    '</span></h2>'
    }
    row = {"id": vid, "properties": properties}
    rowlist.append(row)
    i = i + 1
    o = o + 1

    if i > 100 or o > len(rows):
        # Update records via API
        print('Updating records through API...')
        batch_input_simple_public_object_batch_input = BatchInputSimplePublicObjectBatchInput(inputs=rowlist)

        try:
            api_response = client.crm.contacts.batch_api.update(batch_input_simple_public_object_batch_input=batch_input_simple_public_object_batch_input)
            # print(api_response)
            print('All existing records updated')
            print('')
        except Exception as e:
            print("Exception when calling batch_api->update: %s\n" % e)
        rowlist = []
        i = 1
        sleep(5)

############### GET LIST MEMBERSHIP #################
url1 = "https://api.hubapi.com/crm/v3/lists/{listId}"
url2 = "https://api.hubapi.com/crm/v3/lists/{listId}/memberships/join-order"
rowlist = []

# Get list membership from API
print('Retrieving Today''s Riders list info and members from API...')
for list_id in ["3","4","5"]:
    try:
        api_response = client.crm.lists.lists_api.get_by_id(list_id=list_id, include_filters=False)
        # print(api_response)
        id = api_response.list.list_id
        list_name = api_response.list.name
        
        
        api_response2 = client.crm.lists.memberships_api.get_page_ordered_by_added_to_list_date(list_id=list_id, limit=100)
        # print(api_response2)
        
        for rider in api_response2.results:
            vid = rider.record_id
            date_added = rider.membership_timestamp
            row = (vid, date_added, id, list_name)
            rowlist.append(row)
        
    except ApiException as e:
        print("Exception when calling memberships_api->get_page_ordered_by_added_to_list_date: %s\n" % e)

# Truncate Hubspot Lists table
cursor.execute("""TRUNCATE TABLE [dbo].[Hubspot_Lists]""")
cursor.commit()

# Insert records into Hubspot Lists table
print('Inserting records into Hubspot Lists table...')
cursor.executemany("""INSERT INTO [dbo].[Hubspot_Lists] ([Hubspot ID],[Date Added],[List ID],[List Name]) VALUES (?,?,?,?)""",rowlist)
cursor.commit()

print('All records inserted')
print('')

# REFRESH HUBSPOT CONTACTS TABLE AGAIN
rowlist = get_all_contacts()

# Connect to database and open SQL cursor
print('Connecting to database...')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Truncate Hubspot Records table
cursor.execute("""TRUNCATE TABLE [dbo].[Hubspot_Spin_Contacts]""")
cursor.commit()

# Insert records into Hubspot Records table
print('Inserting records into Hubspot Records Table...')
cursor.executemany("""
INSERT INTO [dbo].[Hubspot_Spin_Contacts]
           ([Hubspot ID]
           ,[Email]
           ,[Last Name]
           ,[First Name]
           ,[Hubspot Opt Out]
           ,[Marketing Email Opt Out]
           ,[Create Date]
           ,[Last Modified Date]
           ,[Emails Delivered]
           ,[Emails Opened]
           ,[Emails Clicked]
           ,[Emails Bounced]
           ,[First Send Date]
           ,[First Open Date]
           ,[First Click Date]
           ,[Last Send Date]
           ,[Last Open Date]
           ,[Last Click Date]
           ,[Sends Since Last Engagement])
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",rowlist)
cursor.commit()

print('All records inserted')
print('')

############### DELETE UNSUBSCRIBED AND EXPIRED CONTACTS #################
URL = "https://api.hubapi.com/crm/v3/objects/contacts/"

# Query Hubspot view
print('Querying data for contacts to delete...')
cursor.execute("""
SELECT 
[Hubspot ID],
[Email]
FROM [SpinClass].[dbo].[HubspotContactsToDelete]
""")
rows = cursor.fetchall()

# Loop through rows 
print('Looping through all rows...')
for row in rows:
    vid = row[0]
    email = row[1]

    try:
        api_response = client.crm.contacts.basic_api.archive(contact_id=vid)
        print('Deleted record - %s' % str(email))
    except ApiException as e:
        print("Exception when calling basic_api->archive: %s\n" % e)
print('')

# Run archive insert procedure
cursor.execute("""EXEC [dbo].[HubspotContactsArchiveInsert];""")
cursor.commit()

# REFRESH HUBSPOT CONTACTS TABLE ONE MORE TIME
rowlist = get_all_contacts()

# Connect to database and open SQL cursor
print('Connecting to database...')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# Truncate Hubspot Records table
cursor.execute("""TRUNCATE TABLE [dbo].[Hubspot_Spin_Contacts]""")
cursor.commit()

# Insert records into Hubspot Records table
print('Inserting records into Hubspot Records Table...')
cursor.executemany("""
INSERT INTO [dbo].[Hubspot_Spin_Contacts]
           ([Hubspot ID]
           ,[Email]
           ,[Last Name]
           ,[First Name]
           ,[Hubspot Opt Out]
           ,[Marketing Email Opt Out]
           ,[Create Date]
           ,[Last Modified Date]
           ,[Emails Delivered]
           ,[Emails Opened]
           ,[Emails Clicked]
           ,[Emails Bounced]
           ,[First Send Date]
           ,[First Open Date]
           ,[First Click Date]
           ,[Last Send Date]
           ,[Last Open Date]
           ,[Last Click Date]
           ,[Sends Since Last Engagement])
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",rowlist)
cursor.commit()

print('All records inserted')
print('')

cursor.close()
conn.close()

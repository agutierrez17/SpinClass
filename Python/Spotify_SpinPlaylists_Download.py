import spotipy
from spotipy.oauth2 import SpotifyOAuth
import win32com.client as win32
from datetime import timedelta, datetime
import time
from requests.exceptions import ReadTimeout
import pyodbc
from time import sleep

def convertMStoTime(ms):
    seconds = (ms/1000)
    #print(seconds)
    td = timedelta(seconds=seconds)

    return td

# Connect to database and open SQL cursor
print('Connecting to database...')
print('')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# API Credentials
print('Connecting to Spotify API...')
print('')
                                               redirect_uri="http://localhost:3000",
                                               scope="playlist-read-private"),requests_timeout=20, retries=10)

# Loop through user playlists, pull down list of ids from "Spin" playlists
print('Grabbing all spin playlist IDs...')
print('')
i = 0
playlist_ids = []
playlists = sp.current_user_playlists(limit=50, offset=0)
while playlists["next"]:
    for item in playlists["items"]:
        if item is None:
            pass
        elif ('spin ' in item["name"] or 'Spin ' in item["name"] or ' Spin' in item["name"] or 'FFC' in item["name"]) and item["owner"]["id"] == 'andrewgoot':
            playlist_ids.append(item["id"])
    playlists = sp.next(playlists)

row_list = []
tracks_playlists = []
playlist_art = []

# Get data for each playlist
print('Pulling down full playlist data...')
print('')
for ids in playlist_ids:
    playlist = sp.playlist(ids)
    id = playlist["id"]
    name = playlist["name"]
    collaborative = playlist["collaborative"]
    spotify_url = playlist["external_urls"]["spotify"]
    href = playlist["href"]
    owner_id = playlist["owner"]["id"]
    owner_name = playlist["owner"]["display_name"]
    owner_url = playlist["owner"]["external_urls"]["spotify"]
    owner_href = playlist["owner"]["href"]
    owner_type = playlist["owner"]["type"]
    owner_uri = playlist["owner"]["uri"]
    primary_color = playlist["primary_color"]
    public = playlist["public"]
    snapshot_id = playlist["snapshot_id"]
    type = playlist["type"]
    uri = playlist["uri"]
    number_of_tracks = playlist["tracks"]["total"]
    tracks_href = playlist["tracks"]["href"]

    row = (id, name, collaborative, spotify_url, href, owner_id, owner_name, owner_url, owner_href, owner_type, owner_uri, primary_color, public, snapshot_id, type, uri, number_of_tracks, tracks_href)
    row_list.append(row)

    # Get album cover
    for image in playlist["images"]:
        imageurl = image["url"]
        height = image["height"]
        width = image["width"]
        playlist_art.append([id, imageurl, height, width])
    
    tracks = sp.playlist_items(id)
    j = 1

    # Pull down track info
    while j <= number_of_tracks:
        for track in tracks["items"]:
            track_id = track["track"]["id"]
            added_at = track["added_at"]
            playlist_order = j
            row_1 = (id, track_id, added_at, playlist_order)
            tracks_playlists.append(row_1)
            j = j + 1
        if tracks["next"]:
            tracks = sp.next(tracks)

# INSERT DATA INTO PLAYLISTS TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Playlists]""")
cursor.commit()

print('Inserting playlist data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Playlists] ([ID],[Name],[Collaborative],[Spotify URL],[Href],[Owner ID],[Owner Name],[Owner URL],[Owner Href],[Owner Type],[Owner URI],[Primary Color],[Public],[Snapshot ID],[Type],[URI],[Number of Tracks],[Tracks Href])
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", row_list)
cursor.commit()
sleep(1)

print('All playlists inserted')
print('')

# INSERT DATA INTO PLAYLIST ARTWORK TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Playlist_Artwork]""")
cursor.commit()

print('Inserting playlist artwork data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Playlist_Artwork] ([Playlist ID],[Image URL],[Height],[Width]) VALUES (?,?,?,?)""", playlist_art)
cursor.commit()
sleep(1)

print('All playlist artwork data inserted')
print('')


# INSERT DATA INTO PLAYLIST-TRACKS TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[PlaylistTracks]""")
cursor.commit()

print('Inserting playlist-tracks data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[PlaylistTracks] ([Playlist ID],[Track ID],[Added At],[Playlist Order]) VALUES (?,?,?,?)""", tracks_playlists)
cursor.commit()
sleep(1)

print('All playlist-track data inserted')
print('')

# GET FULL TRACK INFO FROM TRACKS API
print('Grabbing all song IDs...')
print('')
track_ids = []
for track in tracks_playlists:
    track_ids.append(track[1])

track_ids = list(set(track_ids))
track_ids = [x for x in track_ids if x is not None]
track_data = []
tracks_artists = []
tracks_albums = []
k = 0
l = 100

print('Pulling down full song data...')
print('')
while l < len(track_ids) + 2:
    songlist = sp.tracks(track_ids[k:l])
    #features_list = sp.audio_features(track_ids[k:l]) # Uncomment if access to audio features is restored
    #for song, feature in zip(songlist["tracks"],features_list): # Uncomment if access to audio features is restored
    for song in songlist["tracks"]: # COMMENT THIS OUT IF AUDIO FEATURES COME BACK
        id = song["id"]
        name = song["name"]
        preview_url = song["preview_url"]
        explicit = song["explicit"]
        type = song["type"]
        duration = song["duration_ms"]
        length = str(convertMStoTime(duration))
        external_url = song["external_urls"]['spotify']
        track_href = song["href"]
        popularity = song["popularity"]
        track_uri = song["uri"]
        is_local = song["is_local"]
        track_number = song["track_number"]

##        # Get Audio features
##        danceability = feature["danceability"]
##        energy = feature["energy"]
##        key = feature["key"]
##        loudness = feature["loudness"]
##        mode = feature["mode"]
##        speechiness = feature["speechiness"]
##        acousticness = feature["acousticness"]
##        instrumentalness = feature["instrumentalness"]
##        liveness = feature["liveness"]
##        valence = feature["valence"]
##        tempo = round(feature["tempo"])    

        row = (id, name, preview_url, explicit, type, duration, length, external_url, track_href, popularity, track_uri, is_local, track_number)
              # danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo) # Uncomment if access to audio features is restored
        track_data.append(row)

        # Get track-artist info
        for artist in song["artists"]:
            artist_id = artist["id"]
            tracks_artists.append([id, artist_id])

        # Get track-album info
        album_id = song["album"]["id"]
        tracks_albums.append([id, album_id])
        
    k = k + 100
    if l == len(track_ids) + 1:
        break
    elif l + 100 > len(track_ids):
        l = len(track_ids) + 1
    else:
        l = l + 100

# INSERT DATA INTO TRACKS TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Tracks]""")
cursor.commit()

print('Inserting track data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Tracks]
           ([Track ID]
           ,[Track Name]
           ,[Preview URL]
           ,[Explicit]
           ,[Track Type]
           ,[Duration (ms)]
           ,[Track Length]
           ,[External URL]
           ,[Track Href]
           ,[Popularity]
           ,[Track URI]
           ,[Is Local]
           ,[Track Number]
           --,[Danceability]
           --,[Energy]
           --,[Key]
           --,[Loudness]
           --,[Mode]
           --,[Speechiness]
           --,[Acousticness]
           --,[Instrumentalness]
           --,[Liveness]
           --,[Valence]
           --,[Tempo]
           )
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", track_data) # Add back 11 ?'s here if we get access to audio features back
cursor.commit()
sleep(1)

print('All track data inserted')
print('')

# INSERT DATA INTO ARTISTS-TRACKS TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Tracks_Artists]""")
cursor.commit()

print('Inserting track-artist data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Tracks_Artists] ([Track ID],[Artist ID]) VALUES (?,?)""", tracks_artists)
cursor.commit()
sleep(1)

print('All track-artist data inserted')
print('')

# INSERT DATA INTO TRACKS-ALBUMS TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Tracks_Albums]""")
cursor.commit()

print('Inserting track-album data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Tracks_Albums] ([Track ID],[Album ID]) VALUES (?,?)""", tracks_albums)
cursor.commit()
sleep(1)

print('All track-album data inserted')
print('')

# GET FULL ARTIST INFO FROM ARTISTS API
print('Grabbing all artist IDs...')
print('')
artist_ids = []
for artist in tracks_artists:
    artist_ids.append(artist[1])

artist_ids = list(set(artist_ids))
artist_ids = [x for x in artist_ids if x is not None]
k = 0
l = 50

# LOOP THROUGH AND DOWNLOAD ARTIST AND GENRE DATA
artist_list = []
artists_genres = []

print('Pulling down full artist and genre data...')
print('')
while l < len(track_ids) + 2:
    artists = sp.artists(artist_ids[k:l])
    for artist in artists["artists"]:
        artist_id = artist["id"]
        artist_name = artist["name"]
        artist_url = artist["external_urls"]["spotify"]
        followers = artist["followers"]["total"]
        artist_popularity = artist["popularity"]
        artist_type = artist["type"]
        artist_uri = artist["uri"]
        artist_href = artist["href"]
        for genre in artist["genres"]:
            artists_genres.append([artist_id, genre])
        
        row = (artist_id, artist_name, artist_url, followers, artist_popularity, artist_type, artist_uri, artist_href)
        artist_list.append(row)

    k = k + 50
    if l == len(artist_ids) + 1:
        break
    elif l + 50 > len(artist_ids):
        l = len(artist_ids) + 1
    else:
        l = l + 50

# INSERT ARTIST DATA INTO DATABASE
cursor.execute("""TRUNCATE TABLE [dbo].[Artists]""")
cursor.commit()

print('Inserting artists data into database...')
print('')
cursor.executemany("""INSERT INTO [dbo].[Artists] ([Artist ID],[Artist Name],[Artist URL],[Followers],[Popularity],[Artist Type],[Artist URI],[Artist Href]) VALUES (?,?,?,?,?,?,?,?)""", artist_list)
cursor.commit()
sleep(1)

print('All artist data inserted')
print('')

# INSERT ARTIST-GENRE DATA INTO DATABASE
cursor.execute("""TRUNCATE TABLE [dbo].[Artists_Genres]""")
cursor.commit()

print('Inserting artist-genre data into database...')
print('')
cursor.executemany("""INSERT INTO [dbo].[Artists_Genres] ([Artist ID],[Genre])VALUES (?,?)""", artists_genres)
cursor.commit()
sleep(1)

print('All artist-genre data inserted')
print('')

# GET FULL ALBUM INFO FROM ALBUMS API
print('Grabbing all album IDs...')
print('')
album_ids = []
for album in tracks_albums:
    album_ids.append(album[1])

album_ids = list(set(album_ids))
album_ids = [x for x in album_ids if x is not None]
k = 0
l = 20

# LOOP THROUGH AND DOWNLOAD ALBUM DATA
album_list = []
album_artwork = []
albums_artists = []

print('Pulling down full album data...')
print('')
while l < len(album_ids) + 2:
    albums = sp.albums(album_ids[k:l])
    for album in albums["albums"]:
        album_id = album["id"]
        album_name = album["name"]
        release_date = album["release_date"]
        album_type = album["album_type"]
        total_tracks = album["total_tracks"]
        album_url = album["external_urls"]["spotify"]
        album_href = album["href"]
        album_uri = album["uri"]
        
        for artist in album["artists"]:
            albums_artists.append([album_id, artist["id"]])

        for image in album["images"]:
            imageurl = image["url"]
            height = image["height"]
            width = image["width"]
            album_artwork.append([album_id, imageurl, height, width])
        
        row = (album_id, album_name, release_date, album_type, total_tracks, album_url, album_href, album_uri)
        album_list.append(row)

    k = k + 20
    if l == len(album_ids) + 1:
        break
    elif l + 20 > len(album_ids):
        l = len(album_ids) + 1
    else:
        l = l + 20

# INSERT ALBUM DATA INTO DATABASE
cursor.execute("""TRUNCATE TABLE [dbo].[Albums]""")
cursor.commit()

print('Inserting albums into database...')
print('')
cursor.executemany("""INSERT INTO [dbo].[Albums] ([Album ID],[Album Name],[Release Date],[Album Type],[Total Tracks],[External URL],[Album Href],[Album URI]) VALUES (?,?,?,?,?,?,?,?)""", album_list)
cursor.commit()
sleep(1)

print('All album data inserted')
print('')

# INSERT ALBUM-ARTIST DATA INTO DATABASE
cursor.execute("""TRUNCATE TABLE [dbo].[Albums_Artists]""")
cursor.commit()

print('Inserting album-artist data into database...')
print('')
cursor.executemany("""INSERT INTO [dbo].[Albums_Artists] ([Album ID],[Artist ID]) VALUES (?,?)""", albums_artists)
cursor.commit()
sleep(1)

print('All album-artist data inserted')
print('')

# INSERT DATA INTO ALBUM ARTWORK TABLE
cursor.execute("""TRUNCATE TABLE [dbo].[Album_Artwork]""")
cursor.commit()

print('Inserting album artwork data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[Album_Artwork] ([Album ID],[Image URL],[Height],[Width]) VALUES (?,?,?,?)""", album_artwork)
cursor.commit()
sleep(1)

print('All album artwork data inserted')
print('')

print('Closing SQL cursor')
# CLOSE CURSOR
cursor.close()
conn.close()

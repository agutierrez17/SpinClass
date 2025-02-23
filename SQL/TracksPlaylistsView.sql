USE [SpinClass]
GO

/****** Object:  View [dbo].[Classes_Playlists]    Script Date: 12/3/2024 10:21:40 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [dbo].[Tracks_Historical] AS

WITH CTE AS (
SELECT DISTINCT
PT.[Track ID],
PT.[Playlist ID],
CP.[Class Date] ,
ROW_NUMBER() OVER (PARTITION BY PT.[Track ID] ORDER BY CP.[Class Date] DESC) AS Rw
FROM DBO.PlaylistTracks PT WITH (NOLOCK)
INNER JOIN DBO.Classes_Playlists CP WITH (NOLOCK) ON PT.[Playlist ID] = CP.[Playlist ID]
)

SELECT
[ID],
[Name],
[Spotify URL],
[URI],
[Number of Tracks],
PA.[Image URL] AS "Playlist Image URL - 640",
PA2.[Image URL] AS "Playlist Image URL - 300",
PA3.[Image URL] AS "Playlist Image URL - 60",
PT.[Playlist Order],
PT.[Track ID],
T.[Track Name],
T.[Track Length],
T.[External URL] AS "Track URL",
(SELECT STUFF((
        SELECT ', ' + A.[Artist Name]
        FROM DBO.Artists A WITH (NOLOCK)
		INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON A.[Artist ID] = TA.[Artist ID]
        WHERE TA.[Track ID] = T.[Track ID]
		ORDER BY A.[Artist Name]
        FOR XML PATH('')), 1, 2, ''))  AS Artists,
CTE.[Class Date] AS "Last Time Played",
(SELECT COUNT(DISTINCT CTE.[Class Date]) FROM CTE WHERE T.[Track ID] = CTE.[Track ID]) AS "Number of Plays",
DATEDIFF(Day, CTE.[Class Date],GETDATE()) AS "Days Since Last Play",
DATEDIFF(Week, CTE.[Class Date],GETDATE()) AS "Weeks Since Last Play",
A.[Album ID],
A.[Album Name],
A.[External URL] AS "Album URL",
AA.[Image URL] AS "Album Cover URL - 640",
AA2.[Image URL] AS "Album Cover URL - 300",
AA3.[Image URL] AS "Album Cover URL - 64"

FROM DBO.Tracks T WITH (NOLOCK) 
INNER JOIN DBO.PlaylistTracks PT WITH (NOLOCK) ON PT.[Track ID] = T.[Track ID]
INNER JOIN [SpinClass].[dbo].[Playlists] P WITH (NOLOCK) ON PT.[Playlist ID] = P.ID
INNER JOIN CTE ON T.[Track ID] = CTE.[Track ID] AND CTE.Rw = 1
LEFT OUTER JOIN DBO.Playlist_Artwork PA WITH (NOLOCK) ON P.ID = PA.[Playlist ID] AND PA.Height = '640'
LEFT OUTER JOIN DBO.Playlist_Artwork PA2 WITH (NOLOCK) ON P.ID = PA2.[Playlist ID] AND PA2.Height = '300'
LEFT OUTER JOIN DBO.Playlist_Artwork PA3 WITH (NOLOCK) ON P.ID = PA3.[Playlist ID] AND PA3.Height = '60'
LEFT OUTER JOIN DBO.Tracks_Albums TA WITH (NOLOCK) ON T.[Track ID] = TA.[Track ID]
LEFT OUTER JOIN DBO.Albums A WITH (NOLOCK) ON A.[Album ID] = TA.[Album ID]
LEFT OUTER JOIN DBO.Album_Artwork AA WITH (NOLOCK) ON A.[Album ID] = AA.[Album ID] AND AA.Height = '640'
LEFT OUTER JOIN DBO.Album_Artwork AA2 WITH (NOLOCK) ON A.[Album ID] = AA2.[Album ID] AND AA2.Height = '300'
LEFT OUTER JOIN DBO.Album_Artwork AA3 WITH (NOLOCK) ON A.[Album ID] = AA3.[Album ID] AND AA3.Height = '64'

WHERE
(P.[Name] LIKE '%FFC%' AND P.[Name] LIKE '%[0-9]%%[0-9]%')
OR
P.Name = 'Intro to Spin'

--ORDER BY
--"Weeks Since Last Play",
--[ID],
--[Playlist Order]

GO
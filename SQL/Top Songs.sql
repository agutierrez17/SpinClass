---- TOP SONGS
SELECT
T.[Track ID],
T.[Track Name],
T.[External URL],
T.[Preview URL] ,
MAX(A.[Artist Name]) AS Artist,
COUNT(DISTINCT CONVERT(VARCHAR,CP.[Class Date]) + ' - ' + CONVERT(VARCHAR,CP.[Class Duration]) + ' - ' + CP.[Class Format] + ' - ' + CP.Location) AS "Number of Plays"
FROM [SpinClass].[dbo].[Classes_Playlists] CP WITH (NOLOCK)
INNER JOIN DBO.PlaylistTracks PT WITH (NOLOCK) ON CP.[Playlist ID] = PT.[Playlist ID]
INNER JOIN DBO.Tracks T WITH (NOLOCK) ON PT.[Track ID] = T.[Track ID]
INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON T.[Track ID] = TA.[Track ID]
INNER JOIN DBO.Artists A WITH (NOLOCK) ON TA.[Artist ID] = A.[Artist ID]

GROUP BY
T.[Track ID],
T.[Track Name],
T.[External URL],
T.[Preview URL] 

ORDER BY
COUNT(DISTINCT CONVERT(VARCHAR,CP.[Class Date]) + ' - ' + CONVERT(VARCHAR,CP.[Class Duration]) + ' - ' + CP.[Class Format] + ' - ' + CP.Location)  DESC



---- TOP ARTISTS
SELECT
A.[Artist ID],
A.[Artist Name],
COUNT(DISTINCT CONVERT(VARCHAR,CP.[Class Date]) + ' - ' + CONVERT(VARCHAR,CP.[Class Duration]) + ' - ' + CP.[Class Format] + ' - ' + CP.Location) AS "Number of Plays"
FROM [SpinClass].[dbo].[Classes_Playlists] CP WITH (NOLOCK)
INNER JOIN DBO.PlaylistTracks PT WITH (NOLOCK) ON CP.[Playlist ID] = PT.[Playlist ID]
INNER JOIN DBO.Tracks T WITH (NOLOCK) ON PT.[Track ID] = T.[Track ID]
INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON T.[Track ID] = TA.[Track ID]
INNER JOIN DBO.Artists A WITH (NOLOCK) ON TA.[Artist ID] = A.[Artist ID]

GROUP BY
A.[Artist ID],
A.[Artist Name]

ORDER BY
COUNT(DISTINCT CONVERT(VARCHAR,CP.[Class Date]) + ' - ' + CONVERT(VARCHAR,CP.[Class Duration]) + ' - ' + CP.[Class Format] + ' - ' + CP.Location)  DESC

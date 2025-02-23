SELECT TOP 1
S.Class,
S.Club,
S.Day,
S.Date,
S.Count
FROM DBO.SpinClassCounts S WITH (NOLOCK)

ORDER BY
[Date] Desc


SELECT
FirstName,
LastName
FROM DBO.Riders_Rides
WHERE
DateFormatted = (SELECT MAX([Date]) FROM DBO.SpinClassCounts S WITH (NOLOCK))


SELECT
[Playlist Name]
FROM DBO.Classes_Playlists
WHERE
[Class Date] = (SELECT MAX([Date]) FROM DBO.SpinClassCounts S WITH (NOLOCK))


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


SELECT
COUNT(*)
FROM DBO.Artists
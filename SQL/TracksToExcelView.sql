USE [SpinClass]
GO

/****** Object:  View [dbo].[ExcelTracksView]    Script Date: 1/26/2025 9:57:23 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



ALTER VIEW [dbo].[ExcelTracksView] AS 

SELECT DISTINCT
TB.[External URL],
'' AS "Category",
'' AS "Builder",
'' AS "Ride Code",
'' AS "Position",
TB.[Track Name],
(SELECT STUFF((
        SELECT ', ' + A.[Artist Name]
        FROM DBO.Artists A WITH (NOLOCK)
		INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON A.[Artist ID] = TA.[Artist ID]
        WHERE TA.[Track ID] = TB.[Track ID]
		ORDER BY A.[Artist Name]
        FOR XML PATH('')), 1, 2, ''))  AS Artists,
TB.[Tempo] AS "BPM",
TB.[Tempo] AS "Used RPM",
MAX(TB.[Track Length]) AS "Duration",
'' AS "Genre",
'' AS "Notes"

FROM dbo.TracksBackup TB WITH (NOLOCK)
LEFT OUTER JOIN DBO.SongLibrary S WITH (NOLOCK) ON TB.[Track ID] = REPLACE(S.[External URL],'https://open.spotify.com/track/','')
WHERE
(SELECT STUFF((
        SELECT ', ' + A.[Artist Name]
        FROM DBO.Artists A WITH (NOLOCK)
		INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON A.[Artist ID] = TA.[Artist ID]
        WHERE TA.[Track ID] = TB.[Track ID]
		ORDER BY A.[Artist Name]
        FOR XML PATH('')), 1, 2, '')) IS NOT NULL
AND
S.[External URL] IS NULL

GROUP BY
TB.[External URL],
TB.[Track ID],
TB.[Track Name],
TB.[Tempo]

UNION

SELECT DISTINCT
T.[External URL],
'' AS "Category",
'' AS "Builder",
'' AS "Ride Code",
'' AS "Position",
T.[Track Name],
(SELECT STUFF((
        SELECT ', ' + A.[Artist Name]
        FROM DBO.Artists A WITH (NOLOCK)
		INNER JOIN DBO.Tracks_Artists TA WITH (NOLOCK) ON A.[Artist ID] = TA.[Artist ID]
        WHERE TA.[Track ID] = T.[Track ID]
		ORDER BY A.[Artist Name]
        FOR XML PATH('')), 1, 2, ''))  AS Artists,
T.[Tempo] AS "BPM",
T.[Tempo] AS "Used RPM",
MAX(T.[Track Length]) AS "Duration",
'' AS "Genre",
'' AS "Notes"

FROM [SpinClass].[dbo].[Tracks] T WITH (NOLOCK)
LEFT OUTER JOIN DBO.TracksBackup TB WITH (NOLOCK) ON T.[Track ID] = TB.[Track ID]
LEFT OUTER JOIN DBO.SongLibrary S WITH (NOLOCK) ON T.[Track ID] = REPLACE(S.[External URL],'https://open.spotify.com/track/','')

WHERE
TB.[Track ID] IS NULL
AND
S.[External URL] IS NULL

GROUP BY
T.[External URL],
T.[Track ID],
T.[Track Name],
T.[Tempo]


GO



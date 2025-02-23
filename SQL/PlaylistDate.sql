CREATE VIEW [dbo].[Classes_Playlists] AS

WITH CTE AS (
SELECT 
SCC.Class AS "Class Format",
SCC.Day AS "Day of Week",
SCC.Date AS "Class Date",
SCC.Dur AS "Class Duration",
SCC.Club AS "Location",
SCC.Instructor,
SCC.Count AS "Class Count",
SCC.Cap AS "Club Capacity",

CASE
WHEN SCC.Date IN ('2024-09-18 17:30:00.000','2024-09-22 09:45:00.000') THEN '39IIojYrB3kQ6S6NCiLz29'
WHEN SCC.Date IN ('2024-04-04 18:30:00.000') THEN '7EieZYxvLbi7WA5c8gISvx'
WHEN SCC.Date IN ('2024-09-12 18:30:00.000') THEN '2FlewMRSVkQrTU0QfAv9iY'
ELSE P.[ID] END AS "Playlist ID",

CASE
WHEN SCC.Date IN ('2024-09-18 17:30:00.000','2024-09-22 09:45:00.000') THEN CONVERT(DATETIME,'2024-09-16 00:00:00.000')
WHEN SCC.Date IN ('2024-04-04 18:30:00.000') THEN CONVERT(DATETIME,'2024-04-01 00:00:00.000')
WHEN SCC.Date IN ('2024-09-12 18:30:00.000') THEN CONVERT(DATETIME,'2024-08-24 00:00:00.000')
ELSE CONVERT(DATETIME, REPLACE(SUBSTRING(P.[Name],PATINDEX('%[0-9]%',P.[Name]),LEN(P.[Name])),'.','/')) END AS "Playlist Date",

ROW_NUMBER() OVER (PARTITION BY SCC.Class,SCC.Day,SCC.Date,SCC.Dur,SCC.Club 
ORDER BY 
CASE
WHEN SCC.Date IN ('2024-09-18 17:30:00.000','2024-09-22 09:45:00.000') THEN CONVERT(DATETIME,'2024-09-16 00:00:00.000')
WHEN SCC.Date IN ('2024-04-04 18:30:00.000') THEN CONVERT(DATETIME,'2024-04-01 00:00:00.000')
WHEN SCC.Date IN ('2024-09-12 18:30:00.000') THEN CONVERT(DATETIME,'2024-08-24 00:00:00.000')
ELSE CONVERT(DATETIME, REPLACE(SUBSTRING(P.[Name],PATINDEX('%[0-9]%',P.[Name]),LEN(P.[Name])),'.','/')) END
DESC) AS Rw

FROM [dbo].[SpinClassCounts] SCC WITH (NOLOCK)
LEFT OUTER JOIN [dbo].[Playlists] P WITH (NOLOCK) ON SCC.Date >= CONVERT(DATETIME, REPLACE(SUBSTRING(P.[Name],PATINDEX('%[0-9]%',P.[Name]),LEN(P.[Name])),'.','/'))

WHERE
P.[Name] LIKE '%FFC%'
AND
P.[Name] LIKE '%[0-9]%%[0-9]%'
AND
SCC.Class NOT IN ('Intro To Spin')

---- INTRO CLASSES
UNION

SELECT 
SCC.Class AS "Class Format",
SCC.Day AS "Day of Week",
SCC.Date AS "Class Date",
SCC.Dur AS "Class Duration",
SCC.Club AS "Location",
SCC.Instructor,
SCC.Count AS "Class Count",
SCC.Cap AS "Club Capacity",
P.[ID] AS "Playlist ID",
CONVERT(DATETIME,'2024-01-08') AS "Playlist Date",
1 AS Rw
FROM [dbo].[SpinClassCounts] SCC WITH (NOLOCK),
[dbo].[Playlists] P WITH (NOLOCK) 

WHERE
P.ID = '6CucJoJSlpaiR0lXPbFGAP'
AND
SCC.Class IN ('Intro To Spin')
)

SELECT 
CTE.[Class Date],
CTE.[Class Format],
CTE.Location,
CTE.[Day of Week],
CTE.[Class Duration],
CTE.Instructor,
CTE.[Club Capacity],
CTE.[Class Count],
CTE.[Playlist Date],
CTE.[Playlist ID],
P.[Name] AS "Playlist Name",
[Spotify URL] AS "Playlist URL",
[Owner ID],
[Owner URL],
[Owner URI],
[Public],
[URI],
[Number of Tracks]
FROM CTE WITH (NOLOCK)
INNER JOIN [dbo].[Playlists] P WITH (NOLOCK) ON P.ID = CTE.[Playlist ID]

WHERE
CTE.Rw = 1;

--ORDER BY
--CTE.[Class Date] DESC;

GO
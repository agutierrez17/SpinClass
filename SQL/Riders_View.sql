USE [SpinClass]
GO

/****** Object:  View [dbo].[Riders]    Script Date: 7/5/2025 10:14:25 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO









ALTER VIEW [dbo].[Riders] AS

WITH CTE AS (
SELECT DISTINCT
[FirstName],
[LastName],
[Email],
[Location],
COUNT(DISTINCT [DateFormatted]) AS "Number of Rides",
ROW_NUMBER() OVER (PARTITION BY [FirstName],[LastName],[Email] ORDER BY COUNT(DISTINCT [DateFormatted]) DESC) AS Rw
FROM DBO.Riders_Rides R WITH (NOLOCK)

GROUP BY
[FirstName],
[LastName],
[Email],
[Location]
),

RIDES AS (
SELECT
[FirstName],
[LastName],
[Email],
[DateFormatted],
ISNULL(DATEDIFF(DAY,LAG([DateFormatted]) OVER (PARTITION BY [FirstName],[LastName],[Email] ORDER BY COUNT(DISTINCT [DateFormatted]) DESC), [DateFormatted]),0) AS "Days Between Rides",
ISNULL(DATEDIFF(WEEK,LAG([DateFormatted]) OVER (PARTITION BY [FirstName],[LastName],[Email] ORDER BY COUNT(DISTINCT [DateFormatted]) DESC), [DateFormatted]),0) AS "Weeks Between Rides"
FROM DBO.Riders_Rides R WITH (NOLOCK)

GROUP BY
[FirstName],
[LastName],
[Email],
[DateFormatted]
),

LAST_RIDES AS (
SELECT DISTINCT
[FirstName],
[LastName],
[Email],
R.[Location],
R.[Class Format],
CP.[Playlist URL],
CP.[Playlist ID],
ROW_NUMBER() OVER (PARTITION BY [FirstName],[LastName],[Email] ORDER BY [DateFormatted] DESC) AS Rw
FROM DBO.Riders_Rides R WITH (NOLOCK)
INNER JOIN DBO.Classes_Playlists CP WITH (NOLOCK) ON R.DateFormatted = CP.[Class Date]
)

SELECT DISTINCT
AC.ID AS "Rider ID",
R.[FirstName] AS "First Name",
R.[LastName] AS "Last Name",
R.[Email],
MIN(R.[DateFormatted]) AS "First Ride",
MAX(R.[DateFormatted]) AS "Most Recent Ride",
LAST_RIDES.[Class Format] AS "Most Recent Ride Format",
LAST_RIDES.[Location] AS "Most Recent Ride Location",
LAST_RIDES.[Playlist URL] AS "Most Recent Ride Playlist",
LAST_RIDES.[Playlist ID] AS "Most Recent Playlist ID",
--(SELECT [Class Format] FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Format",
--(SELECT Location FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Location",
--(SELECT [Playlist URL] FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Playlist",
--(SELECT [Playlist ID] FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Playlist ID",
COUNT(DISTINCT R.[DateFormatted]) AS "Number of Rides",
COUNT(DISTINCT R.[Location]) AS "Number of Locations",
CTE.Location AS "Top Location",
(SELECT COUNT(DISTINCT [DateFormatted]) FROM DBO.Riders_Rides R1 WITH (NOLOCK) WHERE R.FirstName = R1.FirstName AND R.LastName = R1.LastName AND R.Email = R1.Email AND R1.DateFormatted >= GETDATE() - 30) AS "Number of Rides - Last Month",
(SELECT COUNT(DISTINCT [DateFormatted]) FROM DBO.Riders_Rides R1 WITH (NOLOCK) WHERE R.FirstName = R1.FirstName AND R.LastName = R1.LastName AND R.Email = R1.Email AND R1.DateFormatted >= GETDATE() - 90) AS "Number of Rides - Last Three Months",
(SELECT COUNT(DISTINCT [DateFormatted]) FROM DBO.Riders_Rides R1 WITH (NOLOCK) WHERE R.FirstName = R1.FirstName AND R.LastName = R1.LastName AND R.Email = R1.Email AND R1.DateFormatted >= GETDATE() - 180) AS "Number of Rides - Last Six Months",
(SELECT COUNT(DISTINCT [DateFormatted]) FROM DBO.Riders_Rides R1 WITH (NOLOCK) WHERE R.FirstName = R1.FirstName AND R.LastName = R1.LastName AND R.Email = R1.Email AND R1.DateFormatted >= GETDATE() - 365) AS "Number of Rides - Last Twelve Months",
DATEDIFF(Day, MIN(R.[DateFormatted]),MAX(R.[DateFormatted])) AS "Days Between First and Last Ride",
DATEDIFF(Day, MIN(R.[DateFormatted]),GETDATE()) AS "Days Since First Ride",
DATEDIFF(Day, MAX(R.[DateFormatted]),GETDATE()) AS "Days Since Last Ride",
AVG(RIDES."Days Between Rides") AS "Average Days Between Rides",
AVG(RIDES."Weeks Between Rides") AS "Average Weeks Between Rides",
CONVERT(FLOAT,COUNT(DISTINCT R.[DateFormatted])) / CONVERT(FLOAT,REPLACE(DATEDIFF(month,MIN(R.[DateFormatted]),GETDATE()),0,1)) AS "Rides per Month",
K.Cluster

FROM DBO.Riders_Rides R WITH (NOLOCK)
LEFT OUTER JOIN DBO.SpinClassCounts S WITH (NOLOCK) ON R.DateFormatted = S.Date
LEFT OUTER JOIN CTE ON R.FirstName = CTE.FirstName AND R.LastName = CTE.LastName AND R.Email = CTE.Email AND CTE.Rw = 1
LEFT OUTER JOIN RIDES ON R.FirstName = RIDES.FirstName AND R.LastName = RIDES.LastName AND R.Email = RIDES.Email
LEFT OUTER JOIN LAST_RIDES ON R.FirstName = LAST_RIDES.FirstName AND R.LastName = LAST_RIDES.LastName AND R.Email = LAST_RIDES.Email AND LAST_RIDES.RW = 1
LEFT OUTER JOIN [dbo].[Alias_Crosswalk] AC WITH (NOLOCK) ON AC.[First Name] = R.FirstName AND AC.[Last Name] = R.LastName AND AC.Email = R.Email
LEFT OUTER JOIN dbo.KMeans_Clusters K WITH (NOLOCK) ON AC.ID = K.[Rider ID]

GROUP BY
AC.ID,
R.[FirstName],
R.[LastName],
R.[Email],
CTE.Location,
LAST_RIDES.[Class Format],
LAST_RIDES.[Location],
LAST_RIDES.[Playlist URL],
LAST_RIDES.[Playlist ID],
K.Cluster

GO



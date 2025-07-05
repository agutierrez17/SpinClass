USE [SpinClass]
GO

/****** Object:  View [dbo].[Riders_Alias]    Script Date: 7/5/2025 10:15:59 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO









ALTER VIEW [dbo].[Riders_Alias] AS

WITH CTE AS (
SELECT DISTINCT
[FirstName],
[LastName],
[Email],
[Location],
COUNT(DISTINCT [DateFormatted]) AS "Number of Rides",
ROW_NUMBER() OVER (PARTITION BY [FirstName],[LastName],[Email] ORDER BY COUNT(DISTINCT [DateFormatted]) DESC) AS Rw
FROM DBO.Riders_Rides_Alias R WITH (NOLOCK)

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
FROM DBO.Riders_Rides_Alias R WITH (NOLOCK)

GROUP BY
[FirstName],
[LastName],
[Email],
[DateFormatted]
)

SELECT DISTINCT
AC.ID AS "Rider ID",
R.[FirstName] AS "First Name",
R.[LastName] AS "Last Name",
R.[Email],
MIN(R.[DateFormatted]) AS "First Ride",
MAX(R.[DateFormatted]) AS "Most Recent Ride",
(SELECT [Class Format] FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Format",
(SELECT Location FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Location",
(SELECT [Playlist URL] FROM DBO.Classes_Playlists WHERE [Class Date] = MAX(R.[DateFormatted])) AS "Most Recent Ride Playlist",
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

FROM DBO.Riders_Rides_Alias R WITH (NOLOCK)
LEFT OUTER JOIN DBO.SpinClassCounts S WITH (NOLOCK) ON R.DateFormatted = S.Date
LEFT OUTER JOIN CTE ON R.FirstName = CTE.FirstName AND R.LastName = CTE.LastName AND R.Email = CTE.Email AND CTE.Rw = 1
LEFT OUTER JOIN RIDES ON R.FirstName = RIDES.FirstName AND R.LastName = RIDES.LastName AND R.Email = RIDES.Email
LEFT OUTER JOIN [dbo].[Alias_Crosswalk] AC WITH (NOLOCK) ON AC.[Alias First Name] = R.FirstName AND AC.[Alias Last Name] = R.LastName
LEFT OUTER JOIN dbo.KMeans_Clusters K WITH (NOLOCK) ON AC.ID = K.[Rider ID]

GROUP BY
AC.ID,
R.[FirstName],
R.[LastName],
R.[Email],
CTE.Location,
K.Cluster

GO



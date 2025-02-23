USE [SpinClass]
GO

/****** Object:  View [dbo].[Riders]    Script Date: 12/5/2024 10:02:25 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO




CREATE VIEW [dbo].[Riders_Alias] AS

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

ALIASES AS (
SELECT
R.[First Name],
R.[Last Name],
R.Email,
B.[First Name] AS "Alias First Name",
B.[Last Name] AS "Alias Last Name"
FROM 
DBO.Riders R WITH (NOLOCK),
DBO.BaseballAliases B WITH (NOLOCK)
)

SELECT DISTINCT
(SELECT TOP 1 [Alias First Name] FROM ALIASES WHERE R.FirstName = ALIASES.[First Name] AND R.LastName = ALIASES.[Last Name] AND R.Email = ALIASES.Email ORDER BY NEWID()) AS "First Name",
(SELECT TOP 1 [Alias Last Name] FROM ALIASES WHERE R.FirstName = ALIASES.[First Name] AND R.LastName = ALIASES.[Last Name] AND R.Email = ALIASES.Email ORDER BY NEWID()) AS "Last Name",
'xxxx@gmail.com' AS "Email",
MIN(R.[DateFormatted]) AS "First Ride",
MAX(R.[DateFormatted]) AS "Most Recent Ride",
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
AVG(RIDES."Weeks Between Rides") AS "Average Weeks Between Rides"

FROM DBO.Riders_Rides R WITH (NOLOCK)
LEFT OUTER JOIN DBO.SpinClassCounts S WITH (NOLOCK) ON R.DateFormatted = S.Date
LEFT OUTER JOIN CTE ON R.FirstName = CTE.FirstName AND R.LastName = CTE.LastName AND R.Email = CTE.Email AND CTE.Rw = 1
LEFT OUTER JOIN RIDES ON R.FirstName = RIDES.FirstName AND R.LastName = RIDES.LastName AND R.Email = RIDES.Email

GROUP BY
R.[FirstName],
R.[LastName],
R.[Email],
CTE.Location

GO



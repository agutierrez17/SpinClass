USE [SpinClass]
GO

/****** Object:  View [dbo].[HubspotUpdate]    Script Date: 12/29/2024 7:52:44 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER VIEW [dbo].[HubspotUpdate] AS

WITH CTE AS (
SELECT TOP 3
[Class Format] + ' - FFC ' + Location AS "Upcoming Ride Location",
[Day of Week] + ', ' + DateFormatted + ' - ' + REPLACE(REPLACE(REPLACE(Time,' AM','am'),' PM','pm'),'-','to') AS "Upcoming Ride Time",
ROW_NUMBER() OVER (PARTITION BY '' ORDER BY [Date],[Time]) AS Rw
FROM DBO.UpcomingRides
ORDER BY
[DATE], [TIME]
)

SELECT 
H.[Hubspot ID],
R.[First Name],
R.[Last Name],
R.[Email],
--CAST(DATEDIFF(s,'1970-01-01 00:00:00',[First Ride])AS BIGINT) AS "First Ride",
--CONVERT(CHAR(20), [First Ride], 127) + '00Z' AS "First Ride",
DATEDIFF_BIG(ms, '1970-01-01 00:00:00', [First Ride]) AS "First Ride",
--CAST(DATEDIFF(s,'1970-01-01 00:00:00',[Most Recent Ride])AS BIGINT) AS "Most Recent Ride",
--CONVERT(CHAR(20), [Most Recent Ride], 127) + '00Z' AS "Most Recent Ride",
DATEDIFF_BIG(ms, '1970-01-01 00:00:00', [Most Recent Ride]) AS "Most Recent Ride",
[Most Recent Ride Format],
[Most Recent Ride Location],
'https://open.spotify.com/embed/playlist/' + REPLACE(R.[Most Recent Ride Playlist],'https://open.spotify.com/playlist/','')  AS "Most Recent Ride Playlist",
[Number of Rides],
PA.[Image URL] AS "Most Recent Playlist Image",
--[Top Location]

(SELECT "Upcoming Ride Location" FROM CTE WHERE Rw = 1) AS "Upcoming Ride Location 1",
(SELECT "Upcoming Ride Time" FROM CTE WHERE Rw = 1) AS "Upcoming Ride Time 1",
(SELECT "Upcoming Ride Location" FROM CTE WHERE Rw = 2) AS "Upcoming Ride Location 2",
(SELECT "Upcoming Ride Time" FROM CTE WHERE Rw = 2) AS "Upcoming Ride Time 2",
(SELECT "Upcoming Ride Location" FROM CTE WHERE Rw = 3) AS "Upcoming Ride Location 3",
(SELECT "Upcoming Ride Time" FROM CTE WHERE Rw = 3) AS "Upcoming Ride Time 3"

FROM [SpinClass].[dbo].[Riders] R WITH (NOLOCK)
INNER JOIN DBO.Hubspot_Spin_Contacts H WITH (NOLOCK) ON R.Email = H.Email AND R.[First Name] = H.[First Name] AND R.[Last Name] = H.[Last Name]
LEFT OUTER JOIN DBO.Playlist_Artwork PA WITH (NOLOCK) ON R.[Most Recent Playlist ID] = PA.[Playlist ID] AND PA.Height = '300'

WHERE
R.EMAIL IS NOT NULL

GO



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
)

SELECT DISTINCT
R.[FirstName] AS "First Name",
R.[LastName] AS "Last Name",
R.[Email],
MIN([DateFormatted]) AS "First Ride",
MAX([DateFormatted]) AS "Most Recent Ride",
COUNT(DISTINCT [DateFormatted]) AS "Number of Rides",
COUNT(DISTINCT R.[Location]) AS "Number of Locations",
CTE.Location AS "Top Location"
FROM DBO.Riders_Rides R WITH (NOLOCK)
LEFT OUTER JOIN DBO.SpinClassCounts S WITH (NOLOCK) ON R.DateFormatted = S.Date
LEFT OUTER JOIN CTE ON R.FirstName = CTE.FirstName AND R.LastName = CTE.LastName AND R.Email = CTE.Email AND CTE.Rw = 1

GROUP BY
R.[FirstName],
R.[LastName],
R.[Email],
CTE.Location

GO
;
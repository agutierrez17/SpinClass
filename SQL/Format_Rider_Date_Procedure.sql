CREATE PROCEDURE [dbo].[Format_Rider_Date] AS

UPDATE DBO.Riders_Rides
SET [DateFormatted] = CONVERT(DATETIME,REPLACE(RIGHT([Date], LEN([Date]) - 5),',','') + ' ' + SUBSTRING([Time],0,CHARINDEX(' - ',[Time])),0)
WHERE
[Date] LIKE '%[A-Z]%'

GO

;
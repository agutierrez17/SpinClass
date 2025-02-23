USE [SpinClass]
GO

/****** Object:  StoredProcedure [dbo].[AliasInsert]    Script Date: 12/29/2024 7:46:34 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[UpcomingRidesDateFormat] AS

DECLARE @DateString VARCHAR(50)
DECLARE @Date DATETIME
DECLARE @Time VARCHAR(50)

DECLARE @UpcomingClassCount INT
DECLARE @Counter INT
DECLARE @PrevIndex INT

SET @UpcomingClassCount = (SELECT COUNT(*) FROM DBO.UpcomingRides U WITH (NOLOCK))
SET @Counter = 1

WHILE (@Counter <= @UpcomingClassCount)
BEGIN

SELECT TOP 1 @Date = [Date], @Time = [Time] FROM DBO.UpcomingRides U WITH (NOLOCK) WHERE U.DateFormatted IS NULL ORDER BY [Date], [Time]

SET @DateString = REPLACE(DATENAME(MM, @Date) + RIGHT(CONVERT(VARCHAR(12), @Date, 107), 9), ' 0',' ')

SET @PrevIndex = SUBSTRING(@DateString,CHARINDEX(',',@DateString) - 1,1)

SET @DateString = REPLACE(@DateString,',', CASE WHEN @PrevIndex = '1' THEN 'st,'WHEN @PrevIndex = '2' THEN 'nd,' WHEN @PrevIndex = '3' THEN 'rd,' ELSE 'th,' END)

PRINT @DateString

UPDATE U
SET U.DateFormatted = @DateString
FROM DBO.UpcomingRides U WITH (NOLOCK)
WHERE
U.Date = @Date
AND
U.Time = @Time

PRINT 'Updated table row #' + STR(@Counter)

SET @Counter = @Counter + 1

END

GO
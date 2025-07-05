
ALTER PROCEDURE [dbo].[KMeans_Archive] AS

---- Archive current rider count for each cluster
INSERT INTO DBO.KMeans_Counts_Historical ([Cluster], [Number of Riders], [Date])
SELECT
[Cluster],
COUNT(DISTINCT [Rider ID]) AS "Number of Riders",
MAX([DateFormatted]) AS "Date"
FROM [SpinClass].[dbo].[KMeans_Clusters]

GROUP BY
[Cluster];


-- Drop previous model run table if exists
IF OBJECT_ID('dbo.[KMeans_Clusters_Previous]', 'U') IS NOT NULL 
  DROP TABLE dbo.[KMeans_Clusters_Previous]; 

----- Select current model run into prior model run table
SELECT
[Rider ID],
[DateFormatted],
[Cluster],
[Component 1],
[Component 2],
[Component 3]
INTO [dbo].[KMeans_Clusters_Previous]
FROM [SpinClass].[dbo].[KMeans_Clusters];

----- Truncate current KMeans table
TRUNCATE TABLE [SpinClass].[dbo].[KMeans_Clusters];


GO



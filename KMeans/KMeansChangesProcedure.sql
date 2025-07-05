
ALTER PROCEDURE [dbo].[KMeans_Changes_Insert] AS

---- Capture instances where riders' clusters have changed
INSERT INTO dbo.KMeans_Clusters_Changes ([Rider ID],[Date],[New Cluster],[Old Cluster])
SELECT
K.[Rider ID],
K.[DateFormatted],
K.[Cluster] AS "New Cluster",
K2.Cluster AS "Old Cluster"
FROM [SpinClass].[dbo].[KMeans_Clusters] K WITH (NOLOCK)
LEFT OUTER JOIN [dbo].[KMeans_Clusters_Previous] K2 WITH (NOLOCK) ON K.[Rider ID] = K2.[Rider ID]

WHERE
K.Cluster <> K2.Cluster;

GO



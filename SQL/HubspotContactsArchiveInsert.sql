USE [SpinClass]
GO

/****** Object:  StoredProcedure [dbo].[AliasInsert]    Script Date: 1/19/2025 5:17:25 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[HubspotContactsArchiveInsert] AS

INSERT INTO DBO.Hubspot_Spin_Contacts_Archive
SELECT
H.[Hubspot ID],
H.[Email],
H.[Last Name],
H.[First Name],
H.[Hubspot Opt Out],
H.[Marketing Email Opt Out],
H.[Create Date],
H.[Last Modified Date],
H.[Emails Delivered],
H.[Emails Opened],
H.[Emails Clicked],
H.[Emails Bounced],
H.[First Send Date],
H.[First Open Date],
H.[First Click Date],
H.[Last Send Date],
H.[Last Open Date],
H.[Last Click Date],
H.[Sends Since Last Engagement]
FROM [SpinClass].[dbo].[Hubspot_Spin_Contacts] H WITH (NOLOCK)
LEFT OUTER JOIN DBO.Hubspot_Spin_Contacts_Archive HA WITH (NOLOCK) ON H.[Hubspot ID] = HA.[Hubspot ID]
WHERE
(H.[Hubspot Opt Out] = 1 OR H.[Marketing Email Opt Out] = 1)
AND
HA.[Hubspot ID] IS NULL

UNION

SELECT
H.[Hubspot ID],
H.[Email],
H.[Last Name],
H.[First Name],
H.[Hubspot Opt Out],
H.[Marketing Email Opt Out],
H.[Create Date],
H.[Last Modified Date],
H.[Emails Delivered],
H.[Emails Opened],
H.[Emails Clicked],
H.[Emails Bounced],
H.[First Send Date],
H.[First Open Date],
H.[First Click Date],
H.[Last Send Date],
H.[Last Open Date],
H.[Last Click Date],
H.[Sends Since Last Engagement]
FROM [SpinClass].[dbo].[Hubspot_Spin_Contacts] H WITH (NOLOCK)
INNER JOIN DBO.Riders R WITH (NOLOCK) ON R.Email = H.Email AND R.[First Name] = H.[First Name] AND R.[Last Name] = H.[Last Name]
LEFT OUTER JOIN DBO.Hubspot_Spin_Contacts_Archive HA WITH (NOLOCK) ON H.[Hubspot ID] = HA.[Hubspot ID]

WHERE
[Most Recent Ride] < GETDATE() - 365.25
AND
HA.[Hubspot ID] IS NULL

GO
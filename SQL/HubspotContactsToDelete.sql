USE [SpinClass]
GO

/****** Object:  View [dbo].[HubspotUpdate]    Script Date: 12/29/2024 10:18:22 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[HubspotContactsToDelete] AS

SELECT
H.[Hubspot ID],
H.Email
FROM DBO.Hubspot_Spin_Contacts H WITH (NOLOCK)
LEFT OUTER JOIN DBO.Riders R WITH (NOLOCK) ON R.Email = H.Email AND R.[First Name] = H.[First Name] AND R.[Last Name] = H.[Last Name]

WHERE
[Hubspot Opt Out] = 'TRUE'
OR 
[Marketing Email Opt Out] = 'TRUE'
OR 
[Most Recent Ride] < GETDATE() - 365.25

GO
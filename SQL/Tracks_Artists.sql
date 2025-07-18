/*
   Friday, November 22, 20242:08:19 PM
   User: 
   Server: localhost
   Database: SpinClass
   Application: 
*/

/* To prevent any potential data loss issues, you should review this script in detail before running it outside the context of the database designer.*/
BEGIN TRANSACTION
SET QUOTED_IDENTIFIER ON
SET ARITHABORT ON
SET NUMERIC_ROUNDABORT OFF
SET CONCAT_NULL_YIELDS_NULL ON
SET ANSI_NULLS ON
SET ANSI_PADDING ON
SET ANSI_WARNINGS ON
COMMIT
BEGIN TRANSACTION
GO
CREATE TABLE dbo.Tracks_Artists
	(
	[Track ID] nvarchar(255) NOT NULL,
	[Artist ID] nvarchar(255) NOT NULL
	)  ON [PRIMARY]
GO
ALTER TABLE dbo.Tracks_Artists SET (LOCK_ESCALATION = TABLE)
GO
COMMIT

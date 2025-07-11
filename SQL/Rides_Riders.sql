/*
   Wednesday, November 13, 20243:47:35 PM
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
CREATE TABLE dbo.Riders_Rides
	(
	Date varchar(50) NOT NULL,
	Time varchar(50) NOT NULL,
	[Class Format] varchar(50) NOT NULL,
	Location varchar(50) NOT NULL,
	FirstName varchar(50) NOT NULL,
	LastName varchar(50) NOT NULL,
	Email varchar(50) NULL
	)  ON [PRIMARY]
GO
ALTER TABLE dbo.Riders_Rides SET (LOCK_ESCALATION = TABLE)
GO
COMMIT

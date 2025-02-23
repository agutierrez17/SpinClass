USE [SpinClass]
GO

/****** Object:  Table [dbo].[Hubspot_Lists]    Script Date: 12/17/2024 9:03:19 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Hubspot_Lists]') AND type in (N'U'))
DROP TABLE [dbo].[Hubspot_Lists]
GO

/****** Object:  Table [dbo].[Hubspot_Lists]    Script Date: 12/17/2024 9:03:19 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Hubspot_Lists](
	[Hubspot ID] [nvarchar](255) NULL,
	[Date Added] [datetime] NULL,
	[List ID] [int] NULL,
	[List Name] [nvarchar](50) NULL
) ON [PRIMARY]
GO



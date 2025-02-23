USE [SpinClass]
GO

/****** Object:  View [dbo].[ExcelTracksView]    Script Date: 1/5/2025 4:30:45 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



CREATE TABLE [dbo].[SongLibrary](
	[External URL] [nvarchar](255) NULL,
	[Category] [varchar](255) NULL,
	[Builder] [varchar](1) NULL,
	[Ride Code] [varchar](1) NULL,
	[Position] [varchar](1) NULL,
	[Track Name] [nvarchar](255) NULL,
	[Artists] [nvarchar](MAX) NULL,
	[BPM] [float] NULL,
	[Used RPM] [float] NULL,
	[Duration] [nvarchar](255) NULL,
	[Genre] [varchar](255) NULL,
	[Notes] [varchar](MAX) NULL
) ON [PRIMARY]

GO



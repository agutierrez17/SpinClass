USE [SpinClass]
GO

/****** Object:  Table [dbo].[Riders_Rides]    Script Date: 12/29/2024 4:23:31 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[UpcomingRides](
	[Date] [datetime] NULL,
	[Day of Week] [varchar](50) NULL,
	[Time] [varchar](50) NOT NULL,
	[Class Format] [varchar](50) NOT NULL,
	[Location] [varchar](50) NOT NULL

) ON [PRIMARY]
GO



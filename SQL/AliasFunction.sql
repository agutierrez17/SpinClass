SELECT 
R.[First Name],
R.[Last Name],
(SELECT TOP 1 B.[First Name] FROM DBO.BaseballAliases B ORDER BY NEWID()),
(SELECT TOP 1 B.[Last Name] FROM DBO.BaseballAliases B ORDER BY NEWID())
FROM 
DBO.Riders R WITH (NOLOCK)


SELECT
R.[First Name],
R.[Last Name],
B.[First Name],
B.[Last Name]
FROM 
DBO.Riders R WITH (NOLOCK),
DBO.BaseballAliases B WITH (NOLOCK)

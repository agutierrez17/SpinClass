
CREATE PROCEDURE DBO.AliasInsert AS

DECLARE @IdentityStart INT
SET @IdentityStart = (SELECT CASE WHEN (SELECT COUNT(*) FROM DBO.Alias_Crosswalk) = 0 THEN 0 ELSE (SELECT COUNT(*) - 1 FROM DBO.Alias_Crosswalk) END)

SELECT
@IdentityStart

DECLARE @AliasFirstName VARCHAR(50)
DECLARE @AliasLastName VARCHAR(50)
DECLARE @RiderCount INT
DECLARE @Counter INT

SET @RiderCount = (SELECT COUNT(*) FROM DBO.Riders R WITH (NOLOCK) LEFT OUTER JOIN DBO.Alias_Crosswalk AC WITH (NOLOCK) ON AC.[First Name] = R.[First Name] AND AC.[Last Name] = R.[Last Name] AND AC.Email = R.Email WHERE AC.[First Name] IS NULL)
SET @Counter = 1

WHILE (@Counter < @RiderCount)
BEGIN
	BEGIN TRANSACTION
		PRINT 'Starting insert loop'
		PRINT @Counter

		SELECT @AliasFirstName = [First Name] FROM DBO.BaseballAliases ORDER BY NEWID() OFFSET 1 ROWS
		PRINT @AliasFirstName
		SELECT @AliasLastName = [Last Name] FROM DBO.BaseballAliases ORDER BY NEWID() OFFSET 1 ROWS
		PRINT @AliasLastName

		PRINT 'Inserting...'
		INSERT INTO DBO.Alias_Crosswalk ([First Name], [Last Name], Email, [Alias First Name], [Alias Last Name])
		SELECT TOP 1
		R.[First Name],
		R.[Last Name],
		R.Email,
		@AliasFirstName,
		@AliasLastName
		FROM DBO.Riders R WITH (NOLOCK)
		LEFT OUTER JOIN DBO.Alias_Crosswalk AC WITH (NOLOCK) ON AC.[First Name] = R.[First Name] AND AC.[Last Name] = R.[Last Name] AND AC.Email = R.Email

		WHERE
		AC.[First Name] IS NULL

		ORDER BY
		[First Ride],
		[Last Name],
		[First Name]

		IF (ISNULL((SELECT COUNT(*) FROM DBO.Alias_Crosswalk WHERE [Alias First Name] = @AliasFirstName AND [Alias Last Name] = @AliasLastName),0)) > 1
			BEGIN
				ROLLBACK TRANSACTION 
				PRINT 'Alias already used in table'
			END
		ELSE
			SET @Counter = @Counter + 1
			COMMIT TRANSACTION
			PRINT 'Row inserted successfully'
END

GO
	
 

		


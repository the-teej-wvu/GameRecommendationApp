



-- Create a proc to lsit the games to a specific developer. 
-- CREATE PROCEDURE listGames
--     @DeveloperID INT
-- AS
-- BEGIN
--     SELECT
--         GameID,
--         Title,
--         ReleaseYr,
--         Publisher
--     FROM Game
--     WHERE DeveloperID = @DeveloperID;
-- END;
-- GO


-- -- Run seperately to run and test, change @DeveloperID as wanted.  
-- EXEC listGames @DeveloperID = 11;



-- Create a proc named countGames that counts all the games for a specific platform. 
CREATE PROCEDURE countGames
    @PlatformID INT
AS
BEGIN
    SELECT
        P.PlatName,
        COUNT(DISTINCT GP.GameID) AS TotalGames
    FROM Platform P
    LEFT JOIN GamePlatform GP
        ON P.PlatformID = GP.PlatformID
    WHERE P.PlatformID = @PlatformID
    GROUP BY P.PlatName;
END;
GO


-- Test it, and run it seperately @PlatformID 21 is SNES. 
EXEC countGames @PlatformID = 21;


















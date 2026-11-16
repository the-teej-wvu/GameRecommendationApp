

-- Initial Testing Data for the Game Database

-- SELECT COUNT(*) AS Games      FROM Game;
-- SELECT COUNT(*) AS Developers FROM Developer;
-- SELECT COUNT(*) AS Platforms  FROM Platform;
-- SELECT COUNT(*) AS Genres     FROM Genre;
-- SELECT COUNT(*) AS GamePlats  FROM GamePlatform;

-- SELECT TOP 10 g.Title, g.ReleaseYr, d.DeveloperName
-- FROM Game g
-- JOIN Developer d ON d.DeveloperID = g.DeveloperID
-- ORDER BY g.Title;


-- Shows all 5000 Games Available
-- SELECT * FROM Game;


-- Change the quote text to the system you want to use for testing.  The below query will show all games that are available on the that platform.
SELECT 
    Game.GameID,
    Game.Title,
    Game.ReleaseYr,
    Game.Publisher,
    Developer.DeveloperName,
    Platform.PlatName
FROM Game
INNER JOIN Developer
    ON Game.DeveloperID = Developer.DeveloperID
INNER JOIN GamePlatform
    ON Game.GameID = GamePlatform.GameID
INNER JOIN Platform
    ON GamePlatform.PlatformID = Platform.PlatformID
WHERE Platform.PlatName = 'PC'
ORDER BY Game.Title;
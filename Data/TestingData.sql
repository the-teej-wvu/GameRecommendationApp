SELECT COUNT(*) AS Games      FROM Game;
SELECT COUNT(*) AS Developers FROM Developer;
SELECT COUNT(*) AS Platforms  FROM Platform;
SELECT COUNT(*) AS Genres     FROM Genre;
SELECT COUNT(*) AS GamePlats  FROM GamePlatform;

SELECT TOP 10 g.Title, g.ReleaseYr, d.DeveloperName
FROM Game g
JOIN Developer d ON d.DeveloperID = g.DeveloperID
ORDER BY g.Title;



-- SELECT * FROM Game;
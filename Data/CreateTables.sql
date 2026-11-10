-- SELECT
--     member.name AS UserName,
--     role.name AS DatabaseRole
-- FROM sys.database_role_members AS rm
-- JOIN sys.database_principals AS role
--     ON role.principal_id = rm.role_principal_id
-- JOIN sys.database_principals AS member
--     ON member.principal_id = rm.member_principal_id
-- WHERE member.name IN ('TJColon', 'NandaSurendra');

if object_id('Recommendation') is not null
    drop table Recommendation;
if object_id('UserGame') is not null
    drop table UserGame;
if object_id('GameGenre') is not null 
    drop table GameGenre;
if object_id('GamePlatform') is not null 
    drop table GamePlatform;
if object_id('Game') is not null 
    drop table Game;
if object_id('Genre') is not null 
    drop table Genre;
if object_id('Platform') is not null 
    drop table Platform;
if object_id('Developer') is not null 
    drop table Developer;
if object_id('Users') is not null 
    drop table Users;


IF OBJECT_ID('Recommendation') IS NOT NULL DROP TABLE Recommendation;
IF OBJECT_ID('UserGame')       IS NOT NULL DROP TABLE UserGame;
IF OBJECT_ID('GameGenre')      IS NOT NULL DROP TABLE GameGenre;
IF OBJECT_ID('GamePlatform')   IS NOT NULL DROP TABLE GamePlatform;
IF OBJECT_ID('Game')           IS NOT NULL DROP TABLE Game;
IF OBJECT_ID('Genre')          IS NOT NULL DROP TABLE Genre;
IF OBJECT_ID('Platform')       IS NOT NULL DROP TABLE Platform;
IF OBJECT_ID('Developer')      IS NOT NULL DROP TABLE Developer;
IF OBJECT_ID('Users')          IS NOT NULL DROP TABLE Users;
GO

CREATE TABLE [Users] (
    UserID      INT           NOT NULL PRIMARY KEY,
    Username    VARCHAR(50)   NOT NULL,
    Email       VARCHAR(100)  NOT NULL,
    PW          VARCHAR(255)  NOT NULL,
    UserRole    VARCHAR(20)   NOT NULL,
    DateJoined  DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT UQ_Users_Username UNIQUE (Username),
    CONSTRAINT UQ_Users_Email    UNIQUE (Email)
);
GO

CREATE TABLE Developer (
    DeveloperID    INT          NOT NULL PRIMARY KEY,
    DeveloperName  VARCHAR(100) NOT NULL,
    CONSTRAINT UQ_Developer_DeveloperName UNIQUE (DeveloperName)
);
GO

CREATE TABLE Game (
    GameID       INT          NOT NULL PRIMARY KEY,
    Title        VARCHAR(150) NOT NULL,
    ReleaseYr    INT,
    Publisher    VARCHAR(100),
    DeveloperID  INT          NOT NULL,
    CONSTRAINT FK_Game_Developer
        FOREIGN KEY (DeveloperID) REFERENCES Developer(DeveloperID)
);
GO

CREATE TABLE Platform (
    PlatformID       INT          NOT NULL PRIMARY KEY,
    PlatName         VARCHAR(50)  NOT NULL,
    PlatManufacture  VARCHAR(100)
);
GO

CREATE TABLE Genre (
    GenreID    INT         NOT NULL PRIMARY KEY,
    GenreName  VARCHAR(50) NOT NULL,
    CONSTRAINT UQ_Genre_GenreName UNIQUE (GenreName)
);
GO

CREATE TABLE GamePlatform (
    PlatformID  INT NOT NULL,
    GameID      INT NOT NULL,
    NumGames    INT,
    CONSTRAINT PK_GamePlatform PRIMARY KEY (PlatformID, GameID),
    CONSTRAINT FK_GamePlatform_Platform
        FOREIGN KEY (PlatformID) REFERENCES Platform(PlatformID),
    CONSTRAINT FK_GamePlatform_Game
        FOREIGN KEY (GameID) REFERENCES Game(GameID)
);
GO

CREATE TABLE GameGenre (
    GameID   INT NOT NULL,
    GenreID  INT NOT NULL,
    CONSTRAINT PK_GameGenre PRIMARY KEY (GameID, GenreID),
    CONSTRAINT FK_GameGenre_Game
        FOREIGN KEY (GameID) REFERENCES Game(GameID),
    CONSTRAINT FK_GameGenre_Genre
        FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
);
GO

CREATE TABLE UserGame (
    UserID       INT         NOT NULL,
    GameID       INT         NOT NULL,
    Status       VARCHAR(20) NOT NULL,
    HoursPlayed  INT         NOT NULL DEFAULT 0,
    DateAdded    DATETIME2   NOT NULL DEFAULT SYSDATETIME(),
    LastPlayed   DATE,
    Rating       INT,
    CONSTRAINT PK_UserGame PRIMARY KEY (UserID, GameID),
    CONSTRAINT FK_UserGame_User
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT FK_UserGame_Game
        FOREIGN KEY (GameID) REFERENCES Game(GameID)
);
GO  

CREATE TABLE Recommendation (
    RecommendationID      INT          NOT NULL PRIMARY KEY,
    UserID                INT          NOT NULL,
    GameID                INT          NOT NULL,
    Score                 INT,
    CommunityScore        INT,
    Reason                VARCHAR(255),
    GeneratedAt           DATETIME2    NOT NULL DEFAULT SYSDATETIME(),
    AcceptRecommendation  BIT          NOT NULL DEFAULT 0,
    CONSTRAINT FK_Recommendation_Users
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
    CONSTRAINT FK_Recommendation_Game
        FOREIGN KEY (GameID) REFERENCES Game(GameID)
);
GO
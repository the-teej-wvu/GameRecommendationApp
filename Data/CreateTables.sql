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


CREATE TABLE Users (
    UserID      INT PRIMARY KEY,
    Username    VARCHAR(50)  NOT NULL UNIQUE,
    Email       VARCHAR(100) NOT NULL UNIQUE,
    PW          VARCHAR(255) NOT NULL,
    UserRole        VARCHAR(20)  NOT NULL,
    DateJoined  TIMESTAMP    NOT NULL
    CONSTRAINT UQ_Users_Username UNIQUE (Username),
    CONSTRAINT UQ_Users_Email UNIQUE (Email)
);

go 

CREATE TABLE Developer (
    DeveloperID   INT PRIMARY KEY,
    DeveloperName VARCHAR(100) NOT NULL
);

go 

CREATE TABLE Game (
    GameID       INT PRIMARY KEY,
    Title        VARCHAR(150) NOT NULL,
    ReleaseYr    INT,
    Publisher    VARCHAR(100),
    DeveloperID  INT NOT NULL,
    FOREIGN KEY (DeveloperID) REFERENCES Developer(DeveloperID)
);

go 

CREATE TABLE Platform (
    PlatformID       INT PRIMARY KEY,
    PlatName         VARCHAR(50) NOT NULL,
    PlatManufacture  VARCHAR(100)
);

go 

CREATE TABLE Genre (
    GenreID    INT PRIMARY KEY,
    GenreName  VARCHAR(50) NOT NULL UNIQUE
);

go 

CREATE TABLE GamePlatform (
    PlatformID  INT NOT NULL,
    GameID      INT NOT NULL,
    NumGames    INT,
    PRIMARY KEY (PlatformID, GameID),
    FOREIGN KEY (PlatformID) REFERENCES Platform(PlatformID),
    FOREIGN KEY (GameID)     REFERENCES Game(GameID)
);

go

CREATE TABLE GameGenre (
    GameID   INT NOT NULL,
    GenreID  INT NOT NULL,
    PRIMARY KEY (GameID, GenreID),
    FOREIGN KEY (GameID)  REFERENCES Game(GameID),
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
);

go

CREATE TABLE UserGame (
    UserID       INT NOT NULL,
    GameID       INT NOT NULL,
    OnlineStatus       VARCHAR(20) NOT NULL,
    HoursPlayed  INT DEFAULT 0,
    DateAdded    TIMESTAMP NOT NULL,
    LastPlayed   DATE,
    Rating       INT CHECK (Rating BETWEEN 1 AND 10),
    PRIMARY KEY (UserID, GameID),
    CONSTRAINT UQ_UserGame_UserID_GameID UNIQUE (UserID, GameID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (GameID) REFERENCES Game(GameID)
);

go

CREATE TABLE Recommendation (
    RecommendationID  INT PRIMARY KEY,
    UserID            INT NOT NULL,
    GameID            INT NOT NULL,
    Score             INT,
    CommunityScore    INT,
    Reason            VARCHAR(255),
    GeneratedAt       TIMESTAMP NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (GameID) REFERENCES Game(GameID)
);
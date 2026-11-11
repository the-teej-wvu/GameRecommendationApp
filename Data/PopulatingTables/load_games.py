"""
load_games.py

Reads the Kaggle "Video Game Sales with Ratings" CSV and writes populate.sql,
one SQL Server script that:
  1. DROPS all 9 tables (if they exist), so reruns never conflict
  2. CREATEs all 9 tables
  3. INSERTs the games, developers, platforms, genres, and links
  4. Prints a row count per table at the end

Usage:   python load_games.py [number_of_games]      (default 5000)

Kaggle's "Publisher" column is used as the Developer.
"""
import os
import sys
import zipfile
import subprocess
import pandas as pd

TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
DB_NAME = None        # e.g. "GameTracker" to put a USE statement at the top of the script

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = "rush4ratio/video-game-sales-with-ratings"
CSV = os.path.join(BASE, "Video_Games_Sales_as_at_22_Dec_2016.csv")
ZIP = os.path.join(BASE, "video-game-sales-with-ratings.zip")
OUT = os.path.join(BASE, "populate.sql")


# ---------------------------------------------------------------- get the CSV
def get_csv():
    if os.path.exists(CSV):
        return
    if not os.path.exists(ZIP):
        print("CSV not found. Trying the Kaggle command line...")
        try:
            subprocess.run(["kaggle", "datasets", "download", "-d", DATASET, "-p", BASE],
                           check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            sys.exit(
                "\nCould not download automatically. Do this instead:\n"
                "  1. Log in at kaggle.com\n"
                "  2. Open kaggle.com/datasets/rush4ratio/video-game-sales-with-ratings\n"
                "  3. Click Download and unzip it\n"
                "  4. Put Video_Games_Sales_as_at_22_Dec_2016.csv next to this script and rerun.\n")
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(BASE)
    if not os.path.exists(CSV):
        sys.exit("Unzipped, but the CSV was not found. Check the file name inside the zip.")


get_csv()

# ------------------------------------------------------------ load and clean
df = pd.read_csv(CSV)

# Kaggle "Publisher" becomes your Developer
df = df.dropna(subset=["Name", "Platform", "Genre", "Publisher", "Global_Sales"])
df["Publisher"] = df["Publisher"].str.strip()
df = df[df["Publisher"].str.lower() != "unknown"]
df["Developer"] = df["Publisher"]

for c in ["Name", "Platform", "Genre"]:
    df[c] = df[c].str.strip()


def canon(s):
    """One spelling per case-insensitive value (SQL Server UNIQUE is case-insensitive)."""
    first = {}
    return s.map(lambda v: first.setdefault(v.lower(), v))


for c in ["Platform", "Genre", "Developer"]:
    df[c] = canon(df[c])

# ----------------------------------------------------- keep the top N games
available = df["Name"].nunique()
if TARGET > available:
    print(f"Only {available} games have the data needed; loading all of them.")
top = df.groupby("Name")["Global_Sales"].sum().nlargest(TARGET).index
df = df[df["Name"].isin(top)]

# ----------------------------------------------------------- one row per game
games = (df.groupby("Name")
           .agg(Year=("Year_of_Release", "min"),
                Publisher=("Developer", "first"),   # also stored as text in Game.Publisher
                Developer=("Developer", "first"))
           .reset_index())
games["GameID"] = range(1, len(games) + 1)
game_id = dict(zip(games["Name"], games["GameID"]))

dev_id = {n: i for i, n in enumerate(sorted(games["Developer"].unique()), 1)}
plat_id = {n: i for i, n in enumerate(sorted(df["Platform"].unique()), 1)}
genre_id = {n: i for i, n in enumerate(sorted(df["Genre"].unique()), 1)}

MAKER = {"Wii": "Nintendo", "NES": "Nintendo", "GB": "Nintendo", "DS": "Nintendo",
         "SNES": "Nintendo", "GBA": "Nintendo", "3DS": "Nintendo", "N64": "Nintendo",
         "GC": "Nintendo", "WiiU": "Nintendo",
         "PS": "Sony", "PS2": "Sony", "PS3": "Sony", "PS4": "Sony", "PSP": "Sony", "PSV": "Sony",
         "X360": "Microsoft", "XB": "Microsoft", "XOne": "Microsoft",
         "PC": "Various", "2600": "Atari",
         "GEN": "Sega", "DC": "Sega", "SAT": "Sega", "SCD": "Sega", "GG": "Sega"}

# ------------------------------------------------------------------ SQL parts
DROP_AND_CREATE = """\
-- ============================================================
-- 1. DROP existing tables (children first, so no FK conflicts)
-- ============================================================
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

-- ============================================================
-- 2. CREATE tables
-- ============================================================
CREATE TABLE Users (
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
    OnlineStatus VARCHAR(20) NOT NULL,
    HoursPlayed  INT         NOT NULL DEFAULT 0,
    DateAdded    DATETIME2   NOT NULL DEFAULT SYSDATETIME(),
    LastPlayed   DATE,
    Rating       INT,
    CONSTRAINT PK_UserGame PRIMARY KEY (UserID, GameID),
    CONSTRAINT CK_UserGame_Rating CHECK (Rating BETWEEN 1 AND 10),
    CONSTRAINT FK_UserGame_Users
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

"""

VERIFY = """
-- ============================================================
-- 4. Row counts
-- ============================================================
SELECT 'Developer'    AS TableName, COUNT(*) AS NumRows FROM Developer
UNION ALL SELECT 'Platform',     COUNT(*) FROM Platform
UNION ALL SELECT 'Genre',        COUNT(*) FROM Genre
UNION ALL SELECT 'Game',         COUNT(*) FROM Game
UNION ALL SELECT 'GamePlatform', COUNT(*) FROM GamePlatform
UNION ALL SELECT 'GameGenre',    COUNT(*) FROM GameGenre;
GO
"""


def q(v, n=None):
    """Turn a Python value into a SQL string literal (or NULL)."""
    if v is None or pd.isna(v):
        return "NULL"
    return "'" + str(v)[:n].replace("'", "''") + "'"


def emit(f, table, cols, rows, chunk=500):
    """Write INSERTs in batches (SQL Server allows at most 1000 rows per VALUES list)."""
    for i in range(0, len(rows), chunk):
        f.write(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n")
        f.write(",\n".join("(" + ", ".join(r) + ")" for r in rows[i:i + chunk]))
        f.write(";\nGO\n\n")


# ------------------------------------------------------------- write the file
with open(OUT, "w", encoding="utf-8-sig") as f:
    f.write("SET NOCOUNT ON;\nGO\n\n")
    if DB_NAME:
        f.write(f"USE [{DB_NAME}];\nGO\n\n")

    f.write(DROP_AND_CREATE)

    f.write("-- ============================================================\n"
            "-- 3. INSERT data\n"
            "-- ============================================================\n")

    emit(f, "Developer", ["DeveloperID", "DeveloperName"],
         [[str(i), q(n, 100)] for n, i in dev_id.items()])

    emit(f, "Platform", ["PlatformID", "PlatName", "PlatManufacture"],
         [[str(i), q(n, 50), q(MAKER.get(n), 100)] for n, i in plat_id.items()])

    emit(f, "Genre", ["GenreID", "GenreName"],
         [[str(i), q(n, 50)] for n, i in genre_id.items()])

    emit(f, "Game", ["GameID", "Title", "ReleaseYr", "Publisher", "DeveloperID"],
         [[str(r.GameID), q(r.Name, 150),
           "NULL" if pd.isna(r.Year) else str(int(r.Year)),
           q(r.Publisher, 100), str(dev_id[r.Developer])]
          for r in games.itertuples()])

    gp = df[["Platform", "Name"]].drop_duplicates()
    emit(f, "GamePlatform", ["PlatformID", "GameID"],
         [[str(plat_id[p]), str(game_id[n])] for p, n in zip(gp.Platform, gp.Name)])

    gg = df[["Name", "Genre"]].drop_duplicates()
    emit(f, "GameGenre", ["GameID", "GenreID"],
         [[str(game_id[n]), str(genre_id[g])] for n, g in zip(gg.Name, gg.Genre)])

    # NumGames = how many games each platform has
    f.write("UPDATE gp\n"
            "SET NumGames = (SELECT COUNT(*) FROM GamePlatform x WHERE x.PlatformID = gp.PlatformID)\n"
            "FROM GamePlatform gp;\nGO\n")

    f.write(VERIFY)

print(f"Wrote {OUT}")
print(f"  {len(games)} games, {len(dev_id)} developers, "
      f"{len(plat_id)} platforms, {len(genre_id)} genres, "
      f"{len(gp)} game-platform links, {len(gg)} game-genre links")
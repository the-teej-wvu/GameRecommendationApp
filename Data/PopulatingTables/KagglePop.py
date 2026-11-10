import os
import sys
import zipfile
import subprocess
import pandas as pd

DATASET = "rush4ratio/video-game-sales-with-ratings"
CSV = "Video_Games_Sales_as_at_22_Dec_2016.csv"
ZIP = "video-game-sales-with-ratings.zip"
TARGET = 300          # number of games to keep

# ---------- Get the CSV ----------
def get_csv():
    if os.path.exists(CSV):
        return
    if not os.path.exists(ZIP):
        print("CSV not found. Trying the Kaggle command line...")
        try:
            subprocess.run(["kaggle", "datasets", "download", "-d", DATASET], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            sys.exit(
                "\nCould not download automatically. Do this instead:\n"
                "  1. Log in at kaggle.com\n"
                "  2. Open kaggle.com/datasets/rush4ratio/video-game-sales-with-ratings\n"
                "  3. Click Download and unzip it\n"
                f"  4. Put {CSV} in this folder and rerun.\n")
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(".")
    if not os.path.exists(CSV):
        sys.exit(f"Unzipped, but {CSV} was not found. Check the file name in the zip.")

get_csv()

# ---------- Load and clean ----------
df = pd.read_csv(CSV)

# Kaggle "Publisher" becomes your Developer
df = df.dropna(subset=["Name", "Platform", "Genre", "Publisher", "Global_Sales"])
df["Publisher"] = df["Publisher"].str.strip()
df = df[df["Publisher"].str.lower() != "unknown"]   # drop placeholder values
df["Developer"] = df["Publisher"]

for c in ["Name", "Platform", "Genre"]:
    df[c] = df[c].str.strip()

def canon(s):   # one spelling per case-insensitive value (SQL Server UNIQUE is case-insensitive)
    first = {}
    return s.map(lambda v: first.setdefault(v.lower(), v))

for c in ["Platform", "Genre", "Developer"]:
    df[c] = canon(df[c])

# ---------- Keep the best-selling games ----------
top = df.groupby("Name")["Global_Sales"].sum().nlargest(TARGET).index
df = df[df["Name"].isin(top)]

# ---------- One row per game ----------
games = (df.groupby("Name")
           .agg(Year=("Year_of_Release", "min"),
                Publisher=("Developer", "first"),     # same value stored as text in Game.Publisher
                Developer=("Developer", "first"))
           .reset_index())
games["GameID"] = range(1, len(games) + 1)
game_id = dict(zip(games["Name"], games["GameID"]))

dev_id   = {n: i for i, n in enumerate(sorted(games["Developer"].unique()), 1)}
plat_id  = {n: i for i, n in enumerate(sorted(df["Platform"].unique()), 1)}
genre_id = {n: i for i, n in enumerate(sorted(df["Genre"].unique()), 1)}

MAKER = {"Wii": "Nintendo", "NES": "Nintendo", "GB": "Nintendo", "DS": "Nintendo",
         "SNES": "Nintendo", "GBA": "Nintendo", "3DS": "Nintendo", "N64": "Nintendo",
         "GC": "Nintendo", "WiiU": "Nintendo",
         "PS": "Sony", "PS2": "Sony", "PS3": "Sony", "PS4": "Sony", "PSP": "Sony", "PSV": "Sony",
         "X360": "Microsoft", "XB": "Microsoft", "XOne": "Microsoft",
         "PC": "Various", "2600": "Atari",
         "GEN": "Sega", "DC": "Sega", "SAT": "Sega", "SCD": "Sega", "GG": "Sega"}

# ---------- SQL helpers ----------
def q(v, n=None):
    if v is None or pd.isna(v):
        return "NULL"
    return "'" + str(v)[:n].replace("'", "''") + "'"

def emit(f, table, cols, rows, chunk=500):   # SQL Server allows max 1000 rows per VALUES
    for i in range(0, len(rows), chunk):
        f.write(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n")
        f.write(",\n".join("(" + ", ".join(r) + ")" for r in rows[i:i + chunk]))
        f.write(";\nGO\n\n")

# ---------- Write populate.sql ----------
with open("populate.sql", "w", encoding="utf-8-sig") as f:
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

    f.write("UPDATE gp SET NumGames = (SELECT COUNT(*) FROM GamePlatform x "
            "WHERE x.PlatformID = gp.PlatformID)\nFROM GamePlatform gp;\nGO\n")

print(f"{len(games)} games, {len(dev_id)} developers, "
      f"{len(plat_id)} platforms, {len(genre_id)} genres")
print("Wrote populate.sql")
# GameRecommendationApp
MIST 353 Group Project

CreateTables.sql is mostly abandoned now, it's now co-joined with load_games.py; Meaning that all the create tables that were in CreateTables.sql are now just ran under load_games.py, this was done to add more than 300 games more effectively withought running into drop table conflicts. 

The database should be populated now for everything with 5000 games with varying information on each including developer and so on so forth. 

Still need users added into database.
Also, Pandas may need to be installed on your machine to run load_games if it hasn't been already. However, you shouldn't have to since load_games.py just creates populate.sql which can be ran as long as your connected to the sql server. All the games are already in the SQL server so unless we want to add more games that are not already in the database this should be a non issue. 

## Importing to Postgres Database

First step: create the tabels by importing the newest
version of the schema (here: version 2)

  psql infovis_meetup < 2.sql 

Second step: use python script to read json and 
write to postgres:

  python import_to_postgres 

Third step: check if all data was imported:
compare to counts of ids created by jq in ../10-data/:


  $ wc -l ../10-data/id_venue.txt
  2422 ../10-data/id_venue.txt
  $ echo "SELECT count(*) from venues;" |  psql infovis_meetup
   count 
  -------
    2422
  (1 row)




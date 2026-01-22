# SWAPI → MySQL (Airflow + Docker) — Tiny Demo

A minimal, batteries-included demo that:
- Runs Apache Airflow in a single container (`airflow standalone`)
- Spins up MySQL
- Every hour for the next **10 hours**, loads a small slice of Star Wars **people** from SWAPI into MySQL.

## Prereqs
- Docker + Docker Compose

## Quickstart
```bash
# 1) From the project folder:
docker compose build --no-cache --pull
docker compose up -d

# 2) Airflow UI (after ~30s): http://localhost:8080
#    Airflow 'standalone' prints a temporary admin user/password in logs:
#    Run in BASH
docker logs swapi-airflow | grep "username\|password" -n

# 3) Trigger now (optional): in Airflow UI, turn the DAG 'On' if it's not already.
#    The DAG is scheduled hourly from the current hour for 10 hours.
```

## MySQL access
- Host: `localhost`  Port: `3306`  User: `root`  Password: `example`  DB: `swapi`
- Table: `people`


## Running SQL In the Service Container
```Bash
docker compose exec mysql mysql -uroot -pexample swapi
```
```sql
SELECT * FROM people LIMIT 10;
SELECT COUNT(*) FROM people;
```

# Update User password
```bash
docker compose exec airflow airflow users reset-password `
  --username admin `
  --password "Ready4go!"
```


## Notes
- The DAG computes `start_date` and `end_date` at parse time:
  it schedules **@hourly** runs from *now* until *now + 10 hours* and then stops.
- To change the window, edit `dags/swapi_to_mysql.py` (`start`, `end`).

## Tear down
```bash
docker compose down -v
```

## Docker Commands
```bash
#List all docker processes
docker ps 

# restart all containers
docker restart $(docker ps -q)

# Restart everything in the compose project
docker compose restart

# Stop & remove containers, networks, and named volumes for this project
docker compose down -v

# Also remove images built/pulled by this compose project
docker compose down -v --rmi all

# Restart one service (e.g., mysql)
docker compose restart mysql

# If you changed the image or env, recreate the service
docker compose up -d --force-recreate mysql

# see current users
docker compose exec airflow airflow users list


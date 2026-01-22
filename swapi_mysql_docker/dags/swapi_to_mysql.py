from __future__ import annotations
import json
import math
from datetime import datetime, timedelta, timezone
import requests
import pymysql
from airflow import DAG
from airflow.operators.python import PythonOperator

DB_CONFIG = {
    "host": "mysql",
    "user": "root",
    "password": "example",
    "database": "swapi",
    "port": 3306,
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
}

def upsert_people():
    # Connect to MySQL
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """CREATE TABLE IF NOT EXISTS people (
                    id INT PRIMARY KEY,
                    name VARCHAR(255),
                    height VARCHAR(32),
                    mass VARCHAR(32),
                    hair_color VARCHAR(64),
                    skin_color VARCHAR(64),
                    eye_color VARCHAR(64),
                    birth_year VARCHAR(32),
                    gender VARCHAR(32),
                    created DATETIME,
                    edited DATETIME
                )"""
            )

            # Simple: fetch first 2 pages to keep this tiny
            people = []
            url = "https://swapi.dev/api/people/"
            pages = 2
            for page in range(1, pages + 1):
                r = requests.get(url, params={"page": page}, timeout=30)
                r.raise_for_status()
                data = r.json()
                people.extend(data.get("results", []))

            # Insert/replace into MySQL
            for person in people:
                # Extract numeric id from URL like https://swapi.dev/api/people/1/
                url_field = person.get("url", "")
                try:
                    pid = int([seg for seg in url_field.strip("/").split("/") if seg.isdigit()][-1])
                except Exception:
                    continue

                created = person.get("created")
                edited = person.get("edited")
                cur.execute(
                    """REPLACE INTO people
                    (id, name, height, mass, hair_color, skin_color, eye_color, birth_year, gender, created, edited)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        pid,
                        person.get("name"),
                        person.get("height"),
                        person.get("mass"),
                        person.get("hair_color"),
                        person.get("skin_color"),
                        person.get("eye_color"),
                        person.get("birth_year"),
                        person.get("gender"),
                        datetime.fromisoformat(created.replace("Z","+00:00")) if created else None,
                        datetime.fromisoformat(edited.replace("Z","+00:00")) if edited else None,
                    )
                )
    finally:
        conn.close()

# Schedule: hourly for the next 10 hours from DAG parse time
tz = timezone.utc
start = datetime.now(tz=tz).replace(minute=0, second=0, microsecond=0)
end = start + timedelta(hours=10)

with DAG(
    dag_id="swapi_to_mysql_hourly_10x",
    description="Pulls Star Wars people from SWAPI into MySQL, hourly for 10 hours",
    start_date=start,
    end_date=end,
    schedule="@hourly",
    catchup=True,
    default_args={
        "owner": "airflow",
        "retries": 0,
    },
    max_active_runs=1,
    tags=["demo","swapi","mysql"],
) as dag:
    t = PythonOperator(
        task_id="upsert_people",
        python_callable=upsert_people,
    )

import os
import time
import requests
import mysql.connector
from urllib.parse import urlparse
from datetime import datetime

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpw")
DB_NAME = os.getenv("DB_NAME", "swapi")
SWAPI_ENTITY = os.getenv("SWAPI_ENTITY", "people")
SWAPI_PAGES = int(os.getenv("SWAPI_PAGES", "1"))

def connect_db():
    for attempt in range(40):
        try:
            cnx = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cnx.autocommit = True
            cur = cnx.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
            cur.close()
            cnx.close()
            # reconnect to specific DB
            return mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        except Exception as e:
            print(f"[DB] waiting for MySQL... ({attempt+1}/40): {e}")
            time.sleep(3)
    raise RuntimeError("Could not connect to MySQL after multiple attempts.")

def ensure_table(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS people (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            height VARCHAR(32),
            mass VARCHAR(32),
            hair_color VARCHAR(64),
            skin_color VARCHAR(64),
            eye_color VARCHAR(64),
            birth_year VARCHAR(32),
            gender VARCHAR(32),
            homeworld VARCHAR(255),
            url VARCHAR(255) UNIQUE,
            created DATETIME NULL,
            edited DATETIME NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

def parse_dt(value):
    if not value:
        return None
    try:
        # SWAPI uses ISO format with Z
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None

def insert_person(cur, p):
    cur.execute(
        """
        INSERT INTO people
        (name, height, mass, hair_color, skin_color, eye_color, birth_year, gender, homeworld, url, created, edited)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          name=VALUES(name),
          height=VALUES(height),
          mass=VALUES(mass),
          hair_color=VALUES(hair_color),
          skin_color=VALUES(skin_color),
          eye_color=VALUES(eye_color),
          birth_year=VALUES(birth_year),
          gender=VALUES(gender),
          homeworld=VALUES(homeworld),
          created=VALUES(created),
          edited=VALUES(edited)
        """,
        (
            p.get("name"),
            p.get("height"),
            p.get("mass"),
            p.get("hair_color"),
            p.get("skin_color"),
            p.get("eye_color"),
            p.get("birth_year"),
            p.get("gender"),
            p.get("homeworld"),
            p.get("url"),
            parse_dt(p.get("created")),
            parse_dt(p.get("edited")),
        ),
    )

def fetch_swapi_people(pages=1):
    base = f"https://swapi.dev/api/people/"
    results = []
    url = base
    page = 1
    while url and page <= pages:
        print(f"[SWAPI] GET {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        url = data.get("next")
        page += 1
    return results

def main():
    print(f"Loading SWAPI entity='{SWAPI_ENTITY}' pages={SWAPI_PAGES} -> MySQL {DB_HOST}:{DB_PORT}/{DB_NAME}")
    if SWAPI_ENTITY != "people":
        raise SystemExit("This minimal demo only supports entity=people.")

    cnx = connect_db()
    cur = cnx.cursor()
    ensure_table(cur)

    people = fetch_swapi_people(SWAPI_PAGES)
    print(f"[SWAPI] retrieved {len(people)} records")

    inserted = 0
    for p in people:
        insert_person(cur, p)
        inserted += 1
    cnx.commit()
    cur.close()
    cnx.close()
    print(f"[DB] upserted {inserted} rows into people table. Done.")

if __name__ == "__main__":
    main()
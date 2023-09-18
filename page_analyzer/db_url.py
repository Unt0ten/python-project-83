import psycopg2
import os
from dotenv import load_dotenv
from page_analyzer.tools import make_dict_urls, make_dict_checks

DATABASE_URL = os.getenv('DATABASE_URL')
load_dotenv()

keepalive_kwargs = {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 5,
    "keepalives_count": 5,
}

def get_pool():
    connection = psycopg2.connect(DATABASE_URL, **keepalive_kwargs)
    try:
        print('[INFO] Сonnection from "get_name_pool" was successful!')

        with connection.cursor() as cursor:
            cursor.execute(
                '''SELECT name FROM urls ORDER BY id DESC;'''
                )
            pool_name = [(row[0]) for row in cursor]
            cursor.execute(
                '''SELECT id FROM urls ORDER BY id DESC;'''
                )
            pool_id = [(row[0]) for row in cursor]

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)

    finally:
        if connection:
            connection.close()
            print('[INFO] Pool from "get_name_pool" connection closed')

        return pool_name, pool_id


class DB:
    conn = psycopg2.connect(DATABASE_URL, **keepalive_kwargs)
    try:
        print('[INFO] Сonnection was successful!')

        def add_url(self, norm_url, conn=conn):
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''INSERT INTO urls (name)
                    VALUES (%s);''', (norm_url,)
                    )

        def get_data_from_id(self, id, conn=conn):
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''SELECT name FROM urls WHERE id = %s;''', (id,)
                    )
                name = cursor.fetchone()

                cursor.execute(
                    '''SELECT created_at FROM urls WHERE name = %s;''',
                    (name,)
                    )
                created_at = cursor.fetchone()

                return name[0], created_at[0]

        def get_all_data_urls(self, conn=conn):
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''SELECT * FROM urls ORDER BY id DESC;'''
                    )

                result = cursor.fetchall()
                return make_dict_urls(result)

        def get_id(self, name, conn=conn):
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''SELECT id FROM urls WHERE name = %s;''', (name,)
                    )
                id = cursor.fetchall()

                return id[0][0]

        def add_checks(self, id, args, conn=conn):
            status_code, h1, title, description = args
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s);''',
                    (id, status_code, h1, title, description)
                    )

        def get_url_checks(self, id, conn=conn):
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    '''SELECT * FROM url_checks
                    WHERE url_id = (%s)
                    ORDER BY id DESC;''', (id,)
                    )

                result = cursor.fetchall()

                return make_dict_checks(result)

        def get_last_check_data(self, conn=conn):
            data = []
            with conn.cursor() as cursor:
                conn.autocommit = True
                cursor.execute(
                    """SELECT DISTINCT ON (urls.id) urls.id,
                        urls.name, url_checks.status_code, url_checks.created_at
                        FROM urls LEFT JOIN url_checks
                            ON urls.id = url_checks.url_id
                    ORDER BY urls.id DESC;
                    """)
                result = cursor.fetchall()
            for row in result:
                data.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "status": row[2],
                        "created_at": row[3]
                        }
                    )
            return data

    except Exception as ex:
        conn.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)

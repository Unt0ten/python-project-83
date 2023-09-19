import psycopg2
import os
from dotenv import load_dotenv
from page_analyzer.tools import make_dict_urls, make_dict_checks

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def proc_data(request):
    connection = psycopg2.connect(DATABASE_URL)
    try:
        print('[INFO] Сonnection was successful!')

        with connection.cursor() as cursor:
            connection.autocommit = True
            cursor.execute(*request)
            return cursor.fetchall()

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)

    finally:
        if connection:
            connection.close()
            print('[INFO] Connection closed')


def get_pool():
    request_names = ('''SELECT name FROM urls ORDER BY id DESC;''',)
    request_id = ('''SELECT id FROM urls ORDER BY id DESC;''',)
    pool_name = [(row[0]) for row in proc_data(request_names)]
    pool_id = [(row[0]) for row in proc_data(request_id)]

    return pool_name, pool_id


class DB:
    def add_url(self, norm_url):
        request = '''INSERT INTO urls (name)
                VALUES (%s);''', (norm_url,)
        proc_data(request)

    def get_data_from_id(self, id):
        request_name = '''SELECT name FROM urls WHERE id = %s;''', (id,)

        name = proc_data(request_name)

        request_created_at = '''SELECT created_at
         FROM urls WHERE name = %s;''', name

        created_at = proc_data(request_created_at)

        return name[0][0], created_at[0][0]

    def get_all_data_urls(self):
        request = '''SELECT * FROM urls ORDER BY id DESC;'''

        result = proc_data(request)

        return make_dict_urls(result)

    def get_id(self, name):
        request = '''SELECT id FROM urls WHERE name = %s;''', (name,)

        id = proc_data(request)

        return id[0][0]

    def add_checks(self, id, *args):
        # status_code, h1, title, description = args
        request = '''INSERT INTO url_checks
                (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s);''', (
            id, *args)

        proc_data(request)

    def get_url_checks(self, id):
        request = '''SELECT * FROM url_checks
                WHERE url_id = (%s)
                ORDER BY id DESC;''', (id,)

        result = proc_data(request)
        return make_dict_checks(result)

    def get_last_check_data(self):
        data = []
        request = ("""SELECT DISTINCT ON (urls.id) urls.id,
                    urls.name, url_checks.status_code, url_checks.created_at
                    FROM urls LEFT JOIN url_checks
                        ON urls.id = url_checks.url_id
                ORDER BY urls.id DESC;""",)

        result = proc_data(request)
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

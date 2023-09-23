from dotenv import load_dotenv
import psycopg2.extras

load_dotenv()


def get_pool(connection):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor() as cursor:
            cursor.execute('''SELECT id, name FROM urls ORDER BY id DESC;''')
            common_pool = cursor.fetchall()
            pool_id = [(row[0]) for row in common_pool]
            pool_name = [(row[1]) for row in common_pool]

            return pool_name, pool_id

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def add_url(connection, norm_url):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO urls (name)
                    VALUES (%s);''', (norm_url,))

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def get_data_from_id(connection, id):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor() as cursor:
            cursor.execute('''SELECT name FROM urls WHERE id = %s;''', (id,))
            name = cursor.fetchall()

            cursor.execute('''SELECT created_at
             FROM urls WHERE name = %s;''', name)
            created_at = cursor.fetchall()

            return name[0][0], created_at[0][0]

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def get_id(connection, name):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor() as cursor:
            cursor.execute('''SELECT id FROM urls WHERE name = %s;''', (name,))
            id = cursor.fetchall()
            return id[0][0]

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def add_checks(connection, id, *args):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor() as cursor:
            cursor.execute('''INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s);''', (
                id, *args))

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def get_url_checks(connection, id):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute('''SELECT * FROM url_checks
                    WHERE url_id = (%s)
                    ORDER BY id DESC;''', (id,))
            result = cursor.fetchall()
            return result

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)


def get_last_check_data(connection):
    try:
        print('[INFO] Сonnection was successful!')
        with connection.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute("""SELECT DISTINCT ON (urls.id) urls.id,
                    urls.name, url_checks.status_code, url_checks.created_at
                    FROM urls LEFT JOIN url_checks
                        ON urls.id = url_checks.url_id
                ORDER BY urls.id DESC;""")
            result = cursor.fetchall()
            return result

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)

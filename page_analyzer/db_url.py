import psycopg2.extras


def get_connection(database_url):
    connection = psycopg2.connect(database_url)
    print('[INFO] Сonnection was successful!')
    return connection


def connection_close(connection):
    print('[INFO] Connection was closed!')
    connection.close()


def add_url(connection, url):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO urls (name) VALUES (%s);', (url,)
            )
            connection.commit()
            print('[INFO] Adding url was successful!')

    except Exception as ex:
        print('[WARNING] Error while adding url:', ex)
        raise ex


def get_url_by_id(connection, id):
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cursor:
            cursor.execute(
                'SELECT name, created_at FROM urls WHERE id = %s;', (id,)
            )
            urls = cursor.fetchone()
            connection.commit()
            print('[INFO] Retrieving url by id was successful!')

            return urls

    except Exception as ex:
        print('[WARNING] Error when getting url by id:', ex)
        raise ex


def get_url_by_name(connection, name):
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cursor:
            cursor.execute(
                'SELECT * FROM urls WHERE name = %s;', (name,)
            )
            url = cursor.fetchone()
            connection.commit()
            print('[INFO] Retrieving url by name was successful!')

            return url

    except Exception as ex:
        print('[WARNING] Error when getting url by name:', ex)
        raise ex


def add_check(connection, id, page_data):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s);''',
                (
                    id, page_data['status'], page_data['h1'],
                    page_data['title'], page_data['description']
                )
            )
            connection.commit()
            print('[INFO] Adding check was successful!')

    except Exception as ex:
        print('[WARNING] Error while adding check:', ex)
        raise ex


def get_url_checks(connection, url_id):
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cursor:
            cursor.execute(
                '''SELECT * FROM url_checks
                    WHERE url_id = (%s)
                    ORDER BY id DESC;''', (url_id,)
            )
            result = cursor.fetchall()
            connection.commit()
            print('[INFO] Retrieving url checks was successful!')

            return result

    except Exception as ex:
        print('[WARNING] Error when retrieving url checks:', ex)
        raise ex


def get_last_checks(connection):
    last_checks = []
    try:
        with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cursor:
            cursor.execute(
                'SELECT id, name FROM urls ORDER BY id DESC;'
            )
            urls = cursor.fetchall()

        with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cursor:
            cursor.execute(
                '''SELECT DISTINCT ON (url_id) url_id, status_code, created_at
                FROM url_checks
                ORDER BY url_id DESC, created_at DESC;'''
            )
            checks = cursor.fetchall()

        for url in urls:
            for check in checks:
                if url.id == check.url_id:
                    last_checks.append(
                        {
                            'id': url.id,
                            'name': url.name,
                            'created_at': check.created_at,
                            'status_code': check.status_code
                        }
                    )
                    break
            else:
                last_checks.append(
                    {
                        'id': url.id,
                        'name': url.name,
                        'created_at': None,
                        'status_code': None
                    }
                )
        connection.commit()
        print('[INFO] Retrieving url last checks was successful!')
        return last_checks

    except Exception as ex:
        print('[WARNING] Error when retrieving url last checks:', ex)
        raise ex

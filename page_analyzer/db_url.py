import psycopg2
import os
from dotenv import load_dotenv
from page_analyzer.tools import make_dict

DATABASE_URL = os.getenv('DATABASE_URL')
load_dotenv()


def get_name_pool():
    connection = psycopg2.connect(DATABASE_URL)
    try:
        print('[INFO] Сonnection from "get_name_pool" was successful!')

        with connection.cursor() as cursor:
            cursor.execute(
                '''SELECT name FROM urls ORDER BY id DESC;'''
                )
            name_pool = [row[0] for row in cursor]

    except Exception as ex:
        connection.rollback()
        print('[INFO] Error while working with PostgreSQL', ex)

    finally:
        if connection:
            connection.close()
            print('[INFO] Pool from "get_name_pool" connection closed')

    return name_pool


class DB:
    def add_url(self, norm_url):
        connection = psycopg2.connect(DATABASE_URL)

        try:
            print('[INFO] Сonnection was successful!')
            with connection.cursor() as cursor:
                cursor.execute(
                    '''INSERT INTO urls (name)
                    VALUES (%s);''', (norm_url,)
                    )
                connection.commit()

        except Exception as ex:
            connection.rollback()
            print('[INFO] Error while working with PostgreSQL', ex)

        finally:
            if connection:
                connection.close()
                print('[INFO] PostgeSQL connection closed')

    def get_data_from_id(self, id):
        connection = psycopg2.connect(DATABASE_URL)

        try:
            print('[INFO] Сonnection was successful!')

            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT name FROM urls WHERE id = %s;''', (id,)
                    )
                name = cursor.fetchone()

                cursor.execute(
                    '''SELECT created_at FROM urls WHERE name = %s;''', (name,)
                    )
                created_at = cursor.fetchone()

        except Exception as ex:
            connection.rollback()
            print('[INFO] Error while working with PostgreSQL', ex)

        finally:
            if connection:
                connection.close()
                print('[INFO] PostgeSQL connection closed')

        return name[0], created_at[0]

    def get_all_data(self):
        connection = psycopg2.connect(DATABASE_URL)

        try:
            print('[INFO] Сonnection was successful!')
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT id FROM urls ORDER BY id DESC;'''
                    )
                data_id = [row[0] for row in cursor]
                cursor.execute(
                    '''SELECT name FROM urls ORDER BY id DESC;'''
                    )
                data_name = [row[0] for row in cursor]
                cursor.execute(
                    '''SELECT created_at FROM urls ORDER BY id DESC;'''
                    )
                data_created_at = [row[0] for row in cursor]

            result = make_dict(data_id, data_name, data_created_at)

        except Exception as ex:
            connection.rollback()
            print('[INFO] Error while working with PostgreSQL', ex)

        finally:
            if connection:
                connection.close()
                print('[INFO] PostgeSQL connection closed')

        return result

    def get_id(self, name):
        connection = psycopg2.connect(DATABASE_URL)
        try:
            print('[INFO] Сonnection from "get_id" was successful!')
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT id FROM urls WHERE name = %s;''', (name,)
                    )
                id = cursor.fetchall()

        except Exception as ex:
            connection.rollback()
            print('[INFO] Error while working with PostgreSQL', ex)

        finally:
            if connection:
                connection.close()
                print('[INFO] PostgeSQL from "get_id" connection closed')

        return id[0][0]

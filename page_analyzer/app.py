from flask import Flask, render_template
import jinja2
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(['templates']),
    ])
app.jinja_loader = my_loader
DATABASE_URL = os.getenv('DATABASE_URL')
load_dotenv()

try:
    connection = psycopg2.connect(DATABASE_URL)
    print('[INFO] Сonnection was successful!')
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT version();'
            )
        print(f'Server version {cursor.fetchone()}')


    @app.route('/')
    def open_main():
        return render_template('index.html')


    @app.route('/urls/<id>')
    def get_specific_data(id):
        return render_template('specific_data.html')


    @app.route('/urls')
    def get_all_data():
        return render_template('all_data.html')

except Exception as ex:
    print('[INFO] Error while working with PostgreSQL', ex)

finally:
    if connection:
        connection.close()
        print('[INFO] PostgeSQL connection closed')

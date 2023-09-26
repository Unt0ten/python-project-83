from urllib.parse import urlparse
from page_analyzer.db_url import (
    get_pool,
    add_url,
    get_data_from_id,
    get_url_checks,
    get_last_check_data,
    add_checks,
    get_id,
    get_connection)
from page_analyzer.tools import (
    validate_len,
    normalize_url,
    validate_status_code)
from page_analyzer.connection import PHtml
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    get_flashed_messages,
    redirect)
import requests
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.errorhandler(404)
def not_found(error):
    return render_template('error_404.html'), 404


@app.route('/')
def get_main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls')
def get_all_urls():
    conn = get_connection(DATABASE_URL)
    data = get_last_check_data(conn)
    return render_template('all_data.html',
                           data=data
                           )


@app.route('/urls', methods=['POST'])
def post_urls():
    conn = get_connection(DATABASE_URL)
    data = request.form.get('url')
    if not data:
        flash('URL обязателен', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    url = urlparse(data)
    norm_url = normalize_url(url)

    if not norm_url:
        flash('Некорректный URL', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    errors = validate_len(data)
    pool_name, _ = get_pool(conn)

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    elif norm_url in pool_name:
        id_ = get_id(conn, norm_url)
        print(id_)
        flash('Страница уже существует', 'success')
        return redirect(url_for('get_url_from_id',
                                id=id_))

    add_url(conn, norm_url)
    flash('Страница успешно добавлена', 'success')
    id = get_id(conn, norm_url)

    return redirect(url_for('get_url_from_id', id=id), code=302)


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    conn = get_connection(DATABASE_URL)
    _, pool_id = get_pool(conn)
    if id not in pool_id:
        return not_found(404)

    messages = get_flashed_messages(with_categories=True)
    name, created_at = get_data_from_id(conn, id)
    checks = get_url_checks(conn, id)
    return render_template('specific_data.html',
                           id=id,
                           name=name,
                           created_at=created_at,
                           messages=messages,
                           checks=checks
                           )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn = get_connection(DATABASE_URL)
    url, _ = get_data_from_id(conn, id)
    try:
        resp = requests.get(url)
        soup = PHtml(resp)
        status = validate_status_code(resp.status_code)
        h1 = soup.get_h1()
        title = soup.get_title()
        description = soup.get_description()
        add_checks(conn, id, status, h1, title, description)
        flash('Страница успешно проверена', 'success')

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'warning')

    return redirect(url_for('get_url_from_id',
                            id=id,
                            ), 302)

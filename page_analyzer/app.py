from urllib.parse import urlparse
from page_analyzer.db_url import (
    get_pool,
    add_url,
    get_data_from_id,
    get_url_checks,
    get_last_check_data,
    add_checks,
    get_id)
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

CONN = psycopg2.connect(DATABASE_URL)
CONN.autocommit = True


@app.errorhandler(404)
def not_found(error):
    return render_template('error_404.html'), 404


@app.route('/')
def get_index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls')
def get_all_urls():
    data = get_last_check_data(CONN)
    return render_template('all_data.html',
                           data=data
                           )


@app.route('/urls', methods=['POST'])
def post_urls():
    data = request.form.get('url')
    if not data:
        flash('URL обязателен', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422

    url = urlparse(data)
    norm_url = normalize_url(url)

    if not norm_url:
        flash('Некорректный URL', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422

    errors = validate_len(data)
    pool_name, _ = get_pool(CONN)

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422

    elif norm_url in pool_name:
        id_ = get_id(CONN, norm_url)
        print(id_)
        flash('Страница уже существует', 'success')
        return redirect(url_for('get_url_from_id',
                                id=id_))

    add_url(norm_url)
    flash('Страница успешно добавлена', 'success')
    id = get_id(CONN, norm_url)

    return redirect(url_for('get_url_from_id', id=id), code=302)


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    _, pool_id = get_pool(CONN)
    if id not in pool_id:
        return not_found(404)

    messages = get_flashed_messages(with_categories=True)
    name, created_at = get_data_from_id(CONN, id)
    checks = get_url_checks(CONN, id)
    return render_template('specific_data.html',
                           id=id,
                           name=name,
                           created_at=created_at,
                           messages=messages,
                           checks=checks
                           )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    url, _ = get_data_from_id(CONN, id)
    try:
        resp = requests.get(url)
        soup = PHtml(resp)
        status = validate_status_code(resp.status_code)
        h1 = soup.get_h1()
        title = soup.get_title()
        description = soup.get_description()
        add_checks(CONN, id, status, h1, title, description)
        flash('Страница успешно проверена', 'success')

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'warning')

    return redirect(url_for('get_url_from_id',
                            id=id,
                            ), 302)

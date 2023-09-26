from urllib.parse import urlparse
import page_analyzer.db_url
import page_analyzer.tools
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
    conn = page_analyzer.db_url.get_connection(DATABASE_URL)
    data = page_analyzer.db_url.get_last_check_data(conn)
    return render_template('all_data.html',
                           data=data
                           )


@app.route('/urls', methods=['POST'])
def post_urls():
    conn = page_analyzer.db_url.get_connection(DATABASE_URL)
    data = request.form.get('url')
    if not data:
        flash('URL обязателен', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    url = urlparse(data)
    norm_url = page_analyzer.tools.normalize_url(url)

    if not norm_url:
        flash('Некорректный URL', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    errors = page_analyzer.tools.validate_len(data)
    pool_name, _ = page_analyzer.db_url.get_pool(conn)

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    elif norm_url in pool_name:
        id_ = page_analyzer.db_url.get_id(conn, norm_url)
        flash('Страница уже существует', 'success')
        return redirect(url_for('get_url_from_id',
                                id=id_))

    page_analyzer.db_url.add_url(conn, norm_url)
    flash('Страница успешно добавлена', 'success')
    id = page_analyzer.db_url.get_id(conn, norm_url)

    return redirect(url_for('get_url_from_id', id=id), code=302)


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    conn = page_analyzer.db_url.get_connection(DATABASE_URL)
    _, pool_id = page_analyzer.db_url.get_pool(conn)
    if id not in pool_id:
        return not_found(404)

    messages = get_flashed_messages(with_categories=True)
    name, created_at = page_analyzer.db_url.get_data_from_id(conn, id)
    checks = page_analyzer.db_url.get_url_checks(conn, id)
    return render_template('specific_data.html',
                           id=id,
                           name=name,
                           created_at=created_at,
                           messages=messages,
                           checks=checks
                           )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn = page_analyzer.db_url.get_connection(DATABASE_URL)
    url, _ = page_analyzer.db_url.get_data_from_id(conn, id)
    try:
        resp = requests.get(url)
        soup = PHtml(resp)
        status = page_analyzer.tools.validate_status_code(resp.status_code)
        h1 = soup.get_h1()
        title = soup.get_title()
        description = soup.get_description()
        page_analyzer.db_url.add_checks(conn,
                                        id,
                                        status,
                                        h1,
                                        title,
                                        description)
        flash('Страница успешно проверена', 'success')

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'warning')

    return redirect(url_for('get_url_from_id',
                            id=id,
                            ), 302)

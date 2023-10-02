from urllib.parse import urlparse
from page_analyzer import db_url
from page_analyzer import tools
from page_analyzer.seo import get_seo
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    get_flashed_messages,
    redirect,
    abort
)
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/error_404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/error_500.html'), 500


@app.route('/')
def get_main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls')
def get_all_urls():
    conn = db_url.get_connection(DATABASE_URL)
    data = db_url.get_last_check_data(conn)
    db_url.conn_close(conn)
    return render_template('url/urls.html', data=data)


@app.route('/urls', methods=['POST'])
def post_urls():
    conn = db_url.get_connection(DATABASE_URL)
    data = request.form.get('url')
    if not data:
        flash('URL обязателен', 'warning')
        messages = get_flashed_messages(with_categories=True)
        db_url.conn_close(conn)
        return render_template('index.html', messages=messages), 422

    url = urlparse(data)
    norm_url = tools.normalize_url(url)

    if not norm_url:
        flash('Некорректный URL', 'warning')
        messages = get_flashed_messages(with_categories=True)
        db_url.conn_close(conn)
        return render_template('index.html', messages=messages), 422

    errors = tools.validate_len(data)

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages(with_categories=True)
        db_url.conn_close(conn)
        return render_template('index.html', messages=messages), 422

    searched_name = db_url.get_url_by_name(conn, norm_url)

    if searched_name:
        flash('Страница уже существует', 'success')
        db_url.conn_close(conn)
        return redirect(
            url_for(
                'get_url_from_id',
                id=searched_name.id
            )
        )

    db_url.add_url(conn, norm_url)
    flash('Страница успешно добавлена', 'success')
    url = db_url.get_url_by_name(conn, norm_url)
    db_url.conn_close(conn)

    return redirect(url_for('get_url_from_id', id=url.id), code=302)


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    conn = db_url.get_connection(DATABASE_URL)
    searched_id = db_url.get_url_id(id, conn)
    if not searched_id:
        db_url.conn_close(conn)
        abort(404)

    messages = get_flashed_messages(with_categories=True)
    info_url = db_url.get_url_by_id(conn, id)
    checks = db_url.get_url_checks(conn, id)
    db_url.conn_close(conn)
    return render_template(
        'url/url.html',
        id=id,
        info_url=info_url,
        messages=messages,
        checks=checks
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    conn = db_url.get_connection(DATABASE_URL)
    url = db_url.get_url_by_id(conn, id)
    try:
        resp = requests.get(url.name)
        seo = get_seo(resp)
        status = tools.validate_status_code(resp.status_code)
        db_url.add_check(conn, id, status, *seo)
        flash('Страница успешно проверена', 'success')
        db_url.conn_close(conn)

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'warning')
        db_url.conn_close(conn)

    return redirect(url_for('get_url_from_id', id=id), 302)

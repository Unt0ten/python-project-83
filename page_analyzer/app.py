from urllib.parse import urlparse
from page_analyzer import db_url
from page_analyzer import tools
from page_analyzer.seo import get_page_data
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
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.errorhandler(404)
def not_found(error):
    print('[INFO]', error)
    return render_template('errors/error_404.html'), 404


@app.errorhandler(500)
def server_error(error):
    print('[INFO] Internal Server Error', error)
    return render_template('errors/error_500.html', error=error), 500


@app.route('/')
def get_main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls')
def get_urls():
    conn = db_url.get_connection(DATABASE_URL)
    try:
        data = db_url.get_last_checks(conn)
        db_url.connection_close(conn)
        return render_template('url/urls.html', data=data)

    except Exception as ex:
        abort(500, ex)
        db_url.connection_close(conn)


@app.route('/urls', methods=['POST'])
def post_urls():
    conn = db_url.get_connection(DATABASE_URL)
    try:
        data = request.form.get('url')
        if not data:
            flash('URL обязателен', 'warning')
            messages = get_flashed_messages(with_categories=True)
            db_url.connection_close(conn)
            return render_template('index.html', messages=messages), 422

        url = urlparse(data)
        norm_url = tools.normalize_url(url)

        if not norm_url:
            flash('Некорректный URL', 'warning')
            messages = get_flashed_messages(with_categories=True)
            db_url.connection_close(conn)
            return render_template('index.html', messages=messages), 422

        errors = tools.validate_len(data)

        if errors:
            flash('URL превышает 255 символов', 'warning')
            messages = get_flashed_messages(with_categories=True)
            db_url.connection_close(conn)
            return render_template('index.html', messages=messages), 422

        found_url = db_url.get_url_by_name(conn, norm_url)

        if found_url:
            flash('Страница уже существует', 'success')
            db_url.connection_close(conn)
            return redirect(
                url_for(
                    'get_url',
                    id=found_url.id
                )
            )

        db_url.add_url(conn, norm_url)
        flash('Страница успешно добавлена', 'success')
        url = db_url.get_url_by_name(conn, norm_url)
        db_url.connection_close(conn)

        return redirect(url_for('get_url', id=url.id), code=302)

    except Exception as ex:
        abort(500, ex)
        db_url.connection_close(conn)


@app.route('/urls/<int:id>')
def get_url(id):
    conn = db_url.get_connection(DATABASE_URL)
    try:
        searched_id = db_url.get_url_by_id(conn, id)
        if not searched_id:
            db_url.connection_close(conn)
            abort(404)

        messages = get_flashed_messages(with_categories=True)
        info_url = db_url.get_url_by_id(conn, id)
        checks = db_url.get_url_checks(conn, id)
        db_url.connection_close(conn)
        return render_template(
            'url/url.html',
            id=id,
            info_url=info_url,
            messages=messages,
            checks=checks
        )

    except Exception as ex:
        abort(500, ex)
        db_url.connection_close(conn)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def post_url_check(id):
    conn = db_url.get_connection(DATABASE_URL)
    try:
        url = db_url.get_url_by_id(conn, id)
        resp = tools.get_response(url.name)
        if not resp:
            flash('Произошла ошибка при проверке', 'warning')
            db_url.connection_close(conn)
            return redirect(url_for('get_url', id=id), 302)

        page_data = get_page_data(resp)
        db_url.add_check(conn, id, page_data)
        flash('Страница успешно проверена', 'success')
        db_url.connection_close(conn)
        return redirect(url_for('get_url', id=id), 302)

    except Exception as ex:
        abort(500, ex)
        db_url.connection_close(conn)

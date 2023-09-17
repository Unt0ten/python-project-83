from urllib.parse import urlparse
from page_analyzer.db_url import DB, get_pool
from page_analyzer.tools import validate, normalize_url
from page_analyzer.connection import get_seo
from flask import (
    Flask,
    render_template,
    request,
    url_for,
    flash,
    get_flashed_messages,
    redirect,
    make_response
    )
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
repo = DB()


@app.route('/')
def open_main():
    return render_template('index.html')


@app.route('/urls')
def get_all_urls():
    data = repo.get_last_check_data()
    messages = get_flashed_messages()
    return render_template('all_data.html',
                           data=data,
                           messages=messages
                           )


@app.route('/urls', methods=['POST'])
def post_new_data():
    data = request.form.get('url')
    if not data:
        flash('URL обязателен', 'warning')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    url = urlparse(data)
    norm_url = normalize_url(url)

    if not norm_url:
        flash('Некорректный URL', 'warning')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    errors = validate(data)
    POOL_NAME, _ = get_pool()

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    elif norm_url in POOL_NAME:
        id_ = repo.get_id(norm_url)
        flash('Страница уже существует', 'warning')
        return redirect(url_for('get_url_from_id', id=id_))

    repo.add_url(norm_url)
    flash('Страница успешно добавлена', 'success')
    id = repo.get_id(norm_url)

    return make_response(
        redirect(url_for('get_url_from_id', id=id), code=302))


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    _, POOL_ID = get_pool()
    if id not in POOL_ID:
        return render_template('error_404.html'), 404

    messages = get_flashed_messages()
    name, created_at = repo.get_data_from_id(id)
    checks = repo.get_url_checks(id)
    return render_template('specific_data.html',
                           id=id,
                           name=name,
                           created_at=created_at,
                           messages=messages,
                           checks=checks
                           )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    url, _ = repo.get_data_from_id(id)
    info = get_seo(url)
    if not info:
        flash('Произошла ошибка при проверке', 'warning')
        return redirect(url_for('get_url_from_id',
                            id=id,
                            ))

    repo.add_checks(id, info)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url_from_id',
                            id=id,
                            ))

from urllib.parse import urlparse
from page_analyzer.db_url import DB, get_name_pool
from page_analyzer.tools import validate, normalize_url
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
    data = repo.get_all_data()
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

    pool = get_name_pool()
    url = urlparse(data)
    norm_url = normalize_url(url)
    errors = validate(data)

    if errors:
        flash('URL превышает 255 символов', 'warning')
        messages = get_flashed_messages()
        return render_template('index.html', messages=messages)

    elif norm_url in pool:
        id_ = repo.get_id(norm_url)
        flash('Страница уже существует', 'warning')
        return redirect(url_for('get_url_from_id', id=id_))

    else:
        flash('Страница успешно добавлена', 'success')
        repo.add_url(norm_url)
        id = repo.get_id(norm_url)

        return make_response(
            redirect(url_for('get_url_from_id', id=id), code=302))


@app.route('/urls/<int:id>')
def get_url_from_id(id):
    messages = get_flashed_messages()
    name, created_at = repo.get_data_from_id(id)
    return render_template('specific_data.html',
                           id=id,
                           name=name,
                           created_at=created_at,
                           messages=messages
                           )

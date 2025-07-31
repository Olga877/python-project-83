import os
from urllib.parse import urlparse

import psycopg2
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from url_repository import UrlRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


conn = psycopg2.connect(DATABASE_URL)
repo = UrlRepository(conn)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/urls/<int:id>')
def url_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)
    checked_urls = repo.find_checks(id)
    return render_template(
        'show.html',
        url=url,
        checked_urls=checked_urls,
        messages=messages
    )


@app.route('/urls')
def urls_get():
    urls = repo.get_content()
    return render_template(
        'urls.html',
         urls=urls
    )


@app.post('/')
def url_post():
    # term = request.args.get('term', '')
    unparsed_url = request.form['url']
    parsed_url = urlparse(request.form['url'])
    url_data = f"{parsed_url.scheme}://{parsed_url.netloc}"
    is_valid = validators.url(unparsed_url)
    if not is_valid:
        flash('Некорректный URL', 'error')
        return render_template(
            'index.html',
            url_address=unparsed_url,
            # errors=errors,
        )
    unique_url = repo.is_unique(url_data)
    if unique_url:
        url_id = repo.save(url_data)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_show', id=url_id), code=302)
    else:
        url_id = repo.find_by_name(url_data)
        flash('Страница уже существует', 'error')
        return redirect(url_for('url_show', id=url_id), code=302)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def url_check(id):
    url = repo.find(id)
    result = repo.get_checked(id)
    if result:
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('url_show', id=url['id']), code=302)
    else:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_show', id=url['id']), code=302)


if __name__ == '__main__':
    app.run(debug=True)
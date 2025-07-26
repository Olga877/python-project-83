import os
from dotenv import load_dotenv
from flask import (
    get_flashed_messages,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)
import psycopg2
import validators
from urllib.parse import urlparse
from url_repository import UrlRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


conn = psycopg2.connect(DATABASE_URL)
repo = UrlRepository(conn)




# def validate(url):
#     parsed_url = urlparse(url)
#     return all([parsed_url.scheme, parsed_url.netloc])

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/urls/<id>')
def url_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)
    return render_template(
        'show.html',
        url=url,
        messages=messages
    )

@app.route('/urls')
def urls_get():
    # messages = get_flashed_messages(with_categories=True)
    # term = request.args.get('term', '')
    # if term:
    #     users = repo.get_by_term(term)
    # else:
    #     users = repo.get_content()
    return render_template(
        'urls.html',
        # users=users,
        # search=term,
        # messages=messages
    )

@app.post('/')
def url_post():
    url = request.form['url']
    is_valid = validators.url(url)
    if not is_valid:
        flash('Некорректный URL', 'error')
        return render_template(
            'index.html',
            url=url,
            # errors=errors,
        )
    repo.save(url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_show(id)'), code=302)


if __name__ == '__main__':
    app.run(debug=True)
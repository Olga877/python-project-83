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

@app.route('/urls/<int:id>')
def url_show(id):
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)
    # check_id = repo.get_checked(id)
    checked_urls = repo.find_checks(id)
    return render_template(
        'show.html',
        url=url,
        checked_urls=checked_urls,
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
    urls = repo.get_content()
    return render_template(
        'urls.html',
         urls=urls
        # search=term,
        # messages=messages
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
    repo.get_checked(id)
    # checked_url =repo.find_checks(check_id)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_show', id=url['id']), code=302)






if __name__ == '__main__':
    app.run(debug=True)
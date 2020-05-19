## Main routes

from flask import render_template, redirect, url_for, Response, Blueprint
from ..forms import SearchForm
from .. import client

main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('main.query_results', query=form.search_query.data))

    return render_template('index.html', form=form)

@main.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)
    print(results)

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])

    if len(results) == 0:
        return render_template('query.html', error_msg="No results found.")
    
    return render_template('query.html', results=results)

@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


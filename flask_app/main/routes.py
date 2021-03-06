## Main routes
from bs4 import BeautifulSoup
from flask import render_template, redirect, url_for, Response, Blueprint, flash
from flask_mail import Message
from flask_login import current_user
import requests

from .. import client, mail
from ..forms import SearchForm, InviteFriendForm
from ..utils import current_time
from ..models import Review

main = Blueprint("main", __name__)

def find_top_ten():
    top_ten = []
    steampage = BeautifulSoup(requests.get('https://store.steampowered.com/stats/').text, "html.parser")
    for row in steampage('tr', {'class' :'player_count_row', 'style' :''}):
        x = row.text.split('\n')
        (cur, peak, name) = (x[2], x[5], x[9])
        results = client.search(name)
        guess = results[0] if len(results) > 0 else None
        top_ten.append((cur, peak, name, guess))
    return top_ten


@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    top_ten = find_top_ten()
    reviews = Review.objects.order_by('-date').limit(10)
    game_s = url_for('static', filename='spiderman.jpg')
    game_c = url_for('static', filename='starwars.jpg')
    game_a = url_for('static', filename='witcher.jpg')
    if form.validate_on_submit():
        return redirect(url_for('main.query_results', query=form.search_query.data))

    return render_template('index.html', form=form, top_ten=top_ten, date=current_time(), reviews=reviews, game_a = game_a, game_s = game_s, game_c= game_c)

@main.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client.search(query)

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])

    if len(results) == 0:
        return render_template('query.html', error_msg="No results found.")
    
    return render_template('query.html', results=results)

@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@main.route('/invite', methods=['POST', 'GET'])
def invite():
    invite_form = InviteFriendForm()
    invite_form.subject.data = f'Hello from {current_user.username}!'
    if invite_form.validate_on_submit():
        msg = Message(f'Hello from {current_user.username}!', sender = ('GoodPlays', 'goodplays2020@gmail.com'), recipients = [invite_form.email.data])
        msg.body = invite_form.body.data
        mail.send(msg)
        flash("Sent email!")
        return redirect(url_for('main.invite'))
    
    return render_template("invite.html", invite_form=invite_form)

find_top_ten()
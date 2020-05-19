## Game routes

from flask import render_template, request, redirect, url_for, Response, Blueprint
from flask_login import current_user
from ..forms import GameReviewForm
from ..utils import current_time
from ..models import User, Review, load_user
from .. import client

games = Blueprint("games", __name__)


@games.route('/games/<game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    result = client.retrieve_game_by_id(game_id)

    if type(result) == dict:
        return render_template('game_detail.html', error_msg=result['Error'])

    form = GameReviewForm()
    if form.validate_on_submit():
        review = Review(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            imdb_id=game_id,
            game_title=result.title
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=game_id)

    print(type(result.genres))
    return render_template('game_detail.html', form=form, game=result, reviews=reviews)
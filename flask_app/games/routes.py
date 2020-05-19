## Game routes

from flask import render_template, flash, request, redirect, url_for, Response, Blueprint
from flask_login import current_user
from ..forms import GameReviewForm, AddToListButton
from ..utils import current_time
from ..models import User, Review, UserGameList, Game, load_user
from .. import client

games = Blueprint("games", __name__)


@games.route('/games/<game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    result = client.retrieve_game_by_id(game_id)

    if type(result) == dict:
        return render_template('game_detail.html', error_msg=result['Error'])

    form = GameReviewForm()
    if 'reviews' in request.args and form.validate_on_submit():
        review = Review(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            game_id=game_id,
            game_title=result.name
        )

        review.save()

        return redirect(request.path)

    reviews = Review.objects(game_id=game_id)

    add_button = AddToListButton()
    if 'added' in request.args and add_button.validate_on_submit():
        new_game = Game (
            game_id=game_id,
            name=result.name
        )


        if UserGameList.objects(user=load_user(current_user.username)):
            
            user = UserGameList.objects(user=load_user(current_user.username)).get()

            if new_game in user.games:
                flash("This game is already in your list.")
            else:
                user.games.append(new_game)
                user.save()
                flash("Added to list!")
            
            return redirect(request.path)
        else:
            new_list = UserGameList(
                user=load_user(current_user.username), 
                games=[new_game]
            )
            new_list.save()
            flash("Added to list!")
        
            return redirect(request.path)

    return render_template('game_detail.html', add_button=add_button, form=form, game=result, reviews=reviews)
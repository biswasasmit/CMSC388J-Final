## Game routes

from flask import render_template, flash, request, redirect, url_for, Response, Blueprint
from flask_login import current_user, login_required
from ..forms import GameReviewForm, AddToListButton, AddToPlayedButton, AddToPlayedForm
from ..utils import current_time
from ..models import User, Review, UserGameList, Game, load_user, PlayedGame, DGame
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

    add_to_played_button = AddToPlayedButton()
    if 'played' in request.args and add_to_played_button.validate_on_submit():
        return redirect( url_for('games.add_played', game_id=result.id))

    games = DGame.objects(game_id=game_id)
    played = []
    
    if games:
        played = PlayedGame.objects(game=games.first())

    return render_template('game_detail.html', add_button=add_button, form=form, game=result, reviews=reviews, add_to_played_button=add_to_played_button, played=played)

@games.route('/games/add_to_played/<game_id>', methods=['GET', 'POST'])
@login_required
def add_played(game_id):
    result = client.retrieve_game_by_id(game_id)
    form = AddToPlayedForm()
    if form.validate_on_submit():
        game = DGame(
            game_id=game_id,
            name=result.name
        )
        game.save()
        played = PlayedGame(
            user=load_user(current_user.username),
            finished_on=form.finished_on.data,
            review=form.review.data,
            game=game
        )
        played.save()
        flash("Added played game!")

        return redirect(request.path)

    return render_template('add_to_played.html', form = form, game = result)
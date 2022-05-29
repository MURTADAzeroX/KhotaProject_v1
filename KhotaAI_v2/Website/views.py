from flask import Blueprint, render_template, request, flash,session
from flask_login import login_required, current_user
from .models import Note, User
from . import db
from datetime import datetime
from .AI_Functions import AIEngine, ConvertToPath, check_game

from werkzeug.security import generate_password_hash
import random

views = Blueprint('views', __name__)


def get_user_requests():
    data = User.query.all()
    re = []
    for i in data:
        if i.role == 'Temp':
            re.append(i)
    return re




@views.route('/TicTacToeAI', methods=['POST', 'GET'])
def TicTacToeAI():
    engine = AIEngine()
    print(current_user)
    if str(current_user).find('AnonymousUser') == -1:
        NU = current_user
    else:
        NU = None

    if session.get('UserStartSession') is None:
        session['Game'] = [''] * 9
        session['PlayerSym'] = 0
        session['IsWin'] = None
        session['Last_Call'] = None
        session['UserStartSession'] = True
        session['IsStarted'] = False

    Game = session.get('Game')
    PlayerSym = session.get('PlayerSym')
    IsWin = session.get('IsWin')
    Last_Call = session.get('Last_Call')
    IsStarted = session.get('IsStarted')


    if request.method == 'POST':

        if Last_Call != request.form:

            if request.form.get('X') == 'X':
                IsStarted = True
                PlayerSym = 1
                IsWin = None
                Game = [''] * 9

            elif request.form.get('O') == 'O':
                IsStarted = True
                PlayerSym = -1
                IsWin = None
                Game = [''] * 9
                AI_Choice = random.choice(range(9))
                Game[AI_Choice] = 'X'


            elif request.form.get('restart') == 'restart':
                IsStarted = False
                PlayerSym = 0
                Game = [''] * 9
                IsWin = None

            for i in range(9):
                IndexData = request.form.get(f'index {i}')
                if IndexData is not None:
                    if Game[int(i)] == '' and IsStarted:
                        if PlayerSym == 1:
                            Game[int(i)] = 'X'
                            if check_game(ConvertToPath(Game)):
                                IsWin = 'X Wins'
                                IsStarted = False
                                break
                            elif Game.count('') == 0:
                                IsWin = 'Draw'
                                IsStarted = False
                                break

                            AI_Choice = engine.Best(ConvertToPath(Game))
                            Game[AI_Choice] = 'O'

                            if check_game(ConvertToPath(Game)):
                                IsWin = 'O Wins'
                                IsStarted = False
                                break

                        elif PlayerSym == -1:
                            Game[int(i)] = 'O'
                            if check_game(ConvertToPath(Game)):
                                IsWin = 'O Wins'
                                IsStarted = False
                                break

                            AI_Choice = engine.Best(ConvertToPath(Game))
                            Game[AI_Choice] = 'X'

                            if check_game(ConvertToPath(Game)):
                                IsWin = 'X Wins'
                                IsStarted = False
                                break
                            elif Game.count('') == 0:
                                IsWin = 'Draw'
                                IsStarted = False
                                break

                        break

        Last_Call = request.form

    session['Game'] = Game
    session['PlayerSym'] = PlayerSym
    session['IsWin'] = IsWin
    session['Last_Call'] = Last_Call
    session['IsStarted'] = IsStarted

    return render_template('TicTacToePage.html', data=session.get('Game'), StartGame=IsStarted, IsWin=IsWin,user=NU)


@views.route('/Profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        Change_fn = request.form.get('firstName')
        Change_p1 = request.form.get('password1')
        Change_p2 = request.form.get('password2')
        if Change_fn:
            if len(Change_fn) > 1:
                current_user.first_name = Change_fn
                flash('name Changed !', 'success')
                db.session.commit()

        if Change_p1:
            if Change_p2:
                if len(Change_p1) <= 8:
                    flash('password is too short', 'error')
                elif Change_p1 != Change_p2:
                    flash('password not matched')
                else:
                    current_user.password = generate_password_hash(
                        Change_p1, method='sha256')
                    db.session.commit()
                    flash('Password Changed')
            else:
                flash('conform your password', 'error')

    return render_template("Profile.html", user=current_user, role=current_user.role, fn=current_user.first_name)


@views.route('/accept', methods=['GET', 'POST'])
@login_required
def accept():
    if current_user.role != 'Admin':
        flash('Not allowed', category='error')
        return render_template("home.html", user=current_user, role=current_user.role)

    if request.method == 'POST':
        AddUser = User.query.filter_by(email=request.form.get('AddUser'), role='Temp').first()
        DeclinesUser = User.query.filter_by(email=request.form.get('DeclinesUser'), role='Temp').first()
        if AddUser:
            AddUser.role = 'User'
            db.session.commit()
        if DeclinesUser:
            if DeclinesUser.email == 'admin@gmail.com':
                flash('Why ! are you hacker -_-', category='error')
            else:
                db.session.delete(DeclinesUser)
                db.session.commit()

    UserRequests = get_user_requests()

    return render_template("accept.html", user=current_user, role=current_user.role, requests=UserRequests)


@views.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    if current_user.role != 'Admin':
        flash('Not allowed', category='error')

        return render_template("home.html", user=current_user, role=current_user.role,
                               name=current_user.first_name)

    if request.method == 'POST':
        delete_user = User.query.filter_by(email=request.form.get('DeleteUser')).first()
        ChangeUserRoleToAdmin = request.form.get('ChangeUserRoleToAdmin')
        ChangeUserRoleToUser = request.form.get('ChangeUserRoleToUser')
        if delete_user:
            if delete_user.email == 'admin@gmail.com':
                flash('Why ! are you hacker -_-', category='error')
            else:
                db.session.delete(delete_user)
                db.session.commit()

        elif ChangeUserRoleToAdmin:
            ChangeUserRoleToAdmin = User.query.filter_by(id=ChangeUserRoleToAdmin).first()
            if ChangeUserRoleToAdmin.email == 'admin@gmail.com':
                flash('Why ! are you hacker ? -_-', category='error')
            else:
                ChangeUserRoleToAdmin.role = 'Admin'
                db.session.commit()

        elif ChangeUserRoleToUser:
            ChangeUserRoleToUser = User.query.filter_by(id=ChangeUserRoleToUser).first()
            if ChangeUserRoleToUser.email == 'admin@gmail.com':
                flash('Why ! are you hacker -_- ?', category='error')
            else:
                ChangeUserRoleToUser.role = 'User'
                db.session.commit()

    return render_template("user_list.html", user=current_user, users=User.query.all(), role=current_user.role,
                           name=current_user.first_name)


@views.route('/PublicChat', methods=['GET', 'POST'])
@login_required
def public_chat():
    if request.method == 'POST':
        if list(request.form.keys()).count('DeleteNote') == 1:
            delete_note(request.form.get('DeleteNote').split('_'), User.query.filter_by(email='Bot@gmail.com').first())
        else:
            note = request.form.get('note')
            if note:
                if len(note) < 1:
                    flash('Note is too short', category='error')
                else:

                    new_note = Note(data=f'{current_user.first_name} : {note}',
                                    user_id=User.query.filter_by(email='Bot@gmail.com').first().id)
                    db.session.add(new_note)

                    if len(Note.query.filter_by(user_id=4).all()) > 10:
                        db.session.delete(Note.query.filter_by(user_id=4).all()[0])
                    db.session.commit()
                    flash('Note added', category='success')

    return render_template("PublicChat.html", user=User.query.filter_by(email='Bot@gmail.com').first(),
                           role=current_user.role, name=current_user.first_name,
                           cr_user=len(current_user.first_name), cr_user_name=current_user)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if list(request.form.keys()).count('DeleteNote') == 1:
            delete_note(request.form.get('DeleteNote').split('_'), current_user)
        else:
            note = request.form.get('note')
            if note:
                if len(note) < 1:
                    flash('Note is too short', category='error')
                else:
                    new_note = Note(data=note, user_id=current_user.id)
                    db.session.add(new_note)
                    db.session.commit()
                    flash('Note added', category='success')

    return render_template("home.html", user=current_user, role=current_user.role, name=current_user.first_name)


def get_date(date):
    date = date.split(' ')
    y, m, d = date[0].split('-')
    h, mn, s = date[1].split(':')
    return int(y), int(m), int(d), int(h), int(mn), int(s)


def delete_note(note_data, user):
    y, m, d, h, mn, s = get_date(note_data[1])
    date = datetime(y, m, d, h, mn, s)
    note = note_data[0]
    IDs = Note.query.filter_by(data=note, user_id=user.id).all()
    for ID in IDs:
        if ID.date == date:
            db.session.delete(ID)
            db.session.commit()

    return render_template("home.html", user=user, name=current_user.first_name)

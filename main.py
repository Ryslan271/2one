import os

from flask import Flask, render_template, redirect
from models import db_session
from models.users import User, RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('sqlite.db')

f = False
men_page, reg, adm = None, None, None


@app.route("/")
def home():
    global f, adm
    return render_template('Osnova.html', flag=f, admi=adm, men=men_page)


@app.route("/Lyshee")
def lyshee():
    return render_template('Lyshee.html', men=men_page, flag=f)


@app.route("/O nas")
def onas():
    return render_template('O nas.html', men=men_page, flag=f)


@app.route("/Contact")
def contact():
    return render_template('Contact.html', men=men_page, flag=f)


@app.route("/girl")
def girl():
    global men_page, f
    men_page = False
    return render_template('Osnova.html', men=men_page, flag=f)


@app.route("/men")
def men():
    global men_page, f
    men_page = True
    return render_template('Osnova.html', men=men_page, flag=f)


@app.route("/Admin")
def admin():
    session = db_session.create_session()
    return render_template(
        'base2.html',
        User=session.query(User).order_by(User.date.desc())
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    global f, men_page, reg, adm
    reg = True
    form = LoginForm()
    if form.validate_on_submit():
        if form.login.data == 'adminrys':
            if form.password.data == '123':
                f, adm = True, True
                return render_template('Osnova.html', flag=f, admi=adm, men=men_page)
            else:
                return render_template('login.html', title='Регистрация',
                                       log=True,
                                       form=form,
                                       reg=reg,
                                       message="Ты не админ, куда хочешь а?")

        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():

            user = session.query(User).filter(User.login == form.login.data).first()
            if user and user.check_password(form.password.data):
                f = True
                return render_template('Osnova.html', flag=f, men=men_page)
            else:
                return render_template('login.html', title='Регистрация',
                                       log=True,
                                       form=form,
                                       reg=reg,
                                       message="Не правильный пароль")
        else:
            return render_template('login.html', title='Регистрация',
                                   log=True,
                                   form=form,
                                   reg=reg,
                                   message="Такого пользователя нету в базе данных, может зарегистрируешься?")

    return render_template('login.html', title='Авторизация', form=form, reg=reg,)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global f, reg
    reg = False
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   reg=reg,
                                   message="Пароли не совпадают")

        session = db_session.create_session()
        if session.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   reg=reg,
                                   message="Такой пользователь уже есть")
        if len(form.password.data) < 5 and len(form.login.data) < 5:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   reg=reg,
                                   message="Логин и пароль должны быть больше 5 символов")

        if len(form.password.data) < 5:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   reg=reg,
                                   message="Пароль слишком короткий, он должны быть больше 5 символов")
        if len(form.login.data) < 5:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   reg=reg,
                                   message="Логин слишком короткий, он должны быть больше 5 символов")

        user = User(
            login=form.login.data,
            hashed_password=form.password.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        f = True
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, reg=reg,)


@app.route('/delete_log', methods=['GET', 'POST'])
def delete_log():
    global f, men_page
    f = False
    men_page = None
    return render_template('Osnova.html', flag=f, admi=False)


@app.route('/delete_login', methods=['GET', 'POST'])
def delete_login():
    global f, men_page
    form = LoginForm()
    f = False
    men_page = None
    User.query.filter(User.id == form.id.data).delete()
    return render_template('Osnova.html', flag=f, admi=False)


if __name__ == '__main__':
    app.run('127.0.0.1', 7000, True)

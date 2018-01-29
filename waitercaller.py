from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from bitlyhelper import BitlyHelper
from mockdbhelper import MockDBHelper as DBHelper
from passwordhelper import PasswordHelper
from user import User
from forms import RegistrationForm, LoginForm, CreateTableForm, DeleteTableForm
import config
import datetime

application = Flask(__name__)
application.secret_key = \
    'FispAodSrTygWIwiHM+YcAhmCmxxjZmzdrWcfi4SgrqqSEzK1Fps1kqCo/YVvQ9Zdyi2mu+R8HSejUfE5Mw7vI8H7mxbPl4NXClQ'
login_manager = LoginManager(application)
DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()


@application.route("/")
def home():
    return render_template("home.html", loginform=LoginForm(), registrationform=RegistrationForm())


@application.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("Email or password invalid")
    return render_template("home.html", loginform=form, registrationform=RegistrationForm())


@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


@application.route("/register", methods=["POST"])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template('home.html', registrationform=form)
        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        DB.add_user(form.email.data, salt, hashed)
        return render_template("home.html", registrationform=form,
                               onloadmessage="Registration successful. Please log in.")
    return render_template("home.html", registrationform=form)


@application.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = "{}:{}".format((deltaseconds // 60), str(deltaseconds % 60).zfill(2))
    return render_template("dashboard.html", requests=requests)


@application.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id = request.args.get("request_id")
    DB.delete_request(request_id)
    return redirect(url_for('dashboard'))


@application.route("/account")
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template("account.html", createtableform=CreateTableForm(), tables=tables,
                           deletetableform=DeleteTableForm())


@application.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = BH.shorten_url(config.base_url + "newrequest/" + tableid)
        DB.update_table(tableid, new_url)
        return redirect(url_for('account'))

    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))


@application.route("/account/deletetable", methods=["POST"])
@login_required
def account_deletetable():
    form = DeleteTableForm(request.form)
    if form.validate():
        DB.delete_table(form.tablenumber.data)
        return redirect(url_for('account'))
    return render_template("account.html", createtableform=CreateTableForm(),
                           tables=DB.get_tables(current_user.get_id()),
                           deletetableform=form)


@application.route("/newrequest/<tid>")
def new_request(tid):
    DB.add_request(tid, datetime.datetime.now())
    return "Your request has been logged and a waiter will be with you shortly"


if __name__ == '__main__':
    application.run(port=5000, debug=True)

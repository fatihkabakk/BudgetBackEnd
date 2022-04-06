from flask import Flask, session, request
from sqlite_context import SqliteContext
from passlib.hash import sha512_crypt
from compress import Compress
from functools import wraps
import db_operations
from log import Log
import json
import os


class App(Flask):
    def process_response(self, response):
        response.headers['server'] = 'KlinzBlog'
        super(App, self).process_response(response)
        return response


app = App(__name__)
app.secret_key = os.urandom(16)

Compress(app)
Log(app)


def jsonify(needs_json=False):
    """ Wrapper to transform data into json.

    Also checks if the function needs json to perform.

    Args:
        needs_json (bool, optional): Checks if request contains json data. Defaults to False.
    """
    def main_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if needs_json and request.json is None:
                return {'message': 'Needs json'}
            return json.dumps(func(*args, **kwargs))
        return wrapper
    return main_wrapper


@app.route("/", endpoint='index')
@jsonify()
def index():
    return {'message': 'Hello, World!'}


@app.route('/post', methods=['POST'], endpoint='form_test')
@jsonify(needs_json=True)
def form_test():
    print(request.data, request.form, request.get_data(), request.json)
    return {'message': 'Ok'}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrapper


@app.route("/register", methods=["POST"], endpoint='register')
@jsonify
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha512_crypt.hash(form.password.data)

        query = "INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)"

        with SqliteContext() as cursor:
            cursor.execute(query, (name, email, username, password))

        flash(message="Başarıyla Kayıt Oldunuz...", category="success")

        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"], endpoint='login')
@jsonify
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        form_pass = form.password.data

        query = "SELECT * FROM users WHERE username = %s"

        with SqliteContext() as cursor:
            cursor.execute(query, (username, ))
            data = cursor.fetchone()

        if data and len(data) > 0:
            real_pass = data["password"]
            if sha512_crypt.verify(form_pass, real_pass):
                flash("Başarıyla Giriş Yaptınız. Yönlendiriliyorsunuz...",
                      category="success")

                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))

        flash(
            "Kullanıcı Adı Veya Şifreniz Hatalı! Lütfen Tekrar Deneyiniz...",
            category="danger")
        return redirect(url_for("login"))

    else:
        return render_template("login.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)

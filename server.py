from forms import RegisterForm, LoginForm
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha512_crypt
from core.validation import *
from compress import Compress
from functools import wraps
from core.cors import CORS
from os import urandom
from time import time
from log import Log
import jwt


class App(Flask):
    def process_response(self, response):
        response.headers['server'] = 'Budgee'
        response = super(App, self).process_response(response)
        return response


app = App(__name__)
app.secret_key = urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
Compress(app)
CORS(app)
Log(app)


# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150))

    def save(self, db: SQLAlchemy = db):
        db.session.add(self)
        db.session.commit()


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token', None)

        if not token:
            return ErrorResponse('Token is missing.'), 400

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = User.query\
                .filter_by(id=data['id'])\
                .first()
            return f(user, *args, **kwargs)
        except Exception:
            return ErrorResponse('Token is invalid'), 401

    return wrapper


def needs_json(func):
    ''' Checks if the request's json body is ok. '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.json is None:
            return ErrorResponse('Invalid json body.')
        return func(*args, **kwargs)
    return wrapper


@app.errorhandler(404)
def page_not_found(e):
    return ErrorResponse('Not found.'), 404


@app.errorhandler(400)
def bad_request(e):
    return ErrorResponse('Bad request'), 400


@app.route('/')
def index():
    return SuccessResponse('Index page.')


@app.route('/post', methods=['POST'])
def form_test():
    print(request.data, request.form, request.get_data(), request.json)
    return {'Data': str(request.data), 'Form': request.form, 'Get_Data': str(request.get_data()), 'JSON': request.json}
    return {'message': 'Ok'}


@app.route('/form', methods=['POST'])
def form():
    form = LoginForm(json_data=request.json, **request.form)
    if not form.validate():
        return ErrorResponse('Invalid form body'), 400
    return {'Username': form.username, 'Password': form.password}


@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm(json_data=request.json, **request.form)

    if not form.validate():
        return ErrorResponse('Invalid request body'), 400

    username = form.username
    password = sha512_crypt.hash(form.password)

    if User.query.filter_by(username=username).first():
        return ErrorResponse('User exists.'), 202

    user = User(username=username, password=password)
    user.save()
    return SuccessResponse('Successfully registered.'), 201


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(json_data=request.json, **request.form)

    if not form.validate():
        return ErrorResponse('Invalid form body'), 400

    username = form.username
    form_pass = form.password
    remember_me = form.rememberMe

    user = User.query.filter_by(username=username).first()
    if user:
        if sha512_crypt.verify(form_pass, user.password):
            add_exp = (24 * 3600) if not remember_me else (24 * 3600 * 7)
            token = jwt.encode({'exp': time() + add_exp,
                                'id': user.id, 'username': user.username
                                }, app.config['SECRET_KEY'])
            return SuccessDataResponse({'token': token}, 'Login successful.')
        return ErrorResponse('Debug[pass] Invalid credentials.')
    return ErrorResponse('Debug[user] Invalid credentials.')
    # if data and len(data) > 0:
    #     real_pass = data['password']
    #     if sha512_crypt.verify(form_pass, real_pass):
    #         pass


if __name__ == '__main__':
    app.run(debug=True)

from forms import RegisterForm, LoginForm, Form
from flask_sqlalchemy import SQLAlchemy
from core.utilities import ErrorHandler
from passlib.hash import sha512_crypt
from flask import Flask, request
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
        response = super(self.__class__, self).process_response(response)
        return response


app = App(__name__)
app.secret_key = 'supersecret'  # ! In production => urandom(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
ErrorHandler(app)
Compress(app)
CORS(app)
Log(app)


class CustomModel:
    noserialize = True
    def save(self, db: SQLAlchemy = db):
        db.session.add(self)
        db.session.commit()
    
    def delete(self, db: SQLAlchemy = db):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        """ Deep serializes SQLAlchemy Model instances. """
        if hasattr(self, 'serialize'):
            serialized = {}
            for i in self.serialize:
                obj = getattr(self, i)
                if isinstance(obj, CustomModel):
                    serialized[i] = obj.to_json()
                elif isinstance(obj, (tuple, list)):
                    new_iterable = []
                    for item in obj:
                        if isinstance(item, CustomModel):
                            item = item.to_json()
                        new_iterable.append(item)
                    serialized[i] = new_iterable
                else:
                    serialized[i] = obj
            return serialized       
        else:
            if getattr(self, 'noserialize'):
                return {}
            return self

group_members = db.Table('group_member', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),    
    db.Column('budgee_group_id', db.Integer, db.ForeignKey('budgee_group.id')),    
)

# Database ORMs
class User(db.Model, CustomModel):
    serialize = ('id', 'username')
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(150))

    joined_groups = db.relationship('BudgeeGroup', secondary=group_members, backref='members')
    owned_groups = db.relationship('BudgeeGroup', backref='owner')


class BudgeeGroup(db.Model, CustomModel):
    serialize = ('id', 'name', 'owner', 'members')
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


db.create_all()


"""
    ! Parent is Group, Child is the user
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child")

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
"""


def token_verifier(token) -> Response:
    try:
        data = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return SuccessDataResponse(data=data, message='Token is valid')
    except Exception:
        return ErrorResponse('Authentication token is invalid')


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token', None)

        if not token:
            return ErrorResponse('Token is missing.'), 400

        result = token_verifier(token)
        if not result.success:
            return result, 401

        user = User.query\
            .filter_by(id=result.data['id'])\
            .first()
        return f(user, *args, **kwargs)

    return wrapper


@app.route('/groups/list')
@token_required
def group_list_owned(current_user):
    groups = BudgeeGroup.query.filter_by(owner_id=current_user.id).all()
    if not groups:
        return ErrorResponse(message='You do not have any groups!'), 400
    return SuccessDataResponse(data=[group.to_json() for group in groups], message='Group list successful.')


@app.route('/groups/create', methods=['POST'])
@token_required
def group_create(current_user):
    group_name = request.json.get('name')
    group = BudgeeGroup(name=group_name, owner_id=current_user.id)
    group.owner = current_user
    group.members.append(current_user)
    group.save()
    return SuccessDataResponse(data=group, message='Group create successful.')


@app.route('/groups/delete', methods=['DELETE'])
@token_required
def group_delete(current_user):
    group_id = request.json.get('id')
    group = BudgeeGroup.query.filter_by(id=group_id, owner_id=current_user.id).first()
    if not group:
        return ErrorResponse(message='You do not have such a group!'), 400
    group.delete()
    return SuccessResponse(message='Group is deleted!')


@app.route('/grouptest')
@token_required
def group_test(current_user):
    test_group = BudgeeGroup(name='Maniacs', owner_id=current_user.id)
    test_group.owner = current_user
    test_group.members.append(current_user)
    test_group.save()
    return SuccessDataResponse(data=test_group, message='Group create successful.')


@app.route('/verify-token', methods=['POST'])
def verify_token():
    result = token_verifier(request.json.get('token'))
    if result.success:
        return result
    return result, 401


@app.route('/')
def index():
    return SuccessDataResponse(data=CustomModel(), message='Custom model')
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

    if User.query.filter_by(username=username).first():
        return ErrorResponse('User exists.'), 202

    password = sha512_crypt.hash(form.password)

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
                                }, app.config['SECRET_KEY'], algorithm='HS256')
            return SuccessDataResponse({'token': token}, 'Login successful.')
        return ErrorResponse('Debug[pass] Invalid credentials.')
    return ErrorResponse('Debug[user] Invalid credentials.')
    # if data and len(data) > 0:
    #     real_pass = data['password']
    #     if sha512_crypt.verify(form_pass, real_pass):
    #         pass


def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()

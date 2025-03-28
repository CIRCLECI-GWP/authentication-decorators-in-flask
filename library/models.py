from sqlalchemy.orm import backref
from flask import request, jsonify, make_response
from library.main import app, db
from functools import wraps
import jwt
from flask_restful import abort


# users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean)
    books = db.relationship('BookModel', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

# books table
class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    author = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def ___repr__(self):
        return '<Book {}>'.format(self.title)


# token decorator 
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('x-access-token')  # Simplified token retrieval
        if not token:  # Throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data.get('public_id')).first()
            if not current_user:  # Ensure the user exists
                return make_response(jsonify({"message": "User not found!"}), 404)
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({"message": "Token has expired!"}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Invalid token!"}), 401)

        return f(current_user, *args, **kwargs)
    return decorator
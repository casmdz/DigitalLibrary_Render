from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid 
from datetime import datetime
# from wtforms.validators  import DataRequired, Email, ValidationError

# Adding Flask Security for Passwords
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
# Imports for Login Manager
from flask_login import UserMixin
# Import for Flask Login
from flask_login import LoginManager
# Import for Flask-Marshmallow
from flask_marshmallow import Marshmallow

login_manager = LoginManager()
ma = Marshmallow()
db = SQLAlchemy()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=True)
    last_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)
    # image 
    image_file = db.Column(db.String, nullable = False, server_default = 'defaultuser.png')
    password = db.Column(db.String, nullable = False)
    g_auth_verify = db.Column(db.Boolean, default = False)
    token = db.Column(db.String, default = '', unique = True )
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    books = db.relationship('Book', backref='user', lazy=True)
    
    def __init__(self, username, first_name, last_name, email, image_file, password, token='', g_auth_verify=False):
        self.id = self.set_id()
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.image_file = image_file
        self.password = self.set_password(password)
        self.token = self.set_token(24)
        self.g_auth_verify = g_auth_verify
        
    def set_token(self, length):
        return secrets.token_hex(length)
    
    #set_id = unique # for PK 
    def set_id(self):
        return str(uuid.uuid4()) 
            
    # set_password generates a hash that makes it impossible for the database owner to see the actual password. 
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
        return self.pw_hash
    
    def __repr__(self):
        return f'Something just happened to {self.username} / {self.first_name} {self.last_name}, {self.image_file} in the void...'
        
class UserSchema(ma.Schema):
    class Meta:
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']
  
user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150))
    publishing = db.Column(db.String(250))
    format = db.Column(db.String(50))
    isbn = db.Column(db.String(50))
    genre = db.Column(db.String(150))
    imageSrc = db.Column(db.String(600))
    user_token = db.Column(db.String, db.ForeignKey('user.token'), nullable=False)
    
    def __init__(self, title, author, publishing, format, isbn, genre, imageSrc, user_token):
        # self.id = self.set_id()
        self.title = title
        self.author = author
        self.publishing = publishing
        self.format = format
        self.isbn = isbn
        self.genre = genre
        self.imageSrc = imageSrc
        self.user_token = user_token
        
    def __repr__(self):
        return f'{self.title} has been added to the library of {self.user_token}'
    
    def set_id(self):
        return (secrets.token_urlsafe())
    
class BookSchema(ma.Schema):
    class Meta:
        fields = ['id', 'title', 'author', 'publishing', 'format', 'isbn', 'genre', 'imageSrc']
        
book_schema = BookSchema()
books_schema = BookSchema(many=True)
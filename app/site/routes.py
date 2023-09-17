from flask import Blueprint, render_template, url_for, redirect, flash, request
from helpers import token_required
from flask_login import login_required, current_user
#  token_required,
from models import db, User, Book
from forms import UpdateUserForm


site = Blueprint('site', __name__, template_folder='site_templates')

@site.route('/')
def home():
    return render_template('index.html')

@site.route('/about')
def about():
    return render_template('about.html')


# @site.route('/bookshelf')
# @login_required  
# def bookshelf():
#     user_id = current_user.id
#     books = Book.query.filter_by(user_id=user_id).all()
#     print(books)
#     return render_template('bookshelf.html', books=books)

@site.route('/bookshelf')
@login_required  
def bookshelf(): 
    user_books = Book.query.filter_by(user_token=current_user.token).all()
    book_titles = [book.title for book in user_books]
    print(f'{current_user.username}\'s books: {book_titles}')
    return render_template('bookshelf.html', user_books=user_books)

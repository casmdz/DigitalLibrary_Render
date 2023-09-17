from flask import Blueprint, request, jsonify, render_template
from helpers import token_required
from models import db, User, Book, book_schema, books_schema

api = Blueprint('api',__name__, url_prefix='/api')

@api.route('/getdata')
def getdata():
    return {'yee': 'haw'}

#CREATE
@api.route('/books', methods=['POST'])
@token_required
def add_book(current_user_token):
        title = request.json['title']
        author = request.json['author']
        publishing = request.json['publishing']
        format = request.json['format']
        isbn = request.json['isbn']
        genre = request.json['genre']
        user_token = current_user_token.token
        
        print(f'{current_user_token.first_name} {current_user_token.token} just added a new book')
        
        book = Book(title, author, publishing, format, isbn, genre, user_token = user_token )
        
        db.session.add(book)
        db.session.commit()
        
        response = book_schema.dump(book)
        return jsonify(response)

# http://127.0.0.1:5000/
# {
# 		"title": ,
# 		"author": ,
# 		"publishing": ,
# 		"format": ,
# 		"isbn": ,
# 		"genre": ,
# 		"user_token":
# }    


@api.route('/books', methods = ['GET'])
#@token_required
def get_book():
    books = db.session.query(Book, User.first_name).join(User, Book.user_token == User.token).all()
    books_list = []
    for b, user_name in books:
            books_list.append({
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "publishing": b.publishing,
                    "format": b.format,
                    "isbn": b.isbn,
                    "genre": b.genre,
                    "bookworm": user_name,
            })
    return jsonify(books_list)

# SINGLE QUERY
@api.route('/books/<id>', methods=['GET'])
def get_single_book(id):
    book = Book.query.get(id)

    if book:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "publishing": book.publishing,
            "format": book.format,
            "isbn": book.isbn,
            "genre": book.genre,
            "user_token": book.user_token
        #     does that work???
        }
        return jsonify(book_data)
    else:
        return jsonify({"message": "Book not found"}), 404


# UPDATE BOOK
@api.route('/books/<id>', methods=['POST','PUT'])
@token_required

def update_book(current_user_token,id):
        if current_user_token is None:
                return jsonify({"message": "Authentication error: Invalid token"}), 401
        book = Book.query.get(id)
        if book is None:
                return jsonify({"message": "Book not found"}), 404
        book.title = request.json['title']
        book.author = request.json['author']
        book.publishing = request.json['publishing']
        book.format = request.json['format']
        book.isbn = request.json['isbn']
        book.genre = request.json['genre']
        
        db.session.commit()
        response = book_schema.dump(book)
        return jsonify(response)

# DELETE
@api.route('/books/<id>', methods=['DELETE'])
@token_required

def delete_book(current_user_token,id):
        book = Book.query.get(id)
        db.session.delete(book)
        db.session.commit()
        response = book_schema.dump(book)
        return jsonify(response, {"message": "Book deleted successfully"})
from flask import Blueprint, render_template, url_for, redirect, flash, request, jsonify

from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from models import User, db, check_password_hash
from forms import UserLoginForm, UserRegistrationForm, UpdateUserForm

from helpers import token_required
from models import user_schema, users_schema

import os 
import app
import secrets
from PIL import Image

from os.path import join, dirname, realpath
from flask import current_app



auth = Blueprint('auth', __name__, template_folder='auth_templates')

@auth.route('/toast')
def gettoast():
    return {'peanut butter': 'jelly time'}


@auth.route('/register', methods=['GET','POST'])
def register():
    form = UserRegistrationForm()
    try:
        if request.method == 'POST': 
            if form.validate_on_submit():
                first_name = form.first_name.data
                last_name = form.last_name.data
                username = form.username.data
                email = form.email.data
                password = form.password.data
                print(first_name, last_name, username, email, password, ' Successfully signed up')

                user = User(email=email, username=username, first_name=first_name, last_name=last_name, password=password, image_file='defaultuser.png')

                db.session.add(user)
                db.session.commit()
                
                print(f'You have successfully created a user account {username}', 'User-created')
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Please make sure to complete the entire form!', 'danger')
    except:
        raise Exception('Invalid Form Data: Please Check your Form')
    return render_template('register.html', form=form)
# Cas Mdz casmdz admincas@checkmeowt.org password  Successfully signed up


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            username_or_email = form.username_or_email.data
            password = form.password.data
            
            logged_user = User.query.filter((User.email == username_or_email) | (User.username == username_or_email)).first()
            
            if logged_user:
                if check_password_hash(logged_user.password, password):
                    login_user(logged_user)
                    print(f'{username_or_email} has successfully signed in to the library', 'auth-successful')
                    flash('You have been logged in!', 'success')
                    # from tutorial, 44:24
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('site.home'))
                else:
                    print(f' incorrect password for {username_or_email}', 'auth-failed')
                    flash('Incorrect password. Please try again.', 'danger')
        else:
            print('Credentials do not exist', 'auth-failed')
            flash('Login Unsuccessful. User does not exist', 'danger')

    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    print('User has logged out.', 'auth')
    return redirect(url_for('site.home'))



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics/', picture_fn)
    # app.root_path is the root folder of the project
    form_picture.save(picture_path)
    
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn
    


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateUserForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        print(f'{current_user} just updated their account')
        return redirect(url_for('auth.profile')) 
    # makes sure we dont submit another get request
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Account Profile', image_file=image_file, form=form)
    




@auth.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    user_list = []
    for u in users:
        user_list.append({
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'username': u.username,
            'email': u.email,
            'token': u.token
        })
    return jsonify(user_list)
#http://127.0.0.1:5000/users


# single user
@auth.route('/users/<id>', methods = ['GET'])
@token_required
def get_single_contact(current_user_token, id):
    user = User.query.get(id)
    response = user_schema.dump(user)
    if user is None:
         return jsonify({'message': 'User might not exist'}), 404
    return jsonify(response)
# http://127.0.0.1:5000/users/8fa3f086-4eb1-43a0-a4fe-4a29ba17a7b0
# x-access-token  Bearer ec3bb06541dfb1984914c78c1127214a89bc64a672ba8000


# Update
@auth.route('/users/<id>', methods=['POST','PUT'])
@token_required
def update_user(current_user_token,id):
    print(f'current user id: {id}')

    user = User.query.get(id)
    user.first_name = request.json['first_name']
    user.last_name = request.json['last_name']

    user.username = request.json['username']
    user.email = request.json['email']
    user.user_token = current_user_token.token
    
    db.session.commit()
    response = user_schema.dump(user)
    return jsonify(response)



@auth.route('/users/<id>', methods=['DELETE'])
@token_required
def delete_user(current_user_token,id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    response = user_schema.dump(user)
    return jsonify(response, {'message': 'User deleted successfully'})
from functools import wraps
import secrets
from flask import request, jsonify, json
import decimal
from json import JSONEncoder

from models import User

def token_required(our_flask_function):
    @wraps(our_flask_function)
    def decorated(*args, **kwargs):
        # https://www.geeksforgeeks.org/args-kwargs-python/
        token = None 
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token'].split(' ')[1]
            #Flask 4.2 Helpers.py 5min 
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            current_user_token = User.query.filter_by(token=token).first()
            print(token)
            print(current_user_token)
        except:
            owner = User.query.filter_by(token=token).first()
            
            if token != owner.token and secrets.compare_digest(token, owner.token):
                return jsonify({'message': 'Token is invalid'})
        return our_flask_function(current_user_token, *args, **kwargs)
    return decorated

class JSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(json.JSONEncoder, self).default(obj)

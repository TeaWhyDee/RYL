from flask import Blueprint

routes_test = Blueprint('test', __name__)

@routes_test.route('/ping')
def ping():
    return 'pong'
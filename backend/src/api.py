import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()
    try:
        drinks_formated = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_formated
        })
    except Exception as e:
        print(e)
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    try:

        drinks_formated = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_formated
        })
    except Exception as e:
        print(e)
        abort(500)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):

    body = request.get_json()
    req_title = body.get('title', None)
    req_recipe = body.get('recipe', None)
    try:
        req_recipe_list = []
        if isinstance(req_recipe, dict):
            req_recipe_list.append(req_recipe)
            drink = Drink(title=req_title, recipe=json.dumps(req_recipe_list))
        else:
            drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink.insert()

        drinks = Drink.query.all()
        drinks_formated = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": drinks_formated

        })
    except Exception as e:
        print(e)
        abort(500)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    body = request.get_json()
    req_title = body.get('title', None)
    # req_recipe = body.get('recipe', None)

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.title = req_title
        # drink.recipe = json.dumps(req_recipe)
        drink.update()

        drinks = []
        drinks.append(drink.long())
        return jsonify({
            "success": True,
            "drinks": drinks
        })

    except Exception as e:
        print(e)
        abort(500)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })

    except Exception as e:
        print(e)
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    return jsonify({
        "success": False,
        "error": ex.status_code,
        "message": ex.error
    }), ex.status_code

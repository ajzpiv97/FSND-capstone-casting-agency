import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movies, Actors, db

from auth import AuthError, requires_auth

from datetime import datetime


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Endpoints

    @app.route('/movies', methods=['GET'])
    @requires_auth('read:movies')
    def get_movies(payload):
        movies = Movies.query.all()
        movies = [movie.format() for movie in movies]

        return jsonify({
            "success": True,
            "movies": movies
        })

    @app.route('/actors', methods=['GET'])
    @requires_auth('read:actors')
    def get_actors(payload):
        actors = Actors.query.all()
        actors = [actor.format() for actor in actors]

        return jsonify({
            "success": True,
            "actors": actors
        })

    @app.route('/actors/<int:id>', methods=['GET'])
    @requires_auth('read:actors')
    def get_specific_actor(payload, id):
        actor = Actors.query.get(id)

        if actor is None:
            abort(404)

        return jsonify({
            "success": True,
            "actor": actor.format()
        })

    @app.route('/movies/<int:id>', methods=['GET'])
    @requires_auth('read:movies')
    def get_specific_movie(payload, id):
        movie = Movies.query.get(id)

        if movie is None:
            abort(404)

        return jsonify({
            "success": True,
            "movie": movie.format()
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def post_movie(payload):
        body = request.get_json()

        if not ('title' in body and 'release_date' in body):
            abort(422)

        new_title = body.get('title', None)
        new_release_date = body.get('release_date', None)

        if new_title is None or new_release_date is None:
            abort(400)

        try:
            movie = Movies(title=new_title, release_date=new_release_date)
            if Movies.query.filter_by(title=movie.title).count():
                abort(409)
            movie.insert()

            return jsonify({
                'success': True,
                'movie': movie.format(),
                'total_movies': len(Movies.query.all())
            })

        except AttributeError:
            abort(422)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def post_actor(payload):
        body = request.get_json()

        if not ('name' in body and 'age' in body, 'gender' in body and 'movie' in body):
            abort(422)

        new_name = body.get('name', None)
        new_age = body.get('age', None)
        new_gender = body.get('gender', None)
        new_movie = body.get('movie', None)

        if new_name is None or new_age is None or new_gender is None:
            abort(400)

        try:
            actor = Actors(name=new_name, age=new_age, gender=new_gender, movie_id=new_movie)
            if Actors.query.filter_by(name=actor.name).count():
                abort(409)
            actor.insert()

            return jsonify({
                'success': True,
                'actor': actor.format(),
                'total_actors': len(Actors.query.all())
            })

        except AttributeError:
            abort(422)

    @app.route('/movies/<int:id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(payload, id):
        movie = Movies.query.filter(Movies.id == id).one_or_none()
        if movie is None:
            abort(404)
        try:
            movie.delete()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            'success': True,
            'deleted': movie.id
        })

    @app.route('/actors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(payload, id):
        actor = Actors.query.filter(Actors.id == id).one_or_none()
        if actor is None:
            abort(404)
        try:
            actor.delete()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            'success': True,
            'deleted': actor.id
        })

    @app.route('/movies/<int:id>', methods=['PATCH'])
    @requires_auth('update:movies')
    def update_movie(payload, id):
        movie = Movies.query.get(id)

        if movie is None:
            abort(404)

        data = request.get_json()

        if 'title' in data:
            movie.title = data.get('title')

        if 'release_date' in data:
            movie.release_date = data.get('release_date')
        try:
            movie.update()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            'success': True,
            'movie': movie.format()
        })

    @app.route('/actors/<int:id>', methods=['PATCH'])
    @requires_auth('update:actors')
    def update_actor(payload, id):
        actor = Actors.query.get(id)

        if actor is None:
            abort(404)

        data = request.get_json()

        if 'name' in data:
            actor.name = data.get('name')

        if 'age' in data:
            actor.age = data.get('age')

        if 'gender' in data:
            actor.gender = data.get('gender')

        if 'movie_id' in data:
            actor.movie_id = data.get('movie_id')

        try:
            actor.update()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({
            'success': True,
            'actor': actor.format()
        })

    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method is not allowed"
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": 'Internal Server Error'
        }), 500

    @app.errorhandler(409)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 409,
            "message": 'Duplicate resource'
        }), 409

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

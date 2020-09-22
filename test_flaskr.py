import unittest
from flask_sqlalchemy import SQLAlchemy
import json
from flaskr import create_app
from models import setup_db, Movies, Actors


class CastingTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "casting_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)

        setup_db(self.app, database_path=self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.movie = {
            "title": "Black Panther",
            "release_date": "2018-02-16 "
        }

        self.actor = {
            "name": "Chadwick Boseman",
            "age": 42,
            "gender": 'M',
            "movie_id": 7
        }

        # Set up authentication tokens info
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())

        assistant_jwt = self.auth["roles"]["Casting Assistant"]["jwt_token"]
        director_jwt = self.auth["roles"]["Casting Director"]["jwt_token"]
        producer_jwt = self.auth["roles"]["Executive Producer"]["jwt_token"]
        self.auth_headers = {
            "Casting Assistant": 'Bearer {}'.format(assistant_jwt),
            "Casting Director": 'Bearer {}'.format(director_jwt),
            "Executive Producer": 'Bearer {}'.format(producer_jwt)
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["movies"]), type([]))

    def test_get_specific_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies/5', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/actors', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

    def test_get_specific_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies/5', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_get_actors_by_casting_director(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().get('/actors', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

    def test_get_actor_fail_401_no_header(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), type(""))

    def test_get_actor_fail_404(self):

        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().get('/actors/100', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data["message"], "resource not found")

    def test_post_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().post('/movies',
                                 json=self.movie, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_movies_fail_422(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        missing_parameter = {"title": "Movie"}
        res = self.client().post('/movies',
                                 json=missing_parameter, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "unprocessable")

    def test_post_movies_fail_403_missing_permission(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        missing_parameter = {"title": "Movie"}
        res = self.client().post('/movies',
                                 json=missing_parameter, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_post_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().post('/actors',
                                 json=self.actor, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_actors_fail_400(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        missing_parameter = {"name": "Actor"}
        res = self.client().post('/actors',
                                 json=missing_parameter, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "bad request")

    def test_create_actors_fail_403_missing_permission(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        missing_parameter = {"name": "Actor"}
        res = self.client().post('/actors',
                                 json=missing_parameter, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().delete('/movies/1', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 1)

        res = self.client().get('/movies/1', headers=header_obj)

        self.assertEqual(res.status_code, 404)

    def test_delete_movie_fail_404_not_found(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().delete(f'/movies/100', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_movie_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().delete('/movies/3', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_delete_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().delete('/actors/4', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], 4)

        res = self.client().get('/actors/4', headers=header_obj)

        self.assertEqual(res.status_code, 404)

    def test_delete_actor_fail_404_not_found(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        res = self.client().delete(f'/actors/100', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_actor_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().delete('/actors/3', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_update_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }

        new_title = "Flight Club 2"
        res = self.client().patch(
            '/movies/2',
            json={
                'title': new_title},
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['movie']['id'], 2)
        self.assertEqual(data['movie']['title'], new_title)

    def test_update_movie_fail_404_not_found(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }

        res = self.client().patch(
            '/movies/1000',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_update_movie_fail_403_failed_permission(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }

        res = self.client().patch(
            '/movies/1000',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    def test_update_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        new_name = "Tom Hanks Sr"
        new_movie = 5
        res = self.client().patch(
            '/actors/1',
            json={
                'name': new_name,
                'movie_id': new_movie},
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['actor']['id'], 1)
        self.assertEqual(data['actor']['name'], new_name)
        self.assertEqual(data['actor']['movie_id'], new_movie)

    def test_update_actor_fail_404_not_found(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }

        res = self.client().patch(
            '/actors/1000',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_update_actor_fail_403_failed_permission(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }

        res = self.client().patch(
            '/actors/1000',
            headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)

    # Make the tests conveniently executable


if __name__ == "__main__":
    unittest.main()

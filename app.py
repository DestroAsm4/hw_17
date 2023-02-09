# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace('movies')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return '', 404
        return movie_schema.dump(movie), 200


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        stmt = Movie.query
        if director_id:
            stmt = stmt.filter(Movie.director_id == director_id)
        if genre_id:
            stmt = stmt.filter(Movie.genre_id == genre_id)

        movie = stmt.all()
        return movie_schema.dump(movie, many=True), 200


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreScheme(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
genre_schema = GenreScheme()


@movie_ns.route('/directors/')
class DirectorsViews(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return director_schema.dump(all_directors, many=True), 200


@movie_ns.route('/director/<int:did>')
class DirectorViews(Resource):

    def get(self, did: int):
        director = db.session.query(Director).filter(Director.id == did).one()
        return director_schema.dump(director), 200

    def post(self, did: int):
        response = request.json
        director = Director(**response)
        db.session.add(director)
        db.session.commit()
        return 'Creating director', 201

    def put(self, did: int):
        director = db.session.query(Director).get(did)
        req_json = request.json

        director.name = req_json.get('name')

        db.session.add(director)
        db.session.commit()

        return 'Update director', 204

    def delete(self, did: int):
        director = db.session.query(Director).get(did)

        db.session.delete(director)
        db.session.commit()

        return 'Deleted director', 204


@movie_ns.route('/genres/')
class GenresViews(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return director_schema.dump(all_genres, many=True), 200


@movie_ns.route('/genre/<int:gid>')
class GenreViews(Resource):

    def get(self, gid: int):
        genre = db.session.query(Genre).filter(Genre.id == gid).one()
        return genre_schema.dump(genre), 200

    def post(self, gid: int):
        response = request.json
        genre = Genre(**response)
        db.session.add(genre)
        db.session.commit()
        return 'Creating genre', 201

    def put(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json

        genre.name = req_json.get('name')

        db.session.add(genre)
        db.session.commit()

        return 'Update genre', 204

    def delete(self, gid: int):
        genre = db.session.query(Genre).get(gid)

        db.session.delete(genre)
        db.session.commit()

        return 'Deleted genre', 204


if __name__ == '__main__':
    app.run(debug=True)

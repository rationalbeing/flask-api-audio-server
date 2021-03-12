import os

from datetime import datetime
from json import loads as json_loader

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow  # parse model object(s) into a JSON response
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from variables import *



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

AUDIO_FILE_DIR = os.getcwd() + '/audio_files' 




## INITIALIZING MODELS
## --------------------------------------


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    uploaded_time = db.Column(db.DateTime)



class SongSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'duration', 'uploaded_time')
        model = Song



song_schema = SongSchema()
songs_schema = SongSchema(many=True)



class Podcast(db.Model):
    __tablename__ = 'podcasts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    uploaded_time = db.Column(db.DateTime)
    host = db.Column(db.String(50))
    participants = db.Column(db.Text)



class PodcastSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'duration', 'uploaded_time', 'host', 'participants')
        model = Podcast



podcast_schema = PodcastSchema()
podcasts_schema = PodcastSchema(many=True)



class AudioBook(db.Model):
    __tablename__ = 'audiobooks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(50))
    narrator = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    uploaded_time = db.Column(db.DateTime)



class AudioBookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'narrator', 'duration', 'uploaded_time')
        model = AudioBook



audiobook_schema = AudioBookSchema()
audiobooks_schema = AudioBookSchema(many=True)






## SCRIPTING VIEWS
## ------------------------------------------------------


def response_handler(code):
    if code == 200:
        resp = jsonify({'message' : 'Action is Successful'})
    elif code == 400:
        resp = jsonify({'message' : 'The request is invalid'})
    elif code == 500:
        resp = jsonify({'message' : 'Server Error'})
    else:
        return
    resp.status_code = code
    return resp



class CreateAudioFiles(Resource):
    def post(self):

        if ('audioFile' not in request.files):
            return response_handler(400)

        audio_file = request.files['audioFile']
        request_args = request.values
        audio_file_type = request_args.get('audioFileType')
        audio_meta = json_loader(request_args['audioFileMetadata'])

        filename = secure_filename(audio_file.filename)
        audio_file.save(os.path.join(AUDIO_FILE_DIR, filename))

        if audio_file_type in ['song', 'podcast', 'audiobook']:

            if audio_file_type == 'song':
                new_song = Song(
                        title=audio_meta.get('title'),
                        duration=audio_meta.get('duration'),
                        uploaded_time=datetime.now()
                    )
                db.session.add(new_song)

            if audio_file_type == 'podcast':
                new_podcast = Podcast(
                        title=audio_meta.get('title'),
                        duration=audio_meta.get('duration'),
                        uploaded_time=datetime.now(),
                        host=audio_meta.get('duration')
                    )
                db.session.add(new_podcast)

            if audio_file_type == 'audiobook':
                new_audiobook = AudioBook(
                        title=audio_meta.get('title'),
                        author=audio_meta.get('author'),
                        narrator=audio_meta.get('narrator'),
                        duration=audio_meta.get('duration'),
                        uploaded_time=datetime.now(),
                    )
                db.session.add(new_audiobook)


            db.session.commit()
            return response_handler(200)
        else:
            return response_handler(500)



class RetrieveSingleAudioFile(Resource):
    def get(self, slug, id):
        if slug == 'song':
            song = Song.query.get_or_404(id)
            return song_schema.dump(song)

        elif slug == 'podcast':
            podcast = Podcast.query.get_or_404(id)
            return podcast_schema.dump(podcast)

        elif slug == 'audiobook':
            audiobook = AudioBook.query.get_or_404(id)
            return audiobook_schema.dump(audiobook)

        else:
            response_handler(404)



class RetrieveAllAudioFile(Resource):
    def get(self, slug):
        if slug == 'song':
            song = Song.query.all()
            return songs_schema.dump(song)

        elif slug == 'podcast':
            podcast = Podcast.query.all()
            return podcasts_schema.dump(podcast)

        elif slug == 'audiobook':
            audiobook = AudioBook.query.all()
            return audiobooks_schema.dump(audiobook)

        else:
            response_handler(404)



class UpdateAudioFile(Resource):
    def patch(self, slug, id):
        request_args = request.values
        audio_file_type = request_args.get('audioFileType')
        audio_meta = json_loader(request_args['audioFileMetadata'])
        audio_meta_keys = audio_meta.keys()

        if slug == 'song':
            song = Song.query.get_or_404(id)
            if 'title' in audio_meta_keys:
                song.title = audio_meta['title']
            if 'duration' in audio_meta_keys:
                song.duration = audio_meta['duration']

        elif slug == 'podcast':
            podcast = Podcast.query.get_or_404(id)
            if 'title' in audio_meta_keys:
                podcast.title = audio_meta['title']
            if 'duration' in audio_meta_keys:
                podcast.duration = audio_meta['duration']
            if 'host' in audio_meta_keys:
                podcast.host = audio_meta['host']
            if 'participants' in audio_meta_keys:
                podcast.participants = audio_meta['participants']


        elif slug == 'audiobook':
            audiobook = AudioBook.query.get_or_404(id)
            if 'title' in audio_meta_keys:
                audiobook.title = audio_meta['title']
            if 'duration' in audio_meta_keys:
                audiobook.duration = audio_meta['duration']
            if 'author' in audio_meta_keys:
                audiobook.author = audio_meta['author']
            if 'narrator' in audio_meta_keys:
                audiobook.narrator = audio_meta['narrator']
        else:
            response_handler(400)


        db.session.commit()
        return response_handler(200)


        

class DeleteAudioFile(Resource):
    def delete(self, slug, id):
        if slug == 'song':
            audiofile = Song.query.get_or_404(id)
        elif slug == 'podcast':
            audiofile = Podcast.query.get_or_404(id)
        elif slug == 'audiobook':
            audiofile = AudioBook.query.get_or_404(id)
        else:
            return response_handler(400)

        db.session.delete(audiofile)
        db.session.commit()

        return response_handler(200)



api.add_resource(CreateAudioFiles, '/create')
api.add_resource(RetrieveSingleAudioFile, '/get/<slug>/<int:id>')
api.add_resource(RetrieveAllAudioFile, '/get/<slug>')
api.add_resource(UpdateAudioFile, '/patch/<slug>/<int:id>')
api.add_resource(DeleteAudioFile, '/delete/<slug>/<int:id>')


db.create_all()


if __name__ == '__main__':
    if not os.path.exists(AUDIO_FILE_DIR):
        os.mkdir(AUDIO_FILE_DIR)

    app.run(debug=True)

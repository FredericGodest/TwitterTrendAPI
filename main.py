import tweet
from flask import Flask, jsonify, json
from flask_restful import Resource, Api
import os
from dotenv import dotenv_values

app = Flask(__name__)
api = Api(app)

class GetTweet(Resource):
    def get(self, hashtag, nbitem):
        d = tweet.main("Rouen", nbitem)
        d["hashtag"] = "#" + str(hashtag)
        return jsonify(d)

api.add_resource(GetTweet, '/<string:hashtag>/<int:nbitem>')

if __name__ == '__main__':
    if os.environ.get("ENV") == "PROD":
        app.run(debug=False)
    else:
        app.run(debug=True)
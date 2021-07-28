import tweet
from flask import Flask, jsonify
from flask_restful import Resource, Api
import os
from flask_cors import CORS
from dotenv import dotenv_values

app = Flask(__name__)
CORS(app)
api = Api(app)

class GetTweet(Resource):
    def get(self, hashtag):
        if os.environ.get("ENV") == "PROD":
            d = tweet.main(hashtag, 100)
        else:
            d = tweet.main(hashtag, 40)

        d["hashtag"] = "#" + str(hashtag)
        return jsonify(d)

api.add_resource(GetTweet, '/<string:hashtag>')

if __name__ == '__main__':
    if os.environ.get("ENV") == "PROD":
        app.run(debug=False)
    else:
        app.run(debug=True)
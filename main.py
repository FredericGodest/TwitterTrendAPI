"""
This is the main module for running Flask Rest API
"""

import tweet
from flask import Flask, jsonify
from flask_restful import Resource, Api
import os
from flask_cors import CORS
from dotenv import dotenv_values
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Initialisation + CORS Package
app = Flask(__name__)
CORS(app)
api = Api(app)

# Initilisation des tokens hugging face
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

class GetTweet(Resource):
    def get(self, hashtag : str) -> dict:
        """
        This is the function that the main function of the tweet.py module.
        :param hashtag: The hashtag searched by the user
        :return d: Json object
        """
        # Checking Environement
        if os.environ.get("ENV") == "PROD":
            d = tweet.main(hashtag, tokenizer, model, 30)
        else:
            d = tweet.main(hashtag, tokenizer, model, 30)

        d["hashtag"] = "#" + str(hashtag)
        return jsonify(d)

api.add_resource(GetTweet, '/<string:hashtag>')

# Main function to run Flask rest API
if __name__ == '__main__':
    # Checking Environement
    if os.environ.get("ENV") == "PROD":
        app.run(debug=False)
    else:
        app.run(debug=True)
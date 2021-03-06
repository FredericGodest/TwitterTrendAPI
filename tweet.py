"""
This module is compiling data from twitter API.
The data is then cleaned and analysed.
"""

# librairies
import tweepy
import pandas as pd
import re
import numpy as np
import json
import os
from sentiment_analysis_torch import sentiment_analysis
from dotenv import dotenv_values
from googletrans import Translator

translator = Translator()

def get_auth() -> object:
    """
    function to obtain credentials
    :return: Twitter API credentials
    """
    # PROD MOD
    if os.environ.get("ENV") == "PROD":
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        access_token = os.environ.get("ACCESS_TOKEN")
        access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

    # TEST MOD
    else:
        all_keys = open("twitterauth", "r").read().splitlines()
        auth = tweepy.OAuthHandler(all_keys[0], all_keys[1])
        auth.set_access_token(all_keys[2], all_keys[3])

    api = tweepy.API(auth)

    return api

def get_cleaned(msg : str) -> str:
    """
    This function use regex function to clean up a message.
    :param: The given message (string)
    :return: cleaned message (string)
    """
    #remove # and @
    msg = re.sub("@[A-Za-z0-9_]+", "", msg)
    msg = msg.replace('#', '')

    # remove urls
    msg = re.sub(r"http\S+", "", msg)

    # symbols & pics & emoji
    EMOJI_PATTERN = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])"
    )
    msg = re.sub(EMOJI_PATTERN, '', msg)

    return msg

def get_tweet(tokenizer, model, word : str, item_number : int, api : object) -> dict:
    """
    This function use the twitter API to find all the tweets related to a given hashtag.
    :param word: the hashtag searched by the user
    :param item_number: the numbers of tweets requested by the user
    :param api: Twitter API credentials

    :return data: a Pandas dataframe with a bunch of data.
    """

    #Variable Creation
    TWEETS = []
    USER = []
    FAV = []
    RT = []
    ORIGIN = []
    POLARITY = []
    ORIGIN_NAME = []

    # Get tweets from API
    tweets = tweepy.Cursor(api.search, q=word, lang="fr", tweet_mode='extended').items(item_number)

    # get data
    for tweet in tweets:
        RT.append(int(tweet.retweet_count))
        USER.append(str(tweet.user.screen_name))

        if hasattr(tweet, 'retweeted_status'):
            origin = tweet.retweeted_status.author.screen_name
            origin_name = tweet.retweeted_status.author.name
            favorite = tweet.retweeted_status.favorite_count
            tweet = str(tweet.retweeted_status.full_text)

        else:
            origin = str(tweet.author.screen_name)
            origin_name = tweet.author.name
            favorite = tweet.favorite_count
            tweet = str(tweet.full_text)



        #Get it cleaned
        msg = get_cleaned(tweet)

        #Translation to english
        msg = translator.translate(msg, dest='en').text

        #sentiment analysis
        polarity = sentiment_analysis(tokenizer, model, msg)

        # Compile data in list
        POLARITY.append(polarity)
        ORIGIN.append(origin)
        FAV.append(int(favorite))
        TWEETS.append(str(tweet))
        ORIGIN_NAME.append(str(origin_name))

    # Dictionnarie Creation
    d = {"Username" : USER,
         "Origin" : ORIGIN,
         "Origin Name" : ORIGIN_NAME,
         "Message" : TWEETS,
         "Favorite Number": FAV,
         "RT Number": RT,
         "Sentiment": POLARITY}

    # Daframe Creation
    data = pd.DataFrame(data = d).drop_duplicates("Message")

    return data

def remove_dark(df : dict) -> dict:
    """
    This function remove all the tweets which are not suitable for our application.
    :param df: uncleaned dataframe
    :return df: Clean dataframe
    """
    # Open the Black list
    file = open("blacklist.txt", "r")
    List = []
    for line in file:
        stripped_line = line.strip()
        line_list = stripped_line.split()
        List.append(line_list)

    blackList = []
    [blackList.append(List[i][0]) for i in range(0, len(List))]
    blackListExtended = []

    for word in blackList:
        blackListExtended.append(word)
        blackListExtended.append(word.upper())
        blackListExtended.append(word.capitalize())

    for word in blackListExtended:
        df = df[df["Message"].str.contains(word)==False]

    return df

def toJson(data : dict) -> dict:
    """
    This function convert the pandas dataframe to a lighweight json object.
    :param data: Pandas dataframe
    :return d: Dataframe on Json format
    """
    data["Reaction"] = data["RT Number"] + data["Favorite Number"]
    SCORE = data["Sentiment"].to_numpy()
    REACTION = data["Reaction"].to_numpy()

    data = remove_dark(data)

    RT = data["RT Number"].to_numpy()
    FAV = data["Favorite Number"].to_numpy()
    max_fav = int(np.max(FAV))
    max_RT = int(np.max(RT))
    total_fav = int(np.sum(FAV))
    total_RT = int(np.sum(RT))
    final_score = float(np.average(SCORE, weights=REACTION))

    #Getting best Tweet
    data = data.sort_values(by='Reaction', ascending=False).head(1)
    best_account = str(data["Origin"].values[0])
    best_account_name = str(data["Origin Name"].values[0])
    best_tweet = str(data["Message"].values[0])
    best_fav = int(data["Favorite Number"].values[0])
    best_RT = int(data["RT Number"].values[0])
    best_sentiment = float(data["Sentiment"].values[0])


    d = {
        "best_account": best_account,
        "best_account_name" : best_account_name,
        "best_tweet": best_tweet,
        "best_fav": best_fav,
        "best_sentiment": best_sentiment,
        "best_RT": best_RT,
        "max_fav": max_fav,
        "max_RT": max_RT,
        "total_fav": total_fav,
        "total_RT": total_RT,
        "final_score": final_score
    }

    return d

def main(word : str,  tokenizer, model, item_number : int) -> dict:
    """
    This is the main function that run all the functions above.
    :param word: the hashtag searched by the user
    :param item_number: the numbers of tweets requested by the user
    :return d: json object
    """
    word = word.replace('#', '')
    word = '#' + str(word)
    api = get_auth()
    data = get_tweet(tokenizer, model, word, item_number, api)
    d = toJson(data)

    return d



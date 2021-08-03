import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from googletrans import Translator

translator = Translator()

model_name = "distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def sentiment_analysis(tokenizer : any, model : any, msg : str) -> int:
    """ Getting sentiment analysis with pytorch and transformers.
    :param msg = tweet message in str
    :return score = score between 1 and 5"""

    msg = translator.translate(msg, dest='en').text
    tokens = tokenizer.encode(msg, return_tensors='pt')
    result = model(tokens)
    score = int(torch.argmax(result.logits))
    print(result, score)

    return result

msg = "Ce film était vraiment sympa !"
sentiment_analysis(tokenizer, model, msg)
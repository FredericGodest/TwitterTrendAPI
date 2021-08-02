"""
This module is a sentiment analyse model based on bert-base-multilingual-uncased-sentiment available on hugging face.
This module is using pytorch.
"""

import torch

def sentiment_analysis(tokenizer : any, model : any, msg : str) -> int:
    """ Getting sentiment analysis with pytorch and transformers.
    :param msg = tweet message in str
    :return score = score between 1 and 5"""

    tokens = tokenizer.encode(msg, return_tensors='pt')
    result = model(tokens)
    score = int(torch.argmax(result.logits)) + 1

    return score




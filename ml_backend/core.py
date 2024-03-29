import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import nltk
import requests

#Cleaning the input to get tags
def get_tags(input):
    #Downloading the required libraries for nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    tokenized_word=word_tokenize(input)
    stop_words=set(stopwords.words("english"))
    filtered_sent=[]
    for w in tokenized_word:
        if w not in stop_words:
            filtered_sent.append(w)
    return filtered_sent

#Requesting the StackExchange API for questions using the tags obatained
def get_questions(tags):
    URL = 'https://api.stackexchange.com/2.2/questions?order=asc&sort=activity&tagged=python%3Bfunction%3Bdefinition&site=stackoverflow'
    r = requests.get(url = URL)
    data = r.json()
    messages = []
    for item in data['items']:
        messages.append(item['title'])
    return messages

#Converting sentences to embeddings and computing the inner product to calculate similarity
def get_similarity(messages):
    # Downloading the pre-trained "Universal Sentence Encoder" from tensorflow hub
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/2" 
    embed = hub.Module(module_url)
    similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
    similarity_message_encodings = embed(similarity_input_placeholder)
    with tf.Session() as session:
        session.run(tf.global_variables_initializer())
        session.run(tf.tables_initializer())
        message_embeddings = session.run(similarity_message_encodings, feed_dict={similarity_input_placeholder: messages})
        per = np.inner(message_embeddings, message_embeddings[-1:])

    # Sorting the results according to similarity"""
    dictItems = []
    i = 0
    for i in range(0, len(per)-1 ):
        temp = { "probability" : per.item(i), "title" : messages[i] }
        dictItems.append(temp)

    sortedSearch = sorted(dictItems, key = lambda i: i['probability'], reverse = True)

    # returning the top 5 results
    top = []
    for i in range(0,5):
        top.append(sortedSearch[i].get("title"))
    return top
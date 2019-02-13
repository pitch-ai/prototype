# Takes in a text string and outputs the understanding of the audience:
# {
#   "categories": ["/technology and computing/internet technology"], 
#   "concepts": ["Copyright", "Copyright infringement"], 
#   "emotions": "sadness", 
#   "keywords": ["Copyright Act", "copyright violation"], 
#   "sentiment": "negative"
# }

from urllib import request, parse, error
import json
import base64
import requests

text_example = "While the Internet offers all sorts of music, movies, apps and software, many of them aren’t really meant to be given away for free. If you download those off Torrent sites and other similar services it could be they are condemned as part of Digital Piracy. According to the Copyright Act, Digital Piracy can be “a copyright violation to download, upload, or distribute copyrighted material through the Internet without having authorization.” FBI calls it stealing since it robs people of their ideas, inventions, and creative expressions. But, is Digital Piracy really that bad? According to a recent study conducted by Cammerts, Mansell, and Meng from the London School of Economics and Political Science (LSE) digital piracy isn’t really that bad. In fact, they may even be helpful to the entertainment industry."
api_key = 'Dx5l75uQ8lQC7bW3lwIYcpMmRsI46kKnlDWVme_8xqSs'
service_endpoint = 'https://gateway-wdc.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2018-11-16'
token_endpoint = 'https://iam.bluemix.net/identity/token'
speech_to_text_endpoint = 'https://gateway-wdc.watsonplatform.net/speech-to-text/api/recognize'
features = {'categories': {},
            'concepts': {},
            'emotion': {},
            'entities':{},
            'keywords': {},
            'sentiment': {}} #all options: ['categories','concepts','emotion','entities','keywords','metadata','relations','semantic_roles','sentiment']
concept_relevance_threshold = .8
keyword_relevance_threshold = .8
category_relevance_threshold = .9
emotion_score_threshold = .65

def perception(text):

    data = {'features': features, 'text': text}
    response = requests.post(url=service_endpoint, json=data, headers={'Authorization':'Bearer ' + get_access_token()})
    if response.ok:
        print(response.text)
        print("")
    else:
        print("error")
        print(response.content)

    content = json.loads(response.content.decode())

    print('Overall Sentiment: ' + content['sentiment']['document']['label'])

    concepts = [concept['text'] for concept in content['concepts'] if concept['relevance'] > concept_relevance_threshold]
    print('Concepts include: ' + str(concepts))

    keywords = [keyword['text'] for keyword in content['keywords'] if keyword['relevance'] > keyword_relevance_threshold]
    print('Keywords noted: ' + str(keywords))

    categories = [category['label'] for category in content['categories'] if category['score'] > category_relevance_threshold]
    print('Categories: ' + str(categories))

    emotions = max(content['emotion']['document']['emotion'].items(), key=lambda k: k[1])
    if emotions[1] > emotion_score_threshold:
        print("Detected emotion of speech is " + emotions[0])


    data = {
        'categories': categories,
        'concepts': concepts,
        'emotions': emotions[0],
        'keywords': keywords,
        'sentiment': content['sentiment']['document']['label']
    }

    return json.dumps(data)
    print(json_string)

def get_access_token():
    data = {'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': api_key}
    data = parse.urlencode(data).encode()

    req = request.Request(token_endpoint, data=data)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        response = request.urlopen(req)
        encoding = response.info().get_content_charset('utf8')  # JSON default
        response_data = json.loads(response.read().decode(encoding))
        return response_data['access_token']
    except error.HTTPError as err:
       if err.code == 400:
           print("HTTP 400 Bad Request, token request is invalid")
       elif err.code == 404:
           print("HTTP 404 Not Found, token request is missing something")
       elif err.code == 401:
            print("HTTP 401 Unauthorized, make sure you are using valid credentials to make request.")
       else:
           raise

# Remove this if not running python3 AudiencePerception.py
if __name__ == '__main__':
   perception(text_example)


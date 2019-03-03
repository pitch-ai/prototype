from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, validators, FileField
from werkzeug import secure_filename
import speech_recognition as sr
import re
from flask import send_from_directory
import os
import urllib
import urllib2
import json
import base64
import requests

dirname = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(dirname, 'data')
ALLOWED_EXTENSIONS = set(['wav'])

# Hardcoded profile info
USERNAME = "Anita"

# App config.
TEMPLATES_AUTO_RELOAD = True
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Semantic similarity
# Takes in a text string and outputs the understanding of the audience:
# {
#   "categories": ["/technology and computing/internet technology"],
#   "concepts": ["Copyright", "Copyright infringement"],
#   "emotions": "sadness",
#   "keywords": ["Copyright Act", "copyright violation"],
#   "sentiment": "negative"
# }
text_example = "The missiles and rockets are no longer flying in every direction. Nuclear testing has stopped. Some military facilities are already being dismantled. Our hostages have been released. And as promised, the remains of our fallen heroes are being returned home to lay at rest in American soil."
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

def get_access_token():
    data = {'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
            'apikey': api_key}
    # data = parse.urlencode(data).encode()
    data = urllib.urlencode(data)

    req = urllib2.Request(token_endpoint, data=data)
    req.add_header('Accept', 'application/json')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        response = urllib2.urlopen(req)
        # encoding = response.info().get_content_charset('utf8')  # JSON default
        # encoding = response.headers.getparam("charset")  # python 2
        # response_data = json.loads(response.read().decode(encoding))
        response_data = json.loads(response.read())
        return response_data['access_token']
    except urllib2.HTTPError as err:
       if err.code == 400:
           print("HTTP 400 Bad Request, token request is invalid")
       elif err.code == 404:
           print("HTTP 404 Not Found, token request is missing something")
       elif err.code == 401:
            print("HTTP 401 Unauthorized, make sure you are using valid credentials to make request.")
       else:
           raise


# Filler words
def get_filler_word_count(filler_word,text):
    return sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(filler_word), text))

def get_text_from_speech(audio_file):
    print(str(audio_file))
    r = sr.Recognizer()
    af = sr.AudioFile(audio_file)
    with af as source:
        audio = r.record(source)
    r.energy_threshold = 4
    text = r.recognize_google(audio)
    return text

class ReusableForm(Form):
    inputFile = FileField('inputFile:', validators=[validators.required()])

@app.route("/")
def presentations():
    return render_template("presentations.html", user = USERNAME)

@app.route("/new", methods=['GET', 'POST'])
def new_presentation():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'inputFile' not in request.files:
            flash('Error: No file part')
            return redirect(request.url)
        file = request.files['inputFile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Error: No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_location)
            text = get_text_from_speech(file_location)
            filler_word ="like"
            like_count = get_filler_word_count(filler_word,text)
            flash(" Transcript: " + str(text) + "</br>" +
                "Like count : " + str(like_count) + "</br>" +
                "Semantic similarity: " + str(perception(text)))
            return render_template("results.html", user = USERNAME)
        else:
            flash('Error: Problem processing the file')
    return render_template("new_presentation.html", user = USERNAME, form = form)

@app.route('/record_video')
def record_video():
    return "Under construction"

@app.route('/results')
def results():
    return render_template("results.html", user = USERNAME)   

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'inputFile' not in request.files:
            flash('Error: No file part')
            return redirect(request.url)
        file = request.files['inputFile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Error: No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_location)
            text = get_text_from_speech(file_location)
            filler_word ="like"
            like_count = get_filler_word_count(filler_word,text)
            flash(" Transcript: " + str(text) + "</br>" +
                "Like count : " + str(like_count) + "</br>" +
                "Semantic similarity: " + str(perception(text)))
        else:
            flash('Error: Problem processing the file')
    return render_template('hello.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0')

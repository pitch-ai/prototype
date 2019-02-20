from flask import Flask, render_template, flash, request, redirect, url_for
from wtforms import Form, validators, FileField
from werkzeug import secure_filename
import speech_recognition as sr
import re
from flask import send_from_directory
import os

dirname = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(dirname, 'data')
ALLOWED_EXTENSIONS = set(['wav'])

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_filler_word_count(filler_word,text):
    return sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(filler_word), text))

def get_text_from_speech(audio_file):
    print("Hi")
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/", methods=['GET', 'POST'])
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
            flash(" Transcript: " + str(text) +"\n"+ "Like count : "+ str(like_count))
        else:
            flash('Error: Problem processing the file')
    return render_template('hello.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
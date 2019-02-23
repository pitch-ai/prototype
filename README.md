This holds the code for a Pitch.AI prototype hosted on a Flask app.

Clone the repo: git clone https://github.com/pitch-ai/prototype.git

Navigate into `/pitch-ai-flask` and `pip install` a couple things (Note: may need to add `--user` as a parameter. Also might need to install more things.):
- `pip install Flask-WTF`
- `pip install SpeechRecognition`


Make a new `/pitch-ai-flask/data` folder:
- `mkdir data`

In the same folder, run flask:
- `python flaskServer.py`

**Works with Python 2.7!**


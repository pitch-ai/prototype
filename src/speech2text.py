import speech_recognition as sr
import re

def get_filler_word_count(filler_word,text):
    return sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(filler_word), text))

def get_text_from_speech(audio_file):
    r = sr.Recognizer()
    af = sr.AudioFile(audio_file)
    with af as source:
        audio = r.record(source)
    r.energy_threshold = 4
    text = r.recognize_google(audio)
    return text



if __name__ == "__main__":

    audio_file ='../data/youtube_sample1.wav'
    text = get_text_from_speech(audio_file)

    print("Spoken text: "+text)

    filler_word ="like"
    like_count = get_filler_word_count(filler_word, text)

    print("No. of likes in speech: " + str(like_count))
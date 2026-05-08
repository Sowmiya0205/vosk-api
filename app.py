from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer
import wave
import json
import os

app = Flask(__name__)

MODEL_PATH = "model"
model = Model(MODEL_PATH)


@app.route("/")
def home():
    return "Vosk API Running"


@app.route("/audio/", methods=["POST"])
def transcribe():

    audio = request.files["audio"]

    temp_file = "temp.wav"
    audio.save(temp_file)

    wf = wave.open(temp_file, "rb")

    rec = KaldiRecognizer(model, wf.getframerate())

    result = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            part = json.loads(rec.Result())
            result += part.get("text", "") + " "

    final = json.loads(rec.FinalResult())
    result += final.get("text", "")

    wf.close()
    os.remove(temp_file)

    return jsonify({
        "text": result.strip()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

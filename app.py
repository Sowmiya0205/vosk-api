from flask import Flask, request, jsonify
from vosk import Model, KaldiRecognizer
import wave
import json
import os
import subprocess

app = Flask(__name__)

model = Model("model")


@app.route("/")
def home():
    return "Vosk API Running"


@app.route("/audio/", methods=["POST"])
def transcribe():

    audio = request.files["audio"]

    input_file = "input.webm"
    output_file = "converted.wav"

    audio.save(input_file)

    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-ar", "16000",
        "-ac", "1",
        "-f", "wav",
        output_file
    ])

    wf = wave.open(output_file, "rb")

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

    os.remove(input_file)
    os.remove(output_file)

    return jsonify({"text": result.strip()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

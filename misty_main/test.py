import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
import numpy as np

# -------- CONFIG --------
MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5  # seconds
KEYWORD = "misty"

# -------- LOAD MODEL --------
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

# -------- AUDIO QUEUE --------
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(indata.copy())

# -------- ACTION --------
def wake_word_detected():
    print("🔥 Wake word detected!")
    # Put your function here

# -------- MAIN LOOP --------
def listen():
    print("🎧 Listening continuously...")

    prev_chunk = np.zeros((int(SAMPLE_RATE * CHUNK_DURATION), 1), dtype=np.int16)

    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=1,
                        dtype='int16',
                        callback=callback,
                        blocksize=int(SAMPLE_RATE * CHUNK_DURATION)):

        while True:
            current_chunk = q.get()

            # Combine previous + current chunk (overlap)
            combined = np.concatenate((current_chunk), axis=0)

            # Convert to bytes
            data = combined.tobytes()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")

                print("Heard:", text)

                if KEYWORD in text:
                    wake_word_detected()

            # Shift window
            prev_chunk = current_chunk


if __name__ == "__main__":
    listen()
from pynput import keyboard
import time
from PIL import ImageGrab
from audiorecorder import AudioRecorder
import sounddevice as sd
import soundfile as sf
import tempfile
import sieve
from openai import OpenAI
import requests
import base64
import tkinter as tk
API_KEY = "API_KEY_HERE"
class HotkeyApp:
    def __init__(self):
        self.running = True
        self.is_hotkey_active = False
        self.recorder = AudioRecorder(bitrate='32k')
        self.client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")
        self.image = None
        self.hotkey = keyboard.HotKey(keyboard.HotKey.parse('<ctrl>+<alt>+h'), self.on_press)
    def on_press(self, key):
        print("Комбинация Ctrl+Alt+H нажата")
        self.is_hotkey_active = True
        if ImageGrab.grabclipboard() != None:
            ImageGrab.grabclipboard().save("screenshott.png")
            print("grabbed")
            with open("screenshott.png", "rb") as image_file:
                self.image = base64.b64encode(image_file.read()).decode('utf-8')
        self.recorder.start_recording()

    def on_release(self):
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
            temp_mp3_path = temp_mp3.name
        self.recorder.stop_recording("audio.wav")
        file = sieve.File(path="audio.wav")
        backend = "elevenlabs"
        word_level_timestamps = True
        source_language = "auto"
        diarization_backend = "None"
        min_speakers = -1
        max_speakers = -1
        custom_vocabulary = {"":""}
        translation_backend = "None"
        target_language = ""
        segmentation_backend = "ffmpeg-silence"
        min_segment_length = -1
        min_silence_length = 0.4
        vad_threshold = 0.2
        pyannote_segmentation_threshold = 0.8
        chunks = [""]
        denoise_backend = "None"
        initial_prompt = ""

        transcribe = sieve.function.get("sieve/transcribe")
        output = transcribe.run(
                            file = file,
                        backend = backend,
                        word_level_timestamps = word_level_timestamps,
                        source_language = source_language,
                        diarization_backend = diarization_backend,
                        min_speakers = min_speakers,
                        max_speakers = max_speakers,
                        custom_vocabulary = custom_vocabulary,
                        translation_backend = translation_backend,
                        target_language = target_language,
                        segmentation_backend = segmentation_backend,
                        min_segment_length = min_segment_length,
                        min_silence_length = min_silence_length,
                        vad_threshold = vad_threshold,
                        pyannote_segmentation_threshold = pyannote_segmentation_threshold,
                        chunks = chunks,
                        denoise_backend = denoise_backend,
                        initial_prompt = initial_prompt
                    )
        text = ""
        print(output)
        for output_object in output:
            print(output_object)
            text +=output_object['text']
        print(text)
        if self.image != None:
            messages = [
                {
                    "role": "system",
                    "content": (
                        """Ты — голосовой помощник, который отвечает на вопросы пользователя. Твои ответы будут озвучиваться.   Пожалуйста, формируй ответы так, чтобы: - Символы разметки Markdown и LaTeX (например, *, #, $, _, \, {, }) **не озвучивались**, если они служат только для форматирования. - Если символ несёт смысловую нагрузку в контексте (например, знак доллара $ при вопросе о курсе валюты), то озвучивай этот символ. - Используй простой и понятный язык, избегай сложных технических терминов, если это не требуется. - Не включай в ответ явные символы разметки, если это возможно, заменяй их на слова или интонационные паузы. - Если нужно выделить важные слова, используй интонационные подсказки, а не символы. - Форматируй числа, даты и денежные суммы так, чтобы их было удобно озвучивать.  Пример: Вместо \"Курс доллара сегодня составляет **75.32** рублей\" говори \"Курс доллара сегодня составляет семьдесят пять рублей тридцать две копейки\"."""
                    ),
                },
                {   
                    "role": "user",
                            "content": [
                                {"type":"text", "text":text},
                                {"type":"image_url", "image_url":{"url":f"data:image/png;base64,{self.image}"}}
                            ],
                        },
                        ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": (
                        """Ты — голосовой помощник, который отвечает на вопросы пользователя. Твои ответы будут озвучиваться.   Пожалуйста, формируй ответы так, чтобы: - Символы разметки Markdown и LaTeX (например, *, #, $, _, \, {, }) **не озвучивались**, если они служат только для форматирования. - Если символ несёт смысловую нагрузку в контексте (например, знак доллара $ при вопросе о курсе валюты), то озвучивай этот символ. - Используй простой и понятный язык, избегай сложных технических терминов, если это не требуется. - Не включай в ответ явные символы разметки, если это возможно, заменяй их на слова или интонационные паузы. - Если нужно выделить важные слова, используй интонационные подсказки, а не символы. - Форматируй числа, даты и денежные суммы так, чтобы их было удобно озвучивать.  Пример: Вместо \"Курс доллара сегодня составляет **75.32** рублей\" говори \"Курс доллара сегодня составляет семьдесят пять рублей тридцать две копейки\"."""
                ),
            },
            {   
                "role": "user",
                "content": (
                    text
                ),
            },
            ]
        #print(messages)
        response = self.client.chat.completions.create(
            model="sonar",
            messages=messages,
            stream=False
        )
        print(response.choices[0].message.content)
        voice = "openai-echo-hd"
        text = response.choices[0].message.content
        emotion = "normal"
        pace = "normal"
        stability = 0.9
        style = 0.3
        word_timestamps = False
        reference_audio = {"url":""}
        tts = sieve.function.get("sieve/tts")
        text_words = text.split(" ")
        texts = []
        cnter = 0
        txt = ""
        for word in text_words:
            if len(word)+len(txt)+1 < 1200:
                txt += " " + word
            else:
                if len(txt) > 1200:
                    print("Text too long")
                texts.append(txt)
                cnter = 0
                txt = word
        if len(txt) > 0:
            texts.append(txt)
        root = tk.Tk()
        root.title("CMDBuddy")
        root.geometry("300*100")
        label = tk.Label(root, text=text, wraplength=280, font=("Arial", 12))
        label.pack(expand=True, fill="both", padx=10, pady=10)
        close_button = tk.Button(root, text="Close", command=root.destroy)
        close_button.pack(pady=5)
        root.mainloop()
        for textt in texts:                        
            output = tts.run(
                voice = voice,
                text = textt,
                emotion = emotion,
                pace = pace,
                stability = stability,
                style = style,
                word_timestamps = word_timestamps,
                reference_audio = reference_audio
            )
            print(output.path)
            data, fs = sf.read(output.path)
            sd.play(data, fs)
            sd.wait()
        self.image = None
                
    def check_deactivation(self, key):
        if self.is_hotkey_active and not self.hotkey._state.matches(self.hotkey._keys):
            self.is_hotkey_active = False
            self.on_release()
    def stop(self):
        print("Выход из приложения...")
        self.running = False
        if self.listener:
            self.listener.stop()
    def run(self):
        def for_canonical(f):
            return lambda k: f(l.canonical(k))
        print("Приложение запущено. Зажмите Ctrl+Alt+H или нажмите Esc для выхода")
        with keyboard.Listener(
                on_press=for_canonical(self.hotkey.press),
                on_release=lambda k: [for_canonical(self.hotkey.release)(k), self.check_deactivation(k)]) as l:
            l.join()
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

if __name__ == "__main__":
    app = HotkeyApp()
    app.run()
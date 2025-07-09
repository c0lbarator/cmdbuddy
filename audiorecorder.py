import sounddevice as sd
import numpy as np
#from pydub import AudioSegment
from datetime import datetime
import tempfile
import os
import soundfile as sf
class AudioRecorder:
    def __init__(self, samplerate=22050, channels=1, bitrate='64k'):
        self.samplerate = samplerate
        self.channels = channels
        self.bitrate = bitrate  # Качество сжатия MP3 (32k, 64k, 128k и т.д.)
        self.recording = False
        self.audio_data = None
    def start_recording(self):
        if not self.recording:
            print("Начало записи...")
            self.recording = True
            self.audio_data = []
            
            def callback(indata, frames, time, status):
                if status:
                    print(status, file=sys.stderr)
                self.audio_data.append(indata.copy())
            
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                callback=callback
            )
            self.stream.start()
    
    def stop_recording(self, filename=None):
        if self.recording:
            print("Остановка записи...")
            self.stream.stop()
            self.stream.close()
            self.recording = False
            
            if self.audio_data:
                # Объединяем все фрагменты аудио
                audio_data = np.concatenate(self.audio_data, axis=0)
                
                # Если имя файла не указано, генерируем его из текущего времени
                if filename is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"recording_{timestamp}.wav"
                #elif not filename.lower().endswith('.mp3'):
                    #filename += '.mp3'
                
                # Сначала сохраняем во временный WAV файл
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                    temp_wav_path = temp_wav.name
                    sf.write(filename, audio_data, self.samplerate)
                
                # Конвертируем в MP3
                try:
                    #sound = AudioSegment.from_wav(temp_wav_path)
                    #sound.export(filename, format="mp3", bitrate=self.bitrate)
                    print(f"Запись сохранена как {filename} (размер: {os.path.getsize(filename) / 1024:.1f} KB)")
                finally:
                    # Удаляем временный WAV файл
                    os.unlink(temp_wav_path)
                
                return filename
        return None
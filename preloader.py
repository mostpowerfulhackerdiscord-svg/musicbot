import os
audio_folder = "Modules/sounds"

def preload_audios():
    files = [f for f in os.listdir(audio_folder) if f.endswith(".mp3")]
    print(f"Preloaded audios: {files}")
    return files

if __name__ == "__main__":
    preload_audios()

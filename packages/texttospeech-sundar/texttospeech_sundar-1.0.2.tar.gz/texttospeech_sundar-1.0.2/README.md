# texttospeech-sundar

A simple hybrid text-to-speech package that works **online and offline**.

## Features
- Online mode → High-quality Google TTS (gTTS)
- Offline mode → pyttsx3 (works without internet)
- Auto-detection of internet
- Ability to save or directly play the audio

## Installation
pip install texttospeech_sundar

## Usage
```python
from texttospeech_sundar import tts_sundar

tts_sundar("Hello welcome")
path = tts_sundar("Hello world!", play_audio=False, save_path="output.mp3")
print(path)

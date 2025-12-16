"""
texttospeech-sundar: Online + Offline Text-to-Speech
"""

import os
import tempfile
import socket
from gtts import gTTS
from playsound import playsound
import pyttsx3

__version__ = "1.0.0"


def has_internet(timeout=2):
    """Check if internet is available."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False


def offline_tts(text, save_path=None, play_audio=True):
    """Offline voice using pyttsx3."""
    engine = pyttsx3.init()

    if save_path:
        audio_path = save_path
    else:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_path = temp.name
        temp.close()

    engine.save_to_file(text, audio_path)
    engine.runAndWait()

    if play_audio:
        playsound(audio_path)

    return audio_path


def online_tts(text, lang="en", slow=False, save_path=None, play_audio=True):
    """Online TTS using Google gTTS."""
    tts = gTTS(text=text, lang=lang, slow=slow)

    if save_path:
        audio_path = save_path
    else:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        audio_path = temp.name
        temp.close()

    tts.save(audio_path)

    if play_audio:
        playsound(audio_path)

    return audio_path


def tts_sundar(text, lang="en", slow=False, save_path=None, play_audio=True):
    """
    Automatically uses ONLINE gTTS if internet exists,
    otherwise OFFLINE pyttsx3.
    """
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")

    if has_internet():
        return online_tts(text, lang, slow, save_path, play_audio)
    else:
        return offline_tts(text, save_path, play_audio)

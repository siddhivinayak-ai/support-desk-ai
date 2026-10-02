"""Voicemail tickets: transcribe the recording, then treat it like an email."""

from openai import OpenAI

client = OpenAI()


def transcribe_voicemail(path):
    with open(path, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="text",
        )
    return transcript.strip()

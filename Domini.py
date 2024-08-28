import streamlit as st
from audio_recorder_streamlit import audio_recorder
from google.cloud import texttospeech
import io
import os

# Function to synthesize speech using Google TTS
def synthesize_speech(text):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D'  # Choose a human-like voice
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    return response.audio_content

# Streamlit App
st.title("Speech Synthesis with Streamlit")

st.write("Record your audio and convert text to speech!")

# Record audio
audio_data = audio_recorder("Click to record")
if audio_data:
    st.audio(audio_data, format='audio/wav')
    st.write("Audio recorded successfully!")

# Text input for TTS
text = st.text_area("Enter text to convert to speech")
if st.button("Generate Speech"):
    if text:
        audio_content = synthesize_speech(text)
        st.audio(io.BytesIO(audio_content), format='audio/wav')
        st.write("Generated speech:")
    else:
        st.write("Please enter text to generate speech.")

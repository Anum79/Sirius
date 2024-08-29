# speech_key = "YOUR_AZURE_SPEECH_KEY"
# service_region = "YOUR_SERVICE_REGION"

import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import pyttsx3

def text_to_speech_urdu(text):
    # Replace with your Azure Speech service key and region
    speech_key = "547a69c82f0f428caad3537ce7f58c73"
    service_region = "eastus"

    # Set up the Azure Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"  # Ensure this voice is supported

    # Create an in-memory audio stream using tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_audio_file.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Define SSML
        ssml = f"""
        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="ur-PK">
            <voice name="ur-PK-UzmaNeural">
                {text}
            </voice>
        </speak>
        """
        # Perform text-to-speech with SSML
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.success("Successfully synthesized the text.")
            return temp_audio_file.name
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            st.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancellation_details.error_details}")
            return None

def play_audio(audio_file_path):
    # Play the audio file using Streamlit's audio player
    with open(audio_file_path, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/wav")

# Streamlit app
st.title("Urdu Text-to-Speech Converter")

# Text input for generating speech
text_input = st.text_area("Enter the text you want to convert to speech in Urdu:")

# Button to generate speech
if st.button("Generate Speech"):
    if text_input:
        audio_file_path = text_to_speech_urdu(text_input)
        if audio_file_path:
            play_audio(audio_file_path)
    else:
        st.warning("Please enter some text to convert to speech.")

# Option to record audio input
st.subheader("Or record your voice:")
audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

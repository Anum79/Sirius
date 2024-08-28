speech_key = "YOUR_AZURE_SPEECH_KEY"
service_region = "YOUR_SERVICE_REGION"


import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
import tempfile

def text_to_speech_urdu(text):
    # Replace with your Azure Speech service key and region
    speech_key = "YOUR_AZURE_SPEECH_KEY"
    service_region = "YOUR_SERVICE_REGION"
    
    # Set up the Azure Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"  # Ensure this voice is supported
    
    # Create a temporary file to save the audio output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_audio_file.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        # Perform text-to-speech
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.success("Text has been successfully synthesized to speech.")
            return temp_audio_file.name
        else:
            st.error("Speech synthesis failed.")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                st.error(f"Cancellation details: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    st.error(f"Error details: {cancellation_details.error_details}")
            return None

# Example of how to use this in your Streamlit app
st.title("AI Virtual Psychiatrist with Azure TTS")
urdu_text = "آپ کیسے ہیں؟"  # Example text in Urdu

# Generate and play the synthesized speech
audio_file_path = text_to_speech_urdu(urdu_text)
if audio_file_path:
    st.audio(audio_file_path, format='audio/wav')

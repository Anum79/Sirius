import streamlit as st
from audio_recorder_streamlit import audio_recorder
import azure.cognitiveservices.speech as speechsdk

# Azure Cognitive Services setup
speech_key = "YOUR_AZURE_SPEECH_KEY"
service_region = "YOUR_SERVICE_REGION"

def speech_to_text(audio_data):
    # Initialize Azure Speech SDK for speech recognition
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
    # Save the recorded audio to a file (required for the Azure SDK)
    with open("recorded_audio.wav", "wb") as audio_file:
        audio_file.write(audio_data)
    
    # Configure audio for speech recognition from the saved file
    audio_config = speechsdk.audio.AudioConfig(filename="recorded_audio.wav")
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        st.error("No speech could be recognized.")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.error(f"Speech Recognition canceled: {cancellation_details.reason}")
        return None

def text_to_speech(text):
    # Set up the Azure Speech SDK for speech synthesis
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"  # Ensure this voice is supported
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Perform text-to-speech
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        st.success("Successfully synthesized the text.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.error(f"Speech synthesis canceled: {cancellation_details.reason}")

def main():
    st.title("Urdu Speech-to-Text and Text-to-Speech")

    # Record audio
    audio_bytes = audio_recorder()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        if st.button("Convert Speech to Text"):
            # Convert the recorded audio to text
            st.write("Converting speech to text...")
            transcribed_text = speech_to_text(audio_bytes)

            if transcribed_text:
                st.write(f"Transcribed Text: {transcribed_text}")

                # Convert the transcribed text back to speech
                if st.button("Convert Text to Speech"):
                    st.write("Converting text to speech...")
                    text_to_speech(transcribed_text)

if __name__ == "__main__":
    main()

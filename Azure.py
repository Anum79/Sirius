import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from audio_recorder_streamlit import audio_recorder
import io

def text_to_speech_urdu(text):
    # Replace with your Azure Speech service key and region
    speech_key = YOUR_AZURE_SPEECH_KEY
    service_region = YOUR_SERVICE_REGION

    # Set up the Azure Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"  # Ensure this voice is supported

    # Create an in-memory audio stream
    audio_stream = io.BytesIO()
    audio_config = speechsdk.audio.AudioOutputConfig(stream=speechsdk.audio.PushAudioOutputStream(audio_stream))

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
        audio_stream.seek(0)
        st.audio(audio_stream, format="audio/wav")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.error(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            st.error(f"Error details: {cancellation_details.error_details}")

if __name__ == "__main__":
    st.title("Urdu Text to Speech")

    urdu_text = st.text_area("Enter the text you want to convert to speech in Urdu:", "یہ ایک ٹیسٹ ہے")

    if st.button("Convert to Speech"):
        text_to_speech_urdu(urdu_text)

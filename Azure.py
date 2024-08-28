import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from audio_recorder_streamlit import audio_recorder

def text_to_speech_urdu(text):
    # Replace with your Azure Speech service key and region
    speech_key = "YOUR_AZURE_SPEECH_KEY"
    service_region = "YOUR_SERVICE_REGION"

    # Set up the Azure Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"  # Ensure this voice is supported

    # Create an in-memory audio stream
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=False)

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
        st.write("Successfully synthesized the text.")
        # Return the synthesized audio
        return result.audio_data
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        st.write(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            st.write(f"Error details: {cancellation_details.error_details}")
        return None

def main():
    st.title("Urdu Text-to-Speech")

    urdu_text = st.text_area("Enter the text you want to convert to speech in Urdu:")

    if st.button("Convert to Speech"):
        if urdu_text:
            audio_data = text_to_speech_urdu(urdu_text)
            if audio_data:
                st.audio(audio_data, format='audio/wav')
        else:
            st.warning("Please enter some text.")

if __name__ == "__main__":
    main()

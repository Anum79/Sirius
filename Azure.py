# speech_key = "YOUR_AZURE_SPEECH_KEY"
# service_region = "YOUR_SERVICE_REGION"

import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import speech_recognition as sr
from datasets import load_dataset
from deep_translator import GoogleTranslator
import google.generativeai as genai


# Configure the API key for Google Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=api_key)

# Set up Azure Speech SDK credentials
speech_key = "547a69c82f0f428caad3537ce7f58c73"  # Replace with your Azure Speech key
service_region = "eastus"  # Replace with your service region

# Translator for English to Urdu
translator = GoogleTranslator(source='en', target='ur')

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Load data from a file
def load_data(filepath="dataG.txt"):
    documents = []
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            documents.append(file.read())
    else:
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    return documents

# Clean text function
def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

def conversational_retrieval(query, chat_history):
    documents = load_data()
    combined_documents = " ".join(documents)
    conversation_context = "\n".join([f"User: {q}\nGenaiera: {a}" for q, a in chat_history])
    genaiera_persona = (
        "You are Genaiera, a compassionate and empathetic therapist with a deep understanding of mental health issues. "
        "Your goal is to provide support, guidance, and understanding to those seeking help. You respond in a warm, caring, and professional manner."
    )
    full_context = f"{genaiera_persona}\n{conversation_context}\nDocuments: {combined_documents}\nUser Query: {query}"
    
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    n_response = model.generate_content(full_context)
    response = clean_text(n_response.text)
    
    return response

# Convert text to speech using Azure Speech service in Urdu
def text_to_speech_urdu(text):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "ur-PK-UzmaNeural"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_audio_file.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        ssml = f"""
        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="ur-PK">
            <voice name="ur-PK-UzmaNeural">
                {text}
            </voice>
        </speak>
        """
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return temp_audio_file.name
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            st.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancellation_details.error_details}")
            return None

# Transcribe audio to text in Urdu
def transcribe_audio_to_text(audio_data):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="ur-PK")
            return text
        except sr.UnknownValueError:
            st.error("Google Web Speech API could not understand the audio")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Web Speech API; {e}")
    return None

# Streamlit app title and description
st.title("AI Virtual Psychiatrist")
st.write("Speak into the microphone and get responses from the AI Psychiatrist.")

# Record audio from the user
st.subheader("Record your voice:")
audio_bytes = audio_recorder()

# Display chat history
if st.session_state.chat_history:
    st.subheader("Chat History")
    for i, (query, response) in enumerate(st.session_state.chat_history):
        st.write(f"Q{i+1}: {query}")
        st.write(f"A{i+1}: {response}")

# Process the recorded audio
if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        audio_file_path = temp_audio_file.name

    transcribed_text = transcribe_audio_to_text(audio_file_path)
    if transcribed_text:
        st.write(f"آپ نے کہا: {transcribed_text}")

        # Retrieve response from the AI model
        result = conversational_retrieval(transcribed_text, st.session_state.chat_history)
        result_ur = translator.translate(result)
        st.write("Dr. Jennifer:", result_ur)

        # Append the query and response to chat history
        st.session_state.chat_history.append((transcribed_text, result_ur))

        # Convert response text to speech and play it
        audio_file_path = text_to_speech_urdu(result_ur)
        if audio_file_path:
            st.audio(audio_file_path, format="audio/wav")


import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import speech_recognition as sr
from datasets import load_dataset
from deep_translator import GoogleTranslator
import google.generativeai as genai
import re

api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=api_key)

speech_key = os.getenv("AZURE_SPEECH_KEY")
service_region = os.getenv("AZURE_SERVICE_REGION")
if speech_key is None or service_region is None:
    raise ValueError("Azure Speech key or service region not found. Set the AZURE_SPEECH_KEY and AZURE_SERVICE_REGION environment variables.")

translator = GoogleTranslator(source='en', target='ur')

# # Initialize chat history
# if 'chat_history' not in st.session_state:
#     st.session_state.chat_history = []

def load_data(filepath="dataHealth.txt"):
    documents = []
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            documents.append(file.read())
    else:
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    return documents

def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def conversational_retrieval(query, chat_history):
    documents = load_data()
    combined_documents = " ".join(documents)
    
    conversation_context = "\n".join([f"User: {q}\nGenaiera: {a}" for q, a in chat_history])

    genaiera_persona = (
    "You are Genaiera, a compassionate and empathetic female doctor with a deep understanding of mental health issues. "
    "As a female therapist, you are known for your gentle and caring approach. Your goal is to provide support, guidance, and understanding to those seeking help. "
    "You respond in a warm, nurturing, and professional manner, always considering the emotional and mental well-being of your patients."
    )
    
    full_context = f"{genaiera_persona}\n{conversation_context}\nDocuments: {combined_documents}\nUser Query: {query}"
    
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    n_response = model.generate_content(full_context)
    response = clean_text(n_response.text)
    
    return response

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

st.title("AI Virtual Psychiatrist")
st.write("Speak into the microphone and get responses from the AI Psychiatrist.")

st.subheader("Record your voice:")
audio_bytes = audio_recorder()

if st.session_state.chat_history:
    st.subheader("Chat History")
    for i, (query, response) in enumerate(st.session_state.chat_history):
        st.write(f"Q{i+1}: {query}")
        st.write(f"A{i+1}: {response}")

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        audio_file_path = temp_audio_file.name

    transcribed_text = transcribe_audio_to_text(audio_file_path)
    if transcribed_text:
        st.write(f"آپ نے کہا: {transcribed_text}")

        result = conversational_retrieval(transcribed_text, st.session_state.chat_history)
        result_ur = translator.translate(result)
        st.write("Dr. Genaiera:", result_ur)

        st.session_state.chat_history.append((transcribed_text, result_ur))

        audio_file_path = text_to_speech_urdu(result_ur)
        if audio_file_path:
            st.audio(audio_file_path, format="audio/wav")



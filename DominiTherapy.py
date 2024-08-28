import os
import google.generativeai as genai
import sys
from datasets import load_dataset
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import tempfile
import re

# Configure the API key for Google Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API key not found. Set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=api_key)

# Translator for English to Urdu
translator = GoogleTranslator(source='en', target='ur')

# Load data from a file
def load_data(filepath="dataG.txt"):
    documents = []
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file:
            documents.append(file.read())
    else:
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    return documents

# Function to clean text
def clean_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    return text

# Function to retrieve conversational response from the AI model
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

# Translate text from English to Urdu
def translate_text(text, src_lang='en', dest_lang='ur'):
    return translator.translate(text)

# Convert text to speech in Urdu
def text_to_speech(text, lang='ur'):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_output:
            tts.save(temp_audio_output.name)
            return temp_audio_output.name
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Streamlit app title and description
st.title("AI Virtual Psychiatrist")
st.write("Speak into the microphone and get responses from the AI Psychiatrist.")

# Record audio from the user
st.write("Record your query:")
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
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)
        try:
            query = recognizer.recognize_google(audio, language='ur')
            st.write(f"آپ نے کہا: {query}")
            
            # Retrieve response from the AI model
            result = conversational_retrieval(query, st.session_state.chat_history)
            result_ur = translate_text(result)
            st.write("Dr. Jennifer:", result_ur)

            # Append the query and response to chat history
            st.session_state.chat_history.append((query, result_ur))
            
            # Convert response text to speech and play it
            audio_file_path = text_to_speech(result_ur)
            st.audio(audio_file_path, format='audio/mp3')
        
        except sr.UnknownValueError:
            st.write("معذرت، میں آڈیو کو سمجھ نہیں سکا۔")
        except sr.RequestError as e:
            st.write(f"معذرت، میں سروس سے نتائج کی درخواست نہیں کر سکا۔ {e}")
        except Exception as e:
            st.write(f"ایک خطا واقع ہوئی: {str(e)}")

import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
from PIL import Image
import io

# --- AURA CORE ---
class AuraBrain:
    def __init__(self):
        self.personality = "You are AURA, a formal and professional AI assistant. Be concise, polite, and helpful. Address the user formally."
        self.chat_history = []
    
    def think(self, user_input):
        # For V1 we use a simple response. Later swap with Ollama/Llama
        # Install Ollama and run: ollama run llama3.1:8b
        try:
            import ollama
            messages = [{"role": "system", "content": self.personality}] + self.chat_history + [{"role": "user", "content": user_input}]
            response = ollama.chat(model='llama3.1:8b', messages=messages)
            reply = response['message']['content']
        except:
            # Fallback if Ollama not installed
            reply = f"Acknowledged. You said: '{user_input}'. I am AURA, your formal assistant. How may I assist you further?"
        
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": reply})
        return reply

# --- VOICE ---
def speak(text):
    def _speak():
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak).start()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Say 'Hey Aura' first")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)
        return text
    except:
        return ""

# --- UI ---
st.set_page_config(page_title="AURA", page_icon="🤖", layout="wide")
st.title("AURA - Formal AI Assistant")
st.caption("Say 'Hey Aura' or 'Aura' to activate voice. Formal mode enabled.")

if "brain" not in st.session_state:
    st.session_state.brain = AuraBrain()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Vision + Settings
with st.sidebar:
    st.header("👁️ Computer Vision")
    uploaded_file = st.file_uploader("Upload image for analysis", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
        if st.button("Describe Image"):
            st.session_state.messages.append({"role": "user", "content": "Describe this image"})
            response = "I see an uploaded image. For full vision, connect a CLIP model here."
            st.session_state.messages.append({"role": "assistant", "content": response})
            speak(response)
    
    st.divider()
    if st.button("🎤 Hold to Talk"):
        user_voice = listen()
        if "hey aura" in user_voice.lower() or "aura" in user_voice.lower():
            st.success(f"Heard: {user_voice}")
            response = st.session_state.brain.think(user_voice)
            st.session_state.messages.append({"role": "user", "content": user_voice})
            st.session_state.messages.append({"role": "assistant", "content": response})
            speak(response)
        else:
            st.warning("Wake word not detected. Say 'Hey Aura'")

# Main Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Type your request..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    response = st.session_state.brain.think(prompt)
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    speak(response)
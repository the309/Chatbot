# Import necessary libraries 
import streamlit as st
import requests
import time
import os

# -------------------------------------
# Design UI using streamlit.
# -------------------------------------

# FastAPI Backend URL.
API_BASE_URL = "http://127.0.0.1:8080"

# Set Page title.
st.set_page_config(page_title="AI Chatbot 🤖", layout="wide")

# Set Sidebar - Upload PDF.
st.sidebar.header("Upload Document 📄")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with st.sidebar:
        st.success("PDF File uploaded successfully!", icon="✅")
    # Save file locally
    save_path = os.path.join("uploads", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    # Send file to backend To Save It and retrieve.
    with st.sidebar:
        with st.spinner("Uploading..."):
            files = {"file": open(save_path, "rb")}
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        if response.status_code == 200:
            st.sidebar.success("File processed!", icon="📜")
        else:
            st.sidebar.error(f"Upload failed: {response.text}")

# Sidebar - Select AI Model.
st.sidebar.header("Select AI Model 🤖")
model_choice = st.sidebar.selectbox("Choose AI Model", ["Gemini", "Deepseek", "OpenAI"])

# Chatbox UI.
st.title("AI Chat Assistant 💬")
st.markdown("Chat with an AI model based on your uploaded document.")

# Initialize session state for chat history.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history in the chat box.
for role, text in st.session_state.chat_history:
    if role == "assistant":
        st.chat_message("assistant").write(text)
    else: 
        st.chat_message("user").write(text)

# Set User input box. 
user_message = st.chat_input("Type your message.....")

# Function to simulate typing effect of Ai.
def display_typing_effect(message, delay=0.01):
    """
    Function to display a typing effect when showing a message in Streamlit chat.
    
    Parameters:
    - delay (float): The time delay between each character (default: 0.01s).
    - message (str): The message to display.
    """
    output = ""
    message_container = st.chat_message("assistant")
    chat_area = message_container.empty()
    
    for char in message:
        output += char
        chat_area.write(output)
        time.sleep(delay)

# Send a message to the backend.
if user_message:
    # Store user new message in the chat history.
    st.session_state.chat_history.append(("user", user_message))
    st.chat_message("user").write(user_message)

    # Prepare the payload Json to send it to the backend. 
    payload = {
        "message": user_message,
        "history": [msg[1] for msg in st.session_state.chat_history],
        "model": model_choice
    }
    
    # Send request to backend
    response = requests.post(f"{API_BASE_URL}/chat", json=payload)
    # Handle what happens if the request succeeds.  
    if response.status_code == 200:
        ai_response = response.json().get("response", "Error: No response received")
        st.session_state.chat_history.append(("assistant", ai_response))  # Store AI response in chat history.
        display_typing_effect(ai_response)  # Show AI response with typing effect.
    else:
        st.error(f"Error {response.status_code}: {response.text}")

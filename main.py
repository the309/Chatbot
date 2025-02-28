import threading
import os
import time
import uvicorn

# Function to start FastAPI server
def run_api():
    os.system("uvicorn server:app --host 127.0.0.1 --port 8080")

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    # Wait for FastAPI to start before launching Streamlit
    time.sleep(5) 

    # Start Streamlit UI
    os.system("streamlit run ui.py")

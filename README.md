# Chatbot Application 🤖  

![chatbot](https://github.com/user-attachments/assets/bb4173ed-f151-4fa6-be7c-f474164f6a04)

A smart AI-powered chatbot that provides responses based on a structured knowledge base.  



###  Features  

-  **PDF Processing**: Uploads and extracts text from PDFs for reference.  
-  **AI-Powered Responses**: Supports **OpenAI, DeepSeek, and Gemini** models for generating intelligent responses.  
-  **Vector Storage & Retrieval**: Uses **ChromaDB** to store and retrieve processed text efficiently.  
-  **FastAPI Backend & Streamlit UI**: Provides a responsive API and an interactive user interface.  
-  **Flexible Deployment**: Run the chatbot via **Python** or **Docker**.  
-  **Knowledge-Restricted Answers**: Ensures responses are based strictly on the provided knowledge base.  

---

##  Installation & Setup  

### Method 1: Running from Source (GitHub)  

#### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/AliFeteha/chatbot.git
cd chatbot
```
#### 2️⃣ Create a Virtual Environment
```bash
conda create --name chatbot_env python=3.10
conda activate chatbot_env
```
#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
#### 4️⃣ Run the Application
```bash
python main.py
```
Access API Docs: http://localhost:8080/docs
Access UI (if available): http://localhost:8501 


### Method 2: Running with Docker

#### 1️⃣ Pull the Docker Image 
```bash
docker pull alifeteha/chatbot
```
#### 2️⃣ Create a Virtual Environment
```bash
docker run -d -p 8080:8080 -p 8501:8501 --name chat-bot alifeteha/chatbot
```
Access API Docs: http://localhost:8080/docs
Access UI (if available): http://localhost:8501

## API Documentation
The chatbot API is built using FastAPI

### Example Endpoints:  
- **`POST /upload`** → Upload a PDF and store text in ChromaDB  
- **`POST /chat`** → Send a message and receive a chatbot response  
- **`GET /health`** → Check the server status
### This is how the API documentation looks like

![backend_doc](https://github.com/user-attachments/assets/a8c3854d-48df-48b7-bd29-f484d1ede03a)

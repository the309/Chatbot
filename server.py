# Import necessary libraries 
import os
import mimetypes
import uvicorn
import fitz 
from fastapi import  File, HTTPException ,FastAPI, UploadFile
from pydantic import BaseModel
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from openai import OpenAI
from langchain_chroma import Chroma
from dotenv import load_dotenv
# -------------------------------------
# API Configuration
# -------------------------------------
# Load environment variables from .env.
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set Path To Store pdf and its corresponding ChromaDB.
CHROMA_PATH = "chroma_db"
UPLOAD_DIR = "uploads"

# Ensure directories are exist.
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)
# -------------------------------------
# Initialize LLMs and Embedding Model and ChromaDB.
# -------------------------------------

# Intiliaze General-Purpose Embeddings.
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)
# Intiliaze Three diffrent LLMs to be used.
GEMINI_LLM = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.5,
    google_api_key=GEMINI_API_KEY
)
DEEPSEEK_LLM = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=DEEPSEEK_API_KEY,  
)
OPENAI_LLM = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY, 
)
# Initialize ChromaDB
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH
)
# Create a retriever to perform a similarity search.
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 10}
)

# -------------------------------------
# Initialize FastAPI & endpoints.
# -------------------------------------
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}


# -------------------------------------
# PDF Upload and Processing.
# -------------------------------------
def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF using fitz (PyMuPDF).
    """
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text.strip()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    API endpoint to:
    1. Upload a PDF document.
    2. Store the PDF in UPLOAD_DIR.
    3. Extract text from the PDF.
    4. Store extracted text in ChromaDB.
    """
    # Validate if a file is uploaded
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded. Please try again.")

    # Validate file type (only PDF allowed)
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    # Save the file in UPLOAD_DIR
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving failed: {str(e)}")

    # Extract text from the PDF
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from the PDF.")

    # Store extracted text in ChromaDB
    doc = Document(page_content=text)

    # Handle empty vector_store case before deleting
    existing_data = vector_store.get()
    if existing_data and "ids" in existing_data and existing_data["ids"]:
        vector_store.delete(ids=existing_data["ids"])

    vector_store.add_documents([doc])

    return {"message": f"PDF '{file.filename}' successfully processed and stored."}

    
# -------------------------------------
# Chat Endpoint.
# -------------------------------------

# Define the structure of chat requests.
class ChatRequest(BaseModel):
    message: str
    history: list = []
    model: str = "Gemini"


@app.post("/chat")
async def chat_api(request: ChatRequest):
    """
    API endpoint to use retrieved document knowledge & chat history to integrate as a chatbot using Three different LLMs.
    
    """
    docs = retriever.invoke(request.message)
    knowledge = "\n\n".join(doc.page_content for doc in docs) if docs else "No relevant knowledge found."

    model_choice = request.model.lower()
    # construct a prompt That boasts the LLm to respond with the correct answer. 
    rag_prompt = f"""
    ### Role & Purpose
    You are an advanced AI assistant designed to provide **accurate, concise, and context-aware** responses. 
    Your answers must be derived **strictly from the provided knowledge** and must **avoid speculation or assumptions**.

    ### Special Cases:
    - If the user greets with "hello", "hi", "hey", "welcome", or similar:
      - Respond with: **"Hey! I'm ChatBot, here to assist you. How can I help today?"**
      - Do **not** process this as a standard query.

    ### Context
    - **User Query:** {request.message}
    - **Conversation History:** 
      {request.history if request.history else "No prior history available."}

    ### Instructions
    - **Prioritize factual accuracy** based only on the knowledge provided.
    - **Avoid using any external sources, assumptions, or personal opinions.**
    - **Maintain a natural, informative, and engaging tone** while being clear and concise.
    - If the answer is **not found within the provided knowledge**, **state that explicitly** rather than guessing.

    ### Knowledge Base:
    {knowledge}

    ### Response Format:
    - If the answer is **directly available**, provide a **clear and structured response**.
    - If the information is **ambiguous or missing**, acknowledge it and suggest possible clarifications.
    - If relevant, provide **summaries, step-by-step explanations, or examples** for clarity.
    """

    # Navigate between different LLMS depending on choice.
    if model_choice == "Deepseek":
        response_generator = DEEPSEEK_LLM.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": rag_prompt}],
            stream=True 
        )
        response = ""
        for chunk in response_generator:
            response += chunk.choices[0].delta.content 
        return {"response": response}
    elif model_choice == "OpenAI":
        response_generator = OPENAI_LLM.chat.completions.create(
            model="openai/o3-mini-high",
            messages=[{"role": "user", "content": rag_prompt}],
            stream=True
        )
        response = ""
        for chunk in response_generator:
            response += chunk.choices[0].delta.content
        return {"response": response}
    else:
        response_generator = GEMINI_LLM.stream(rag_prompt)
        response = "".join(r.content for r in response_generator)

    return {"response": response}



# -------------------------------------
# Run API Function (For External Calls)
# -------------------------------------
def run_api():
    # Use UVICORN to run FAST API in PORT 80 Locally.
    uvicorn.run(app, host="127.0.0.1", port=8080)

# Run the API if this file is executed directly
if __name__ == "__main__":
    run_api()

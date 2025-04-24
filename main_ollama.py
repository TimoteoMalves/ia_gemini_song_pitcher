from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import fitz 
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

#uvicorn main:app --reload

app = FastAPI()
user_inputAPI = ""
file_context = "context.txt"
last_file_content = ""
chat_status = 0

template ="""
Answer the question below.

Here is the conversation history: {context}

Your name is Freddie mercury and you are a artifical integence made to change the key of asked songs. You do that only if the person sends you a file or the song as a text.

Question: {question}

Answer:
"""

#using fitz to be able to read pdf
def readFile(file):

    doc = fitz.open(file)
    file_content = ""

    for page in doc:
        text = page.get_text()
        file_content += text

    return file_content

#update context
def new_context(file_path,user_input,result):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"\nUser: {user_input}\nAI: {result}")

#upload endpoint
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global last_file_content

    filename = file.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed.")

    # Save file temporarily
    file_location = f"temp_files/{file.filename}"
    os.makedirs("temp_files", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    last_file_content = readFile(file_location)
    return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully."})

# Reber mensagem
class Message(BaseModel):
    text: str

#message endpoint
@app.post("/message/")
async def receive_message(msg: Message):
    global user_inputAPI

    user_inputAPI = msg.text
    response = process_prompt()
    return {"Response": response}


model = OllamaLLM(model="qwen2.5:7b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


def process_prompt():
    global last_file_content

    context = readFile(file_context)
    user_input = user_inputAPI

    #calling when theres a file
    if last_file_content: 
        print("got a file")
        result = chain.invoke({"context": context, "question": f"{user_input}: \n {last_file_content}"})

        new_context(file_context,user_input,result)
        last_file_content = ""
        return result

    result = chain.invoke({"context": context, "question": user_input})
    print(f"\nFreddie: {result}")
    new_context(file_context,user_input,result)
    return result


    


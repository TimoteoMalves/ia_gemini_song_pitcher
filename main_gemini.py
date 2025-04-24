import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
import fitz
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from PIL import Image

# uvicorn main_gemini:app --reload

genai.configure(api_key="AIzaSyBuH2_UvQsl5zMHD3kHwGl6Jgr72i8qunY")
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()
file_context = "context.txt"
user_inputAPI = ""
file_location = ""

#using fitz to be able to read pdf
def readFile(file):

    doc = fitz.open(file)
    file_content = ""

    for page in doc:
        text = page.get_text()
        file_content += text

    return file_content

def new_context(file_path,user_input,result):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"\nUser: {user_input}\nFreddie: {result}")

#upload endpoint
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global file_location

    filename = file.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".txt") or filename.endswith(".png")):
        raise HTTPException(status_code=400, detail="Only .png, .pdf and .txt files are allowed.")

    # Save file temporarily
    file_location = f"temp_files/{file.filename}"
    os.makedirs("temp_files", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully."})

# Message class
class Message(BaseModel):
    text: str

#message endpoint
@app.post("/message/")
async def receive_message(msg: Message):
    global user_inputAPI

    user_inputAPI = msg.text

    if file_location and not file_location.endswith(".png"):
        response = generate_response_from_file(user_inputAPI)
        return {"Response": response}
    
    if file_location.endswith(".png"):
        response = generate_response_from_img(user_inputAPI)
        return {"Response": response}
    
    response = generate_response(user_inputAPI)

    return {"Response": response}

# generating whe there is an image
def generate_response_from_img(user_input):
    global file_location

    img = Image.open(file_location)

    context = readFile(file_context) #read context

    template = f"""Answer the question below.

    Your name is Freddie Mercury and you are an artificial intelligence made to change the key of asked songs.
    You do that only if the person sends you a file or the song as a text.
    You will receive the song as a text or image, and have to return it as text too.
    You must always return a simplified version of the given song transposed up to the asked number of key(s).

    Question: {user_input}
    """

    response = model.generate_content([template, img])
    new_context(file_context,user_input,response.text) #writing new context

    file_location = ""
    return response.text

# generating when there is a file
def generate_response_from_file(user_input):
    global file_location
    last_file_content = readFile(file_location)
    context = readFile(file_context) #read context


    template = f'Answer the question below.\n\nHere is the conversation history:\n\n {context}\n\nYour name is Freddie mercury and you are a artifical inteligence made to change the key of asked songs. You do that only if the person sends you a file or the song as a text. You will receive the song as a text, and have to return it as text too. You must always return a simplified version of the given song transposed up to the asked number of key(s).\n\nQuestion: {user_input}\n\n Song: {last_file_content}\n\n Answer:'
    
    response = model.generate_content(template)

    new_context(file_context,user_input,response.text) #writing new context
    file_location = ""

    return response.text

# Generating when there is no file
def generate_response(user_input):
    context = readFile(file_context) #read context

    template = f'Answer the question below.\n\nHere is the conversation history:\n\n {context}\n\nYour name is Freddie mercury and you are a artifical inteligence made to change the key of asked songs. You do that only if the person sends you a file or the song as a text.You will receive the song as a text, and have to return it as text too. You must always return a simplified version of the given song transposed up to the asked number of key(s).\n\nQuestion: {user_input}\nAnswer:'
       
    response = model.generate_content(template) #generating response

    new_context(file_context,user_input,response.text) #writing new context

    return response.text

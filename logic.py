from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnableMap
from prompt_store import template

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from typing import Any, Dict, List
# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

prompt = ChatPromptTemplate.from_template(template)

# Initialize the ChatOpenAI model
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
#.bind(response_format={"type": "json_object"})

# Function to handle user input
# Function to handle user input and invoke the chain

# Request model to handle input data
class UserInput(BaseModel):
    question: str
    chat_history: List[Dict[str, Any]] = []


def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    chain = RunnableMap({
    "chat_history": lambda x: x["chat_history"],
    "question": lambda x: x["question"]
}) | prompt | llm
    #inputs = RunnableMap({
    #"chat_history": lambda x: x["chat_history"],
    #"question": lambda x: x["question"]
#}) 
    #print(inputs.invoke(input={"question": query, "chat_history": chat_history}))
   
    result = chain.invoke(input={"question": query, "chat_history": chat_history})
    return result.content

# API endpoint to process user input
@app.post("/chat/")
async def chat(input_data: UserInput):
    try:
        response = run_llm(query=input_data.question, chat_history=input_data.chat_history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint to check if API is working
@app.get("/")
async def root():
    return {"message": "Welcome to the LangChain-powered FastAPI!"}

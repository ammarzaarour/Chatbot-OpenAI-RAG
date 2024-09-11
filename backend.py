from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema.runnable import RunnableMap

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from pydantic import ValidationError

from typing import Any, Dict, List
# Load environment variables from .env file
load_dotenv()

print("Hello LangChain")

# Define prompt templates for various stages
welcome_template = """
Welcome to Skilled! I'm ALI, your digital sales colleague. I'm here to make your sales journey smoother. Would you like to hear more about what I can do or just dive right in with the onboarding process?
"""

info_templates = """
    When the user start chatting send to him "Welcome to Skilled! I'm ALI, your digital sales colleague. I'm here to make your sales journey smoother. Would you like to hear more about what I can do or just dive right in with the onboarding process?"
    After the user dive right in with the onboarding process start Asking The user questions to get data from the user. The questions are: 
    "job_title": "Could you please specify the job title of the customer you are targeting? For example, are you focusing on roles such as Chief Executive Officer (CEO), Marketing Manager, or IT Director? This will help me tailor our approach to the appropriate decision-makers or influencers in their role.",
    "job_seniority": "To further refine your target customer, could you specify the job seniority level you're aiming for? Please provide one or a range of seniority levels, such as entry-level, mid-level, senior, or executive.",
    "department": "Cool! could you identify the department or departments you want to target? Please provide one or a list of departments relevant to your ideal customer profiles.",
 
    Finally after taking details from user create email for the targeted audience
    
"""

hi ="you are a helpfull assistant"

template = """When the user start chatting send to him "Welcome to Skilled! I'm ALI, your digital sales colleague. I'm here to make your sales journey smoother. Would you like to hear more about what I can do or just dive right in with the onboarding process?"
   
     After the user dive right in with the onboarding process start Asking The user questions to get data from the user. The questions are: 
    "job_title": "Could you please specify the job title of the customer you are targeting? For example, are you focusing on roles such as Chief Executive Officer (CEO), Marketing Manager, or IT Director? This will help me tailor our approach to the appropriate decision-makers or influencers in their role.",
    "job_seniority": "To further refine your target customer, could you specify the job seniority level you're aiming for? Please provide one or a range of seniority levels, such as entry-level, mid-level, senior, or executive.",
    "department": "Cool! could you identify the department or departments you want to target? Please provide one or a list of departments relevant to your ideal customer profiles.",
    
    job_title, job_seniority are mandatory so user should answer them, don't let him proceed without them. while department is secondary and he can proceed to the email generation
    Finally after taking details from user create email for the targeted audience

    Ask according to this chat history, don't ask a question twice if you have a result {chat_history}

    Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# Initialize the ChatOpenAI model
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
#.bind(response_format={"type": "json_object"})

# Function to handle user input
# Function to handle user input and invoke the chain
def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    chain = RunnableMap({
    "chat_history": lambda x: x["chat_history"],
    "question": lambda x: x["question"]
}) | prompt | llm
    inputs = RunnableMap({
    "chat_history": lambda x: x["chat_history"],
    "question": lambda x: x["question"]
}) 
    print(inputs.invoke(input={"question": query, "chat_history": chat_history}))
   
    result = chain.invoke(input={"question": query, "chat_history": chat_history})
    return result.content


    
   
    
    #prompt = PromptTemplate(template=hi)
    #chain = LLMChain(prompt=prompt, llm=llm)
    #response = res = chain.invoke(answer= query)
    #return response

vectorstore = DocArrayInMemorySearch.from_texts(
   [
    "Smartphone ammar Pro has a 6.5-inch OLED display and a dual-camera system.",
    "Organic honey is a natural sweetener harvested from sustainable bee farms.",
    "Wireless earbuds provide noise cancellation and up to 24 hours of battery life.",
    "Ergonomic office chair with lumbar support and adjustable armrests for comfort.",
    "Portable blender for smoothies, shakes, and juices with a rechargeable battery."
],
    embedding=OpenAIEmbeddings()
)
retriever = vectorstore.as_retriever()

print(retriever.invoke("write an email about smartphone ammar"))

template1 = """create email for the targeted audience on the following product:
{product}

Question: {question}
"""
prompt1 = ChatPromptTemplate.from_template(template1)

chain1 = RunnableMap({
    "product": lambda x: retriever.invoke(x["question"]),
    "question": lambda x: x["question"]
}) | prompt1 | llm

result1 = chain1.invoke({"question": "write email about smartphone ammar"})
print(result1.content)
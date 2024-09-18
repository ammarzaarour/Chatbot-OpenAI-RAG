from dotenv import load_dotenv

load_dotenv()
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


from typing import Any, Dict, List

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
docsearch = PineconeVectorStore(index_name="demo", embedding=embeddings)
chat = ChatOpenAI(verbose=True, temperature=0)

rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
stuff_documents_chain = create_stuff_documents_chain(chat, retrieval_qa_chat_prompt)

history_aware_retriever = create_history_aware_retriever(
        llm=chat, retriever=docsearch.as_retriever(), prompt=rephrase_prompt
    )
qa = create_retrieval_chain(
        retriever=history_aware_retriever, combine_docs_chain=stuff_documents_chain
    )

result = qa.invoke(input={"input": "write summary about amm phone 8"})
print(result["context"])
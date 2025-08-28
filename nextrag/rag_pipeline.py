import os
from transformers import pipeline
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
#from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from transformers import AutoTokenizer


VECTOR_STORE_PATH = "nextchats/vectorstore/faiss_index"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_STORE_PATH2 = os.path.join(BASE_DIR, "nextevolutions", "nextchats", "vectorstore", "faiss_index")

# Steps 1 : Loading pdf docs and chunking
def chunking():
    folder_path = "nextchats/knowledge_base"
    documents = []

    # Load documents from the extracted text files
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load()) 

    # Split documents into smaller chunks (500 characters each with 100 characters overlap)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    return docs


# Function defining Embedding model for building vector store
def getEmbedding():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


# Step 2: Creating and saving vector store in the disc
def build_and_save_vectorstore():
    embedding_model = getEmbedding()
    docs = chunking()
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(VECTOR_STORE_PATH)
    print("Saved successfully")



#(---------------- Semantic search -----------------------)
"""
1. Load vectorestore
2. Retrieve context based on user query
3. Use LLM for structured answer
"""
import os
from mistralai import Mistral

api_key = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
model = "mistral-medium-latest"


# Function for loading the vectore store from the disc
def load_vectorstore():
    embedding_model = getEmbedding()
    vectorstore = FAISS.load_local("C:/Users/DieuveilMABIROU/Desktop/AI projects/nextevolutions/nextchats/vectorstore/faiss_index", embedding_model, allow_dangerous_deserialization=True)
    return vectorstore
   
   

# Defining function for mistral LLM to answer the user question
def mistral_response(user_query, retrieved_context):
    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model = model,
        messages = [
                {
                    "role": "system",
                    "content": (
                        "Vous êtes un assistant utile. Utilisez les informations suivantes pour répondre aux questions de l'utilisateur :\n\n"
                        + retrieved_context
                    )
                },
                {"role": "user", "content": user_query}
        ]
    )

    return chat_response.choices[0].message.content


# Defining the function for using the system
def system_usage(query):

    #query = "Une société peut acheter ses propres actions?"

    # Load the vectorstore 
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever()
    # Retrieve the top-1 relevant document
    retrieved_docs = retriever.get_relevant_documents(query)[:1]

    # Building the context by copying doc content
    context = " ".join([doc.page_content for doc in retrieved_docs])
    # Using Mistral for answer the user question
    response = mistral_response(query, context)

    print("Reponse", response)
    return response

#system_usage("Une société peut acheter ses propres actions?")

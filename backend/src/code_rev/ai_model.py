from dotenv import load_dotenv
import os 
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

groq_api_key = os.getenv("GROQ_API_KEY")


llm = ChatGroq(
    groq_api_key = groq_api_key,
    model_name = 'llama3-8b-8192'
)

template = '''
You are an expert in programming languages and a very talented 
Data Structures and Algorithms problem solver. Also, you are a 
great CODE REVIEWER

Analyse the following {language} code provide
1. A short review summary.
2. List all the issues or bugs
3. Provide suggestions for improvements

Code:
{code}

Give the review in the specified format
'''

prompt = PromptTemplate(
        input_variables= ["code", "language"],
        template= template
    )

chain = prompt | llm

def generate_response(code, language):

    response = chain.invoke(
        {
            "code": code,
            "language": language
        }
    )

    return response.content

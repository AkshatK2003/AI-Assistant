import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import webbrowser
from console import *

urls_keys=list(url_mapping.keys())
## loading environment variables and oher variables
load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
embeddings=OpenAIEmbeddings()
MODEL="gpt-4o"
## collection_name=[UY_prod_manual_chunks,UY_prod_manual_pages]
vector_store = Chroma(
    collection_name="UY_prod_manual_chunks",
    embedding_function=embeddings,
    persist_directory="./vectordb",
)
## setting up llm
openai=OpenAI()
system_prompt="you are a assistant whose expertise is the product of my company UdyogYantra.AI console\n"
system_prompt+="\n"
system_prompt+="Don't create wrong responses, If unsure, state that you don’t know. \n"
system_prompt+="Instructions: \n"
system_prompt+="""1.company equals to UdyogYantra.AI
2.Brand List is in the My Brands tab"""
user_prompt="look at the information below retrieved from the manual and try to answer the question given at the end \n"
user_prompt="Information: "


def normalize(query):
    query=query.lower()
    syn_map={
        "company":"UdyogYantra",
        "institution":"UdyogYantra",
        "firm":"UdyogYantra",
        "bussiness":"UdyogYantra",
        "organization":"UdyogYantra"
    }
    for word in syn_map:
        query=query.replace(word,syn_map[word])
    return query

def retrieve(query,n=7):
    results = vector_store.similarity_search(
        query,
        k=n,
    )
    return("\n".join(results[i].page_content for i in range(n)))

def msg_template(query,system_prompt=system_prompt,user_prompt=user_prompt):
    user_prompt+=retrieve(query)
    user_prompt+=f"\n Question: {query}"
    return [
        {"role":"system", "content":system_prompt},
        {"role":"user", "content":user_prompt}
    ]

def response(query,system_prompt=system_prompt,user_prompt=user_prompt):
    stream=openai.chat.completions.create(
        messages=msg_template(query),
        model=MODEL,
        temperature=0.5,
        stream=True
    )
    for chunk in stream:
        if chunk.choices:
            yield chunk.choices[0].delta.content

def extract_link(text,url_map=url_mapping):
    print(text)
    res=openai.chat.completions.create(
        messages=[
            {"role":"system","content":"You are a helpfull assistant. Don't create wrong responses, If unsure, state that you don’t know."},
            {"role":"user","content":f"""
            extract the last tab or section from the text given after the examples using the examples given below and give response :
            use this list to extract sections or tabs
            
            list:{urls_keys}
    
            example 1:Access the "My Food Products > All Products" tab. 
            result:All Products
    
            example 2:Navigate to the "My Brands" tab.
            result:My Brands
    
            example 3:Navigate to the "My Brands" section.
            result:My Brands
    
            example 4:Navigate to the My Outlets > Stores tab.
            result:Stores
    
            example 5:Navigate to the My Food Products > Product Category tab.
            result:Product Category
    
            example 6:Go to "My Food Products > Variants Tab."
            result:Variants
    
            text:{text}
    
            your response:
            """}
        ],
        model=MODEL,
        temperature=0
    )
    # print(url_map[res.choices[0].message.content])
    try:
        return (url_map[res.choices[0].message.content])
    except:
        return None
def open_link(text,url_map=url_mapping):
    link=extract_link(text)
    if (link):
        return link
    else:
        return False
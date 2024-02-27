from dotenv import load_dotenv
import os
import openai
import tiktoken
from supabase import create_client
import requests

load_dotenv()

openai_api_key = os.getenv("OPENAI_KEY", "")
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_anon_key = os.getenv("SUPABASE_SERVICE_KEY", "")

supabase_client = create_client(supabase_url, supabase_anon_key)

openai.api_key = openai_api_key


def fetch_documents(input_query):
    # Generate a one-time embedding for the query
    embedding_response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=input_query,
        encoding_format="float",
    )

    embedding = embedding_response['data'][0]['embedding']

    # Get the relevant documents to our question using the match_documents function
    # 'rpc' calls PostgreSQL functions in Supabase
    response = requests.post(supabase_url + "/rest/v1/rpc/match_documents", json={
        "match_count": 3,
        "match_threshold": 0.7,
        "query_embedding": embedding
    }, headers={
        "apikey": supabase_anon_key
    })

    return response.json()


# Example usage
input_query = "Допомога Україні"
documents = fetch_documents(input_query)
print(documents)

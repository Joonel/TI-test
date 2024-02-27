from dotenv import load_dotenv
import os
from supabase import create_client, Client
from embed_stuff import generate_embedding

load_dotenv()


supabase_url = os.getenv("SUPABASE_URL", "")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")


def update_embedding_for_doc_id(doc_id: int, supabase: Client):
    """Updates the embedding for a document with the given ID."""
    # Отримуємо документ з Supabase
    doc = supabase.table("docs").select(
        "*").eq("id", doc_id).execute().data[0]

    # Отримуємо текст документа
    text = doc["content"]

    # Отримуємо ембедінги
    embedding = generate_embedding(text)

    # Оновлюємо документ
    supabase.table("docs").update(
        {"embedding": embedding}).eq("id", doc_id).execute()


def main(doc_id: int):
    # Ініціалізація клієнта Supabase
    supabase: Client = create_client(supabase_url, supabase_service_key)

    # Оновлюємо ембедінги для документа з заданим ID
    update_embedding_for_doc_id(doc_id, supabase)


if __name__ == "__main__":
    main(33)

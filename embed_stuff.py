from dotenv import load_dotenv
import os
import openai
import tiktoken
from supabase import create_client, Client

load_dotenv()


openai_api_key = os.getenv("OPENAI_KEY", "")
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def split_text(content, token_limit=3000, overlap=300, encoding_name="cl100k_base"):
    parts = []
    current_part = ""
    last_tokenized_part = ""

    for line in content.splitlines(keepends=True):
        # Додаємо лінію до поточної частини
        current_part += line
        tokenized_length = num_tokens_from_string(current_part, encoding_name)

        # Якщо кількість токенів перевищує ліміт
        if tokenized_length > token_limit:
            # Зберігаємо останню частину, яка не перевищувала ліміт
            parts.append(last_tokenized_part)

            # Розпочинаємо нову частину з перекриванням
            current_part = current_part[-overlap:]

        last_tokenized_part = current_part

    # Додаємо останню частину, якщо вона не порожня
    if current_part.strip() != "":
        parts.append(current_part)

    return parts


def generate_embedding(text):
    # Ініціалізація клієнта OpenAI
    openai.api_key = openai_api_key

    response = openai.Embedding.create(
        input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']


def main():

    # Ініціалізація клієнта Supabase
    supabase: Client = create_client(supabase_url, supabase_service_key)

    # Читання файлів із підкаталогу 'data'
    for filename in os.listdir('data'):
        if filename.endswith('.txt'):
            with open(os.path.join('data', filename), 'r', encoding='utf-8') as file:

                # If file hasn't .txt extension then add it
                if not filename.endswith('.txt'):
                    filename += '.txt'

                content = file.read()

                content_tokens_num = num_tokens_from_string(
                    content, "cl100k_base")
                if content_tokens_num > 3000:
                    print(
                        f'File {filename} was skipped, it has {content_tokens_num} tokens.')
                    continue

                # skip extension
                document_name = filename[:-4]

                # Перевірка наявності такого ж документа в базі даних
                existing_document = supabase.table('docs').select(
                    'id').eq('document_name', document_name).execute()
                if len(existing_document.data) > 0:
                    continue

                # Add document name to the beginning of the text
                content = f"Цей текст містить інформацію про {document_name}\n###\n{content}"

                embedding = generate_embedding(content)

                # Створення запису в Supabase
                data = {'document_name': document_name,
                        'content': content, 'embedding': embedding}
                supabase.table('docs').insert(data).execute()

                # Вивід інформації про створений запис
                print(f'Created record for {document_name}')


if __name__ == "__main__":
    main()

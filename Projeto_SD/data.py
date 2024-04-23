from datasets import load_dataset
import requests

# Carregando o dataset da Hugging Face
dataset = load_dataset("eduagarcia/cc_news_pt", split="train")
backend_url = "http://localhost:8000/upload/"

# Função para enviar artigos para o servidor FastAPI
def upload_article(article):
    response = requests.post(backend_url, json=article)
    if response.status_code == 200:
        print(f"Successfully uploaded article: {article['title']}")
    else:
        print(f"Failed to upload article: {article['title']}, Status Code: {response.status_code}, Response: {response.text}")

# Processando cada item no dataset
for item in dataset:
    article = {
        "title": item['title'],
        "text": item['text'],
        "authors": item.get('authors', None),
        "domain": item.get('domain', None),
        "description": item.get('description', None),
        "url": item.get('url', None)
    }
    upload_article(article)

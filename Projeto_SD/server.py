from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uuid

app = FastAPI()
db = {}  # Um dicionário simples para armazenar os artigos

class Article(BaseModel):
    title: str
    text: str
    authors: Optional[str] = None
    domain: Optional[str] = None
    description: Optional[str] = None
    url: Optional[HttpUrl] = None

@app.post("/upload/")
async def upload_article(article: Article):
    article_id = str(uuid.uuid4())
    db[article_id] = article.dict()
    return {"id": article_id, "message": "Article uploaded successfully", "article": article}

@app.delete("/delete/{article_id}")
async def delete_article(article_id: str):
    if article_id in db:
        del db[article_id]
        return {"message": "Article deleted successfully"}
    raise HTTPException(status_code=404, detail="Article not found")

@app.get("/articles/")
async def list_articles():
    return [{"id": article_id, **article_data} for article_id, article_data in db.items()]

@app.get("/search/")
async def search_articles(query: str):
    results = [{"id": article_id, **article_data} for article_id, article_data in db.items() if query.lower() in article_data['text'].lower()]
    total = len(results)
    return {"results": results[:10], "total": total}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

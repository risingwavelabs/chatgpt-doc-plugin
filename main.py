import json
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from pydantic import BaseModel

app = FastAPI(
    title="RisingWave Doc Plugin API",
    description="A plugin for answering questions based on natural language queries, related documents, metadata",
    version="1.0.0",
    servers=[{"url": "https://localhost:8080.com"}],)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


search_index = FAISS.load_local("search_index", OpenAIEmbeddings())




class QueryResponse(BaseModel):
   result: List[Document]

class QueryRequest(BaseModel):
   query: str

@app.post("/query", response_model=QueryResponse, description="Accept a questions about risingwave, fetch most related contents from docs")
async def query(request: QueryRequest):
    try:
      docs = search_index.similarity_search(request.query, k=5)
      return QueryResponse(result = docs)
    except Exception as e:
      raise HTTPException(status_code=500, detail="Internal Service Error")

if __name__ == "__main__":
   with open('.well-known/openapi.json', 'w') as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    ), f, indent = 4)
   uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
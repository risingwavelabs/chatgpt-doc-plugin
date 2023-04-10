import os
from typing import List

from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

domain = "risingwave.dev"

def create_docs(domain: str) -> List[Document]:
    docs = []
    for file in os.listdir("text/" + domain + "/"):
        with open("text/" + domain + "/" + file, "r", encoding="UTF-8") as f:
            doc = Document(page_content=f.read(), metadata={
                           "source": "https://" + file.replace(".txt", "").replace("_", "/")})
            docs.append(doc)
    return docs


docs = create_docs(domain)

doc_chunks = []
splitter = CharacterTextSplitter(
    separator=" ", chunk_size=1024, chunk_overlap=0)
for source in docs:
    for chunk in splitter.split_text(source.page_content):
        doc_chunks.append(
            Document(page_content=chunk, metadata=source.metadata))

search_index = FAISS.from_documents(doc_chunks, OpenAIEmbeddings())

# persistent search index
search_index.save_local("search_index")

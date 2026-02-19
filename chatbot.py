from ollama import Client
import json
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

#CONFIGURATIOINS
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen2.5:3b"
COLLECTION_NAME = "articles_demo"

#CLIENTS 
chroma_client = chromadb.PersistentClient()
ollama_client = Client(host="http://localhost:11434")

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)

#RESUME COUNTER
counter = 0
if os.path.exists("counter.txt"):
    with open("counter.txt", "r") as f:
        counter = int(f.read())

#TEXT SPLITTER
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=50,
    separators=["\n\n", "\n", "."]
)

print("Reading articles.jsonl and generating embeddings...")

#INGEST DATA 
with open("articles.jsonl", "r", encoding="utf-8") as f:
    for article_index, line in enumerate(f):

        if article_index < counter:
            print(f"Skipping article {article_index} (already processed)")
            continue

        article = json.loads(line)
        title = article.get("title", "")
        content = article.get("content", "")

        chunks = [
            c.strip()
            for c in splitter.split_text(content)
            if len(c.strip()) > 30
        ]

        for chunk_index, chunk in enumerate(chunks):
            embedding = ollama_client.embed(
                model=EMBED_MODEL,
                input=f"search_document: {chunk}"
            )["embeddings"][0]

            collection.add(
                ids=[f"article_{article_index}_chunk_{chunk_index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "title": title,
                    "article_id": article_index,
                    "chunk_id": chunk_index
                }]
            )

        # mark article as processed
        with open("counter.txt", "w") as f_out:
            f_out.write(str(article_index + 1))

print("✅ Database built successfully!")
print("📦 Total chunks:", collection.count())

#CHATBOT 
SYSTEM_PROMPT = """You are a helpful assistant.
Answer ONLY using the provided context.
If the context does not contain enough information, say "I don't know."
Keep answers concise and factual.
"""

def ask_chatbot(question, top_k=3):
    # Embed query
    query_embed = ollama_client.embed(
        model=EMBED_MODEL,
        input=f"query: {question}"
    )["embeddings"][0]

    # Retrieve relevant chunks
    results = collection.query(
        query_embeddings=[query_embed],
        n_results=top_k,
    )

    retrieved_docs = results["documents"][0]
    context = "\n\n".join(retrieved_docs)
    #print the most relevant chunk 
    print("\n Most relevant chunk:")
    print(results["documents"][0][0])
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer:
"""
       #  Generate answer
    response = ollama_client.generate(
        model=CHAT_MODEL,
        prompt=prompt,
        options={"temperature": 0.1}
    )

    return response["response"].strip()

#INTERACTIVE LOOP
print("\n Article Chatbot Ready!")
print("Type your question or type 'exit' to quit\n")

while True:
    user_query = input("You: ")

    if user_query.lower() in ["exit", "quit"]:
        print(" Goodbye!")
        break

    answer = ask_chatbot(user_query)
    print("\nBot Answer:", answer, "\n")
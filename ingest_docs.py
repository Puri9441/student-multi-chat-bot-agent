import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "student-rag-index")

pc = Pinecone(api_key=api_key)

# Re-create Index if needed
existing_indexes = [idx.name for idx in pc.list_indexes()]
if index_name not in existing_indexes:
    print(f"Creating Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# 1. Load files from docs/ folder using exact TextLoader
docs_path = "docs"
print("Loading all files from docs directory...")

documents = []
for file in os.listdir(docs_path):
    if file.endswith(".txt"):
        file_path = os.path.join(docs_path, file)
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        documents.extend(docs)
        print(f"Loaded: {file}")

print(f"Total files successfully loaded: {len(documents)}")

# 2. Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
chunks = text_splitter.split_documents(documents)
print(f"Total chunks created across all files: {len(chunks)}")

# 3. Generate embeddings
embeddings_model = OllamaEmbeddings(model="nomic-embed-text")

vectors = []
print("Generating vector embeddings...")

for i, chunk in enumerate(chunks):
    text_content = chunk.page_content.strip()
    if text_content:
        source_file = os.path.basename(chunk.metadata.get("source", f"doc_{i}"))
        v_emb = embeddings_model.embed_query(text_content)
        
        # Unique vector ID per chunk and source file
        vectors.append({
            "id": f"{source_file}_chunk_{i}",
            "values": v_emb,
            "metadata": {
                "text": text_content,
                "source": source_file
            }
        })

# 4. Upsert all generated vectors
if vectors:
    print(f"Upserting {len(vectors)} vectors into Pinecone...")
    index.upsert(vectors=vectors)
    print("Upsert completed successfully!")

# 5. Check index status
stats = index.describe_index_stats()
print("Pinecone Index Live Stats:", stats)